"""Sons de scène typiques, construits à partir des voix internes du CK61.

Chaque preset décrit le Live Set Sound complet (3 Parts A/B/C) : toute Part non
listée est coupée et les effets non mentionnés sont désactivés, pour que le
résultat ne dépende pas du Live Set affiché avant l'envoi.
"""

from . import sysex as sx
from .voices import voice_number

PART_LETTERS = "ABC"

PRESETS = {
    "grand": {
        "name": "Concert Grand",
        "description": "Piano à queue CFX stéréo, réverbe de salle.",
        "reverb": ("Hall", 30),
        "parts": [{"voice": "CFX Stereo"}],
    },
    "piano-strings": {
        "name": "Piano Strings",
        "description": "Piano + nappe de cordes à attaque lente (ballade, pop).",
        "reverb": ("Hall", 38),
        "parts": [
            {"voice": "CFX Stereo", "volume": 112},
            {"voice": "Warm Strings", "volume": 72, "attack": 80, "release": 80},
        ],
    },
    "rhodes": {
        "name": "Suitcase Rhodes",
        "description": "Rhodes 73 avec auto-pan stéréo et léger overdrive.",
        "reverb": ("Room", 25),
        "parts": [{
            "voice": "73Rd Studio",
            "drive": ("O.Drive", 30),
            "effects": [("Auto Pan", 70, 60)],
        }],
    },
    "wurli": {
        "name": "Wurli Tremolo",
        "description": "Wurlitzer chaud avec trémolo (soul, Supertramp).",
        "reverb": ("Room", 22),
        "parts": [{
            "voice": "Wr Warm",
            "drive": ("O.Drive", 40),
            "effects": [("Tremolo", 64, 70)],
        }],
    },
    "dx-ballad": {
        "name": "DX Ballad",
        "description": "E.Piano DX7 années 80 chorusé + pad discret.",
        "reverb": ("Hall", 40),
        "parts": [
            {"voice": "DX Legend", "volume": 112, "effects": [("Symphonic", 60, 50)]},
            {"voice": "Soft Pad 1", "volume": 55},
        ],
    },
    "jazz-organ": {
        "name": "Jazz Organ",
        "description": "Orgue à roues phoniques 888000000, percu 3rd rapide, chorus C3.",
        "reverb": ("Room", 15),
        "parts": [{
            "voice": "H",
            "drawbars": "888000000",
            "percussion": ("3rd", "Fast"),
            "vibrato": "C3",
        }],
    },
    "rock-organ": {
        "name": "Rock Organ",
        "description": "Orgue saturé 888000000 façon Deep Purple.",
        "reverb": ("Room", 18),
        "parts": [{
            "voice": "H",
            "drawbars": "888000000",
            "vibrato": "C3",
            "drive": ("O.Drive", 95),
        }],
    },
    "gospel-organ": {
        "name": "Gospel Organ",
        "description": "Orgue tous tirants ouverts 888888888.",
        "reverb": ("Room", 20),
        "parts": [{"voice": "H", "drawbars": "888888888", "vibrato": "C3"}],
    },
    "bass-piano": {
        "name": "Bass / Piano",
        "description": "Basse au doigt main gauche, piano main droite (split C3).",
        "split": "A/BC",
        "split_point": "C3",
        "reverb": ("Hall", 25),
        "parts": [
            {"voice": "Finger Bass 1"},
            {"voice": "CFX Stereo"},
        ],
    },
    "brass": {
        "name": "Brass Section",
        "description": "Section cuivres pour les riffs funk/soul.",
        "reverb": ("Room", 30),
        "parts": [{"voice": "BrassSection1"}],
    },
    "jump": {
        "name": "Jump Brass",
        "description": "Le synth brass d'« Jump » (Van Halen).",
        "reverb": ("Hall", 25),
        "parts": [{"voice": "Jump Brass"}],
    },
    "80s-pad": {
        "name": "80s Pad",
        "description": "Cordes JP + pad 80 chorusés, grosse réverbe.",
        "reverb": ("Hall", 45),
        "parts": [
            {"voice": "JP Strings", "volume": 100, "effects": [("SPX Chorus", 64, 40)]},
            {"voice": "Pad 80", "volume": 75},
        ],
    },
    "strings-choir": {
        "name": "Strings Choir",
        "description": "Section de cordes + chœur « aah » (finales, ballades).",
        "reverb": ("Hall", 50),
        "parts": [
            {"voice": "Section Str 1", "volume": 105},
            {"voice": "Choir Aah", "volume": 70, "attack": 75},
        ],
    },
    "clav": {
        "name": "Funky Clav",
        "description": "Clavinet avec touch wah (Superstition).",
        "reverb": ("Room", 12),
        "parts": [{"voice": "Clavi B", "effects": [("Touch Wah", 80, 64)]}],
    },
    "lead": {
        "name": "Mono Lead",
        "description": "Lead analogique mono avec portamento et delay.",
        "reverb": ("Hall", 25),
        "delay": ("Analog", 40, 64),
        "parts": [{
            "voice": "Analog Lead 1",
            "mono": "Fingered Portamento",
            "portamento": 30,
        }],
    },
}

MONO_TYPES = ["Normal", "Fingered Portamento", "Full-time Portamento"]
TONEWHEEL_ORGANS = range(voice_number("H"), voice_number("Y") + 1)


def build_part(p, settings, device=sx.DEVICE_ALL):
    """Messages pour une Part active."""
    number = settings["voice"]
    if isinstance(number, str):
        number = voice_number(number)

    messages = [sx.part(p, sx.PART_SWITCH, 1, device)]
    messages += sx.select_voice(p, number, device)
    messages += [
        sx.part(p, sx.PART_VOLUME, settings.get("volume", 127), device),
        sx.part(p, sx.NOTE_SHIFT, 0x40 + settings.get("shift", 0), device),
        sx.part(p, sx.FILTER_CUTOFF, settings.get("cutoff", 64), device),
        sx.part(p, sx.FILTER_RESONANCE, settings.get("resonance", 64), device),
        sx.part(p, sx.EG_ATTACK, settings.get("attack", 64), device),
        sx.part(p, sx.EG_RELEASE, settings.get("release", 64), device),
    ]

    mono = settings.get("mono")
    messages.append(sx.part(p, sx.MONO_POLY, 0 if mono else 1, device))
    if mono:
        messages.append(sx.part(p, sx.MONO_TYPE, MONO_TYPES.index(mono), device))
        messages.append(sx.part(p, sx.PORTAMENTO_TIME, settings.get("portamento", 20), device))

    if number in TONEWHEEL_ORGANS:
        drawbars = settings.get("drawbars", "888000000")
        values = [sx.drawbar_value(int(d)) for d in drawbars]
        messages += [sx.part(p, sx.DRAWBARS + i, v, device) for i, v in enumerate(values)]
        percussion = settings.get("percussion")
        if percussion:
            kind, decay = percussion
            messages += [
                sx.part(p, sx.PERCUSSION_TYPE, ["3rd", "2nd"].index(kind), device),
                sx.part(p, sx.PERCUSSION_DECAY, ["Slow", "Fast"].index(decay), device),
            ]
        messages.append(sx.part(p, sx.PERCUSSION_SWITCH, 1 if percussion else 0, device))
        vibrato = settings.get("vibrato")
        if vibrato:
            messages.append(sx.part(p, sx.VIBRATO_TYPE, sx.VIBRATO_TYPES.index(vibrato), device))
        messages.append(sx.part(p, sx.VIBRATO_SWITCH, 1 if vibrato else 0, device))

    drive = settings.get("drive")
    if drive:
        kind, depth = drive
        messages += [
            sx.part(p, sx.DRIVE_TYPE, sx.DRIVE_TYPES.index(kind), device),
            sx.part(p, sx.DRIVE_DEPTH, depth, device),
        ]
    messages.append(sx.part(p, sx.DRIVE_SWITCH, 1 if drive else 0, device))

    effects = settings.get("effects", [])
    for slot in (1, 2):
        if slot <= len(effects):
            messages += sx.effect(p, slot, *effects[slot - 1], device=device)
        else:
            switch = sx.EFFECT1_SWITCH if slot == 1 else sx.EFFECT2_SWITCH
            messages.append(sx.part(p, switch, 0, device))
    return messages


def build(preset, device=sx.DEVICE_ALL):
    """Liste des Parameter Changes (sans F0/F7) qui reproduisent un preset."""
    name = preset["name"][:15].ljust(15)
    messages = [sx.common(sx.NAME + i, ord(c), device) for i, c in enumerate(name)]

    messages.append(sx.common(
        sx.LAYER_SPLIT_MODE, sx.LAYER_SPLIT_MODES.index(preset.get("split", "ABC")), device))
    if "split_point" in preset:
        messages.append(sx.common(sx.SPLIT_POINT, sx.note_number(preset["split_point"]), device))
    if "split_points" in preset:
        ab, bc = preset["split_points"]
        messages.append(sx.common(sx.SPLIT_POINT_AB, sx.note_number(ab), device))
        messages.append(sx.common(sx.SPLIT_POINT_BC, sx.note_number(bc), device))

    reverb = preset.get("reverb")
    if reverb:
        kind, depth = reverb
        messages += [
            sx.common(sx.REVERB_TYPE, sx.REVERB_TYPES.index(kind), device),
            sx.common(sx.REVERB_DEPTH, depth, device),
        ]
    messages.append(sx.common(sx.REVERB_SWITCH, 1 if reverb else 0, device))

    delay = preset.get("delay")
    if delay:
        kind, depth, time = delay
        messages += [
            sx.common(sx.DELAY_TYPE, sx.DELAY_TYPES.index(kind), device),
            sx.common(sx.DELAY_DEPTH, depth, device),
            sx.common(sx.DELAY_TIME, time, device),
        ]
    messages.append(sx.common(sx.DELAY_SWITCH, 1 if delay else 0, device))
    messages.append(sx.common(sx.ROTARY_FAST, 0, device))

    parts = preset["parts"]
    for p in range(3):
        if p < len(parts):
            messages += build_part(p, parts[p], device)
        else:
            messages.append(sx.part(p, sx.PART_SWITCH, 0, device))
    return messages
