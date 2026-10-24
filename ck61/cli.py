"""Ligne de commande : python -m ck61 <commande> ..."""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

from . import library as lib
from . import sysex as sx
from .presets import PART_LETTERS, PRESETS, build
from .voices import CATEGORIES, VOICES, voice_number


def hex_string(message):
    return " ".join(f"{b:02X}" for b in message)


def as_syx(payload):
    return bytes([0xF0, *payload, 0xF7])


def open_port(name):
    import mido

    names = mido.get_output_names()
    if name is None:
        matches = [n for n in names if "ck" in n.lower()]
        if not matches:
            sys.exit("CK61 introuvable. Ports disponibles :\n  " + "\n  ".join(names or ["(aucun)"]))
        name = matches[0]
    print(f"→ Port MIDI : {name}")
    return mido.open_output(name)


def send_sysex(args, payloads):
    if args.dry_run:
        for payload in payloads:
            print(hex_string(as_syx(payload)))
        return
    import mido

    with open_port(args.port) as port:
        for payload in payloads:
            port.send(mido.Message("sysex", data=payload))
            time.sleep(args.interval / 1000)
    print(f"{len(payloads)} messages envoyés.")


def cmd_ports(args):
    import mido

    for name in mido.get_output_names():
        print(name)


def cmd_list(args):
    for key, preset in PRESETS.items():
        voices = " + ".join(p["voice"] for p in preset["parts"])
        print(f"{key:15} {preset['name']:16} {voices}")
        print(f"{'':15} {preset['description']}")


def cmd_voices(args):
    query = (args.query or "").lower()
    starts = [start for _, start in CATEGORIES]
    for number, name in enumerate(VOICES):
        if number in starts:
            category = CATEGORIES[starts.index(number)][0]
            if not query:
                print(f"\n[{category}]")
        if query in name.lower():
            print(f"{number:4}  {name}")


def cmd_send(args):
    if args.preset not in PRESETS:
        sys.exit(f"Preset inconnu : {args.preset}. Voir : python -m ck61 list")
    preset = PRESETS[args.preset]
    print(f"{preset['name']} — {preset['description']}")
    send_sysex(args, build(preset, args.device))


def cmd_voice(args):
    p = PART_LETTERS.index(args.part.upper())
    number = int(args.voice) if args.voice.isdigit() else voice_number(args.voice)
    print(f"Part {args.part.upper()} ← {VOICES[number]} ({number})")
    payloads = [sx.part(p, sx.PART_SWITCH, 1, args.device)]
    payloads += sx.select_voice(p, number, args.device)
    send_sysex(args, payloads)


def cmd_recall(args):
    messages = sx.live_set_select(args.page, args.slot, args.channel - 1)
    if args.dry_run:
        for message in messages:
            print(hex_string(message))
        return
    import mido

    with open_port(args.port) as port:
        for message in messages:
            port.send(mido.Message.from_bytes(message))
    print(f"Live Set page {args.page}, slot {args.slot} rappelé.")


def read_all(ck):
    """Lit les 160 Live Sets : {(page, slot): blocs}."""
    live_sets = {}
    for page_slot in lib.all_slots():
        live_sets[page_slot] = ck.read_live_set(page_slot)
        print(f"\rLecture {lib.slot_label(page_slot):>5}", end="", flush=True)
    print()
    return live_sets


def write_backup(live_sets, folder):
    path = Path(folder) / f"ck61-{datetime.now():%Y%m%d-%H%M%S}.syx"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"".join(as_syx(b) for blocks in live_sets.values() for b in blocks))
    print(f"Sauvegarde des 160 Live Sets : {path}")
    return path


def print_slots(live_sets):
    for page in range(lib.PAGES):
        names = [lib.live_set_name(live_sets[(page, slot)]) or "?" for slot in range(lib.SLOTS)]
        print(f"Page {page + 1:2} │ " + " │ ".join(f"{n:15}" for n in names))


def confirm(question, assume_yes):
    if assume_yes:
        return True
    return input(f"{question} [o/N] ").strip().lower() in ("o", "oui", "y", "yes")


def cmd_slots(args):
    with lib.Connection(args.port, args.device, args.interval) as ck:
        print_slots(read_all(ck))


def cmd_backup(args):
    with lib.Connection(args.port, args.device, args.interval) as ck:
        write_backup(read_all(ck), args.folder)


def parse_slot(text):
    page, slot = (int(x) for x in text.split("-"))
    if not (1 <= page <= lib.PAGES and 1 <= slot <= lib.SLOTS):
        raise argparse.ArgumentTypeError("format PAGE-SLOT, ex. 4-1")
    return page - 1, slot - 1


def cmd_store(args):
    keys = args.presets or list(PRESETS)
    unknown = [k for k in keys if k not in PRESETS]
    if unknown:
        sys.exit(f"Presets inconnus : {', '.join(unknown)}")

    with lib.Connection(args.port, args.device, args.interval) as ck:
        live_sets = read_all(ck)
        write_backup(live_sets, args.backup_folder)

        slots = lib.all_slots()
        if args.start:
            first = slots.index(args.start)
        else:
            used = [i for i, s in enumerate(slots) if lib.live_set_name(live_sets[s]) != lib.EMPTY_NAME]
            first = used[-1] + 1 if used else 0
        targets = slots[first:first + len(keys)]
        if len(targets) < len(keys):
            sys.exit(f"Pas assez de place : {len(targets)} slot(s) après {lib.slot_label(slots[first - 1])}.")

        print("\nPlan d'écriture :")
        for key, target in zip(keys, targets):
            current = lib.live_set_name(live_sets[target])
            warning = "" if current == lib.EMPTY_NAME else "   ⚠ écrase un Live Set existant"
            print(f"  {lib.slot_label(target):>5}  {current:15} → {PRESETS[key]['name']}{warning}")
        if not confirm("Écrire ces Live Sets ?", args.yes):
            sys.exit("Annulé, rien n'a été écrit.")

        for key, target in zip(keys, targets):
            preset = PRESETS[key]
            ck.send(build(preset, args.device))
            time.sleep(0.2)
            buffer = ck.read_live_set(lib.CURRENT_BUFFER)
            ck.send(lib.retarget(buffer, target))
            time.sleep(0.2)
            stored = lib.live_set_name(ck.read_live_set(target))
            status = "ok" if stored == preset["name"][:15].rstrip() else f"ÉCHEC (lu : {stored!r})"
            print(f"  {lib.slot_label(target):>5}  {preset['name']:16} {status}")
        ck.send([lib.store_to_flash(args.device)])
        time.sleep(2)
        print("Live Sets inscrits en mémoire flash.")
    print("\nEn cas de souci : python -m ck61 restore <fichier de sauvegarde>")


def cmd_restore(args):
    data = Path(args.file).read_bytes()
    payloads = [list(chunk[1:]) for chunk in data.split(b"\xf7") if chunk.startswith(b"\xf0")]
    print(f"{args.file} : {len(payloads)} blocs SysEx.")
    if not confirm("Réécrire les Live Sets du CK avec cette sauvegarde ?", args.yes):
        sys.exit("Annulé.")
    with lib.Connection(args.port, args.device, args.interval) as ck:
        ck.send(payloads)
        ck.send([lib.store_to_flash(args.device)])
        time.sleep(2)
    print("Restauration envoyée et inscrite en mémoire flash.")


def cmd_export(args):
    folder = Path(args.folder)
    folder.mkdir(parents=True, exist_ok=True)
    for key, preset in PRESETS.items():
        path = folder / f"{key}.syx"
        path.write_bytes(b"".join(as_syx(p) for p in build(preset, args.device)))
        print(path)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="ck61", description="Sons de scène pour Yamaha CK61 via MIDI.")
    sub = parser.add_subparsers(dest="command", required=True)

    def midi_options(p):
        p.add_argument("--port", help="nom du port MIDI (par défaut : le premier contenant « CK »)")
        p.add_argument("--dry-run", action="store_true", help="affiche les messages en hexadécimal sans les envoyer")

    def sysex_options(p):
        midi_options(p)
        p.add_argument("--device", type=int, default=0, help="Device Number SysEx - 1 (0 = réglage « All »)")
        p.add_argument("--interval", type=float, default=10, help="pause entre messages en ms (défaut 10)")

    sub.add_parser("ports", help="liste les ports MIDI").set_defaults(func=cmd_ports)
    sub.add_parser("list", help="liste les presets").set_defaults(func=cmd_list)

    p = sub.add_parser("voices", help="liste les voix internes")
    p.add_argument("query", nargs="?", help="filtre sur le nom")
    p.set_defaults(func=cmd_voices)

    p = sub.add_parser("send", help="envoie un preset dans le Live Set en cours")
    p.add_argument("preset")
    sysex_options(p)
    p.set_defaults(func=cmd_send)

    p = sub.add_parser("voice", help="change la voix d'une Part (A, B ou C)")
    p.add_argument("part", choices=list("ABCabc"))
    p.add_argument("voice", help="nom ou numéro (0-362)")
    sysex_options(p)
    p.set_defaults(func=cmd_voice)

    p = sub.add_parser("recall", help="rappelle un Live Set enregistré (Bank Select + Program Change)")
    p.add_argument("page", type=int, choices=range(1, 21), metavar="PAGE (1-20)")
    p.add_argument("slot", type=int, choices=range(1, 9), metavar="SLOT (1-8)")
    p.add_argument("--channel", type=int, default=1, help="canal MIDI de réception du CK (défaut 1)")
    midi_options(p)
    p.set_defaults(func=cmd_recall)

    def library_options(p):
        p.add_argument("--port", help="nom du port MIDI (par défaut : le premier contenant « CK »)")
        p.add_argument("--device", type=int, default=0, help="Device Number SysEx - 1 (0 = réglage « All »)")
        p.add_argument("--interval", type=float, default=10, help="pause entre messages en ms (défaut 10)")

    p = sub.add_parser("slots", help="affiche les noms des 160 Live Sets")
    library_options(p)
    p.set_defaults(func=cmd_slots)

    p = sub.add_parser("backup", help="sauvegarde les 160 Live Sets dans un .syx")
    p.add_argument("folder", nargs="?", default="backups")
    library_options(p)
    p.set_defaults(func=cmd_backup)

    p = sub.add_parser("store", help="enregistre les presets à la suite des Live Sets existants")
    p.add_argument("presets", nargs="*", help="presets à enregistrer (défaut : tous)")
    p.add_argument("--start", type=parse_slot, help="premier slot PAGE-SLOT (défaut : après le dernier utilisé)")
    p.add_argument("--yes", action="store_true", help="ne pas demander de confirmation")
    p.add_argument("--backup-folder", default="backups")
    library_options(p)
    p.set_defaults(func=cmd_store)

    p = sub.add_parser("restore", help="renvoie une sauvegarde .syx au CK")
    p.add_argument("file")
    p.add_argument("--yes", action="store_true")
    library_options(p)
    p.set_defaults(func=cmd_restore)

    p = sub.add_parser("export", help="exporte chaque preset en fichier .syx")
    p.add_argument("folder", nargs="?", default="syx")
    p.add_argument("--device", type=int, default=0)
    p.set_defaults(func=cmd_export)

    args = parser.parse_args(argv)
    args.func(args)
