"""Construction des messages MIDI pour le CK61 (Owner's Manual, Data List p.57-63).

Les Parameter Changes modifient le Live Set Sound en cours d'édition : rien n'est
écrit en mémoire tant que l'on n'appuie pas sur [STORE] sur le clavier.
"""

from .voices import category_of

# F0 43 1n 7F 1C 0B <adresse haute, moyenne, basse> <données...> F7
YAMAHA_ID = 0x43
GROUP_ID = (0x7F, 0x1C)
MODEL_ID = 0x0B
DEVICE_ALL = 0  # Réglage d'usine du CK : Device Number = All

# Live Set Common (46 00 xx)
COMMON = 0x46
NAME = 0x00  # 15 caractères ASCII
LAYER_SPLIT_MODE = 0x16
SPLIT_POINT = 0x18
SPLIT_POINT_AB = 0x19
SPLIT_POINT_BC = 0x1A
DELAY_SWITCH = 0x27
DELAY_TYPE = 0x28
DELAY_DEPTH = 0x29
DELAY_TIME = 0x2A
REVERB_SWITCH = 0x2C
REVERB_TYPE = 0x2D
REVERB_DEPTH = 0x2E
ROTARY_FAST = 0x30

# Live Set Part (50 0p xx), p = 0 (A), 1 (B), 2 (C)
PART = 0x50
CURRENT_CATEGORY = 0x00
NOTE_SHIFT = 0x16
PART_VOLUME = 0x17
PART_SWITCH = 0x19
MONO_POLY = 0x20
MONO_TYPE = 0x21
PORTAMENTO_TIME = 0x23
DRAWBARS = 0x40  # 9 tirettes : 40 (16') à 48 (1')
PERCUSSION_SWITCH = 0x49
PERCUSSION_TYPE = 0x4A
PERCUSSION_DECAY = 0x4B
VIBRATO_SWITCH = 0x4E
VIBRATO_TYPE = 0x4F
FILTER_CUTOFF = 0x51
FILTER_RESONANCE = 0x52
EG_ATTACK = 0x54
EG_RELEASE = 0x55
DRIVE_SWITCH = 0x56
DRIVE_TYPE = 0x57
DRIVE_DEPTH = 0x58
EFFECT1_SWITCH = 0x59
EFFECT2_SWITCH = 0x5D  # Type, Depth, Rate suivent le switch (+1, +2, +3)

LAYER_SPLIT_MODES = ["ABC", "A/BC", "AB/C", "A/B/C"]
REVERB_TYPES = ["Hall", "Room", "Plate"]
DELAY_TYPES = ["Digital", "Analog", "Cross", "Tempo"]
DRIVE_TYPES = ["O.Drive", "Dist", "Rotary A", "Rotary B", "Comp"]
VIBRATO_TYPES = ["V1", "C1", "V2", "C2", "V3", "C3"]
EFFECT_TYPES = [
    "G Chorus", "SPX Chorus", "Symphonic", "816 Chorus", "VCM Flanger",
    "Cross FB Flanger", "VCM Stereo Phaser", "Small Phaser", "Max90",
    "Dual Phaser", "Tremolo", "Auto Pan", "Simple Rotary", "British Combo",
    "British Lead", "Small Stereo", "Compressor", "Tone Control",
    "1 BandEQ Narrow", "1 BandEQ Wide", "Auto Wah", "Touch Wah", "Pedal Wah",
    "Cross Delay", "Digital Delay", "Analog Delay", "Room Reverb",
    "Hall Reverb", "Reverse Reverb", "Ring Modulator", "Slicer", "LP Filter",
    "HP Filter", "Lo-Fi", "Damper Resonance", "Harmonic Enhancer",
]

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def parameter_change(address, data, device=DEVICE_ALL):
    """Native Parameter Change, sous forme de liste d'octets sans F0/F7."""
    high, mid, low = address
    values = list(data) if isinstance(data, (list, tuple, bytes)) else [data]
    for byte in (high, mid, low, *values):
        if not 0 <= byte <= 0x7F:
            raise ValueError(f"Octet hors plage 7 bits : {byte}")
    return [YAMAHA_ID, 0x10 | device, *GROUP_ID, MODEL_ID, high, mid, low, *values]


def common(low, data, device=DEVICE_ALL):
    return parameter_change((COMMON, 0x00, low), data, device)


def part(p, low, data, device=DEVICE_ALL):
    return parameter_change((PART, p, low), data, device)


def note_number(name):
    """'C3' -> 60 (convention Yamaha : C3 = do central = 60, C-2 = 0)."""
    letters = name[:2] if len(name) > 1 and name[1] == "#" else name[:1]
    octave = int(name[len(letters):])
    return NOTE_NAMES.index(letters.upper()) + (octave + 2) * 12


def drawbar_value(position):
    """Position de tirette 0-8 -> valeur 0-127 (table p.62)."""
    return 127 if position == 8 else position * 18


def select_voice(p, number, device=DEVICE_ALL):
    """Sélectionne une voix (0-362) sur une Part : voix de la catégorie puis catégorie."""
    category = category_of(number)
    voice_address = 0x01 + category * 2
    return [
        part(p, voice_address, [number >> 7, number & 0x7F], device),
        part(p, CURRENT_CATEGORY, category, device),
    ]


def effect(p, slot, name, depth=64, rate=64, device=DEVICE_ALL):
    """Active Effect 1 ou 2 d'une Part avec le type donné."""
    switch = EFFECT1_SWITCH if slot == 1 else EFFECT2_SWITCH
    return [
        part(p, switch + 1, EFFECT_TYPES.index(name), device),
        part(p, switch + 2, depth, device),
        part(p, switch + 3, rate, device),
        part(p, switch, 1, device),
    ]


def live_set_select(page, slot, channel=0):
    """Rappelle un Live Set (page 1-20, slot 1-8) : Bank MSB 63, LSB page-1, PC slot-1."""
    return [
        [0xB0 | channel, 0x00, 63],
        [0xB0 | channel, 0x20, page - 1],
        [0xC0 | channel, slot - 1],
    ]
