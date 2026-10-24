"""Lecture, sauvegarde et écriture des Live Sets utilisateur par Bulk Dump (Data List p.57-58).

Un Live Set Sound se transfère comme une suite de blocs encadrés par un Bulk Header
(0E pp 0n) et un Bulk Footer (0F pp 0n) ; pp = page 0-19, n = slot 0-7, et
pp = 7F, n = 0 désigne le Live Set en cours d'édition (Current Sound Buffer).
"""

import time

from . import sysex as sx

PAGES = 20
SLOTS = 8
HEADER = 0x0E
FOOTER = 0x0F
CURRENT_BUFFER = (0x7F, 0x00)
EMPTY_NAME = "Init Sound"


def store_to_flash(device=sx.DEVICE_ALL):
    """Les Live Sets reçus par Bulk Dump restent en RAM : ce message les inscrit en flash.

    Le manuel ne cite que l'adresse 0D 00 00 ; comme le Bulk Header/Footer, c'est un
    bloc Bulk Dump sans données (un Parameter Change à cette adresse n'a aucun effet).
    """
    return bulk_message((0x0D, 0x00, 0x00), [], device)


def dump_request(page_slot, device=sx.DEVICE_ALL):
    return [sx.YAMAHA_ID, 0x20 | device, *sx.GROUP_ID, sx.MODEL_ID, HEADER, *page_slot]


def bulk_address(message):
    return tuple(message[7:10])


def bulk_message(address, data, device=sx.DEVICE_ALL):
    # Contrairement à ce que laisse entendre le manuel, le Byte Count et le checksum
    # couvrent Model ID + adresse + données (constaté sur les dumps du CK).
    size = len(data) + 4
    count = [size >> 7, size & 0x7F]
    checksum = -sum([sx.MODEL_ID, *address, *data]) & 0x7F
    return [sx.YAMAHA_ID, device, *sx.GROUP_ID, *count, sx.MODEL_ID, *address, *data, checksum]


def is_bulk(message):
    return (len(message) >= 11 and message[0] == sx.YAMAHA_ID and message[1] & 0xF0 == 0
            and tuple(message[2:4]) == sx.GROUP_ID and message[6] == sx.MODEL_ID)


def live_set_name(blocks):
    for block in blocks:
        if bulk_address(block) == (sx.COMMON, 0x00, 0x00):
            # Le CK complète les noms courts avec des octets nuls
            return bytes(block[10:25]).decode("ascii", "replace").rstrip("\x00 ")
    return None


def retarget(blocks, page_slot):
    """Réadresse un Live Set (header et footer) vers un autre emplacement."""
    result = []
    for block in blocks:
        high = bulk_address(block)[0]
        if high in (HEADER, FOOTER):
            result.append(bulk_message((high, *page_slot), [], block[1]))
        else:
            result.append(list(block))
    return result


def slot_label(page_slot):
    page, slot = page_slot
    return f"{page + 1}-{slot + 1}"


def all_slots():
    return [(page, slot) for page in range(PAGES) for slot in range(SLOTS)]


class Connection:
    def __init__(self, port_name=None, device=sx.DEVICE_ALL, interval=10, timeout=3.0):
        import mido

        self.mido = mido
        self.device = device
        self.interval = interval / 1000
        self.timeout = timeout
        out_name = self._find(port_name, mido.get_output_names())
        in_name = self._find(port_name, mido.get_input_names())
        print(f"→ Ports MIDI : {out_name} / {in_name}")
        self.output = mido.open_output(out_name)
        self.input = mido.open_input(in_name)

    @staticmethod
    def _find(name, names):
        if name in names:
            return name
        matches = [n for n in names if "ck" in n.lower()]
        if not matches:
            raise SystemExit("CK61 introuvable. Ports disponibles :\n  " + "\n  ".join(names or ["(aucun)"]))
        return matches[0]

    def close(self):
        self.output.close()
        self.input.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def send(self, payloads):
        for payload in payloads:
            self.output.send(self.mido.Message("sysex", data=payload))
            time.sleep(self.interval)

    def read_live_set(self, page_slot):
        """Demande le Live Set et renvoie ses blocs, du header au footer inclus."""
        for _ in self.input.iter_pending():
            pass
        self.send([dump_request(page_slot, self.device)])
        blocks = []
        deadline = time.monotonic() + self.timeout
        while time.monotonic() < deadline:
            message = self.input.poll()
            if message is None:
                time.sleep(0.002)
                continue
            if message.type != "sysex" or not is_bulk(message.data):
                continue
            data = list(message.data)
            high = bulk_address(data)[0]
            if high == HEADER:
                blocks = []
            blocks.append(data)
            deadline = time.monotonic() + self.timeout
            if high == FOOTER:
                return blocks
        raise SystemExit(
            f"Pas de réponse du CK pour le Live Set {slot_label(page_slot)}. Vérifier "
            "[UTILITY] → MIDI : USB In/Out = On et Device Number = All.")
