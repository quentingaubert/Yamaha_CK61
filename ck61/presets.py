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
    "velours": {
        "name": "Velours",
        "description": "Ballade pop : DX tine chorusé, nappe vocodeur qui respire, "
                       "scintillement de glock une octave au-dessus.",
        "reverb": ("Hall", 42),
        "delay": ("Analog", 28, 72),
        "parts": [
            {"voice": "DX FTine", "volume": 108, "effects": [("Symphonic", 50, 40)]},
            {
                "voice": "VP Soft", "volume": 60, "cutoff": 50,
                "attack": 88, "release": 92,
                "effects": [("Auto Pan", 45, 28)],
            },
            {
                "voice": "Round Glock", "volume": 34, "shift": 12, "release": 72,
                "effects": [("Cross Delay", 40, 64)],
            },
        ],
    },
    "french-touch": {
        "name": "French Touch",
        "description": "Basse synthé qui glisse main gauche ; poly funky phasé + pad "
                       "analogique flangé main droite (split C3).",
        "split": "A/BC",
        "split_point": "C3",
        "reverb": ("Hall", 30),
        "delay": ("Digital", 22, 56),
        "parts": [
            {
                "voice": "Click SynBass", "volume": 115,
                "mono": "Fingered Portamento", "portamento": 14,
                "drive": ("Comp", 70),
            },
            {
                "voice": "Funky Poly", "volume": 98, "cutoff": 70,
                "effects": [("Small Phaser", 55, 38), ("Analog Delay", 30, 60)],
            },
            {
                "voice": "Analog Pad", "volume": 52, "cutoff": 46,
                "attack": 92, "release": 85,
                "effects": [("VCM Flanger", 45, 20)],
            },
        ],
    },
    "retro-futur": {
        "name": "Retro Futur",
        "description": "Cordes analogiques très chorusées + pad à balayage : "
                       "la nappe planante des synthés français de la fin des 70s.",
        "reverb": ("Hall", 55),
        "delay": ("Analog", 30, 80),
        "parts": [
            {
                "voice": "Analog Str", "volume": 105, "attack": 72, "release": 88,
                "effects": [("Symphonic", 72, 35), ("VCM Stereo Phaser", 40, 18)],
            },
            {"voice": "Sweep Pad 1", "volume": 62, "attack": 80, "release": 95},
        ],
    },
    "cp-grand-ecran": {
        "name": "CP Grand Ecran",
        "description": "Piano électrique CP80 des grandes chansons 80s, cordes légères "
                       "en fond et cristal une octave au-dessus.",
        "reverb": ("Hall", 38),
        "parts": [
            {"voice": "CP80 1", "volume": 112, "effects": [("SPX Chorus", 40, 35)]},
            {"voice": "Lite Strings1", "volume": 56, "attack": 82, "release": 85},
            {"voice": "Soft Crystal", "volume": 30, "shift": 12, "release": 70},
        ],
    },
    "annees-80": {
        "name": "Annees 80",
        "description": "E.Piano DX7 brillant doublé de cuivres OB : les riffs de clavier "
                       "de la variété synthé.",
        "reverb": ("Hall", 30),
        "delay": ("Digital", 18, 50),
        "parts": [
            {"voice": "DX 7 II", "volume": 110, "effects": [("Symphonic", 45, 40)]},
            {"voice": "OB Brass 2", "volume": 70, "cutoff": 58, "release": 60},
        ],
    },
    "pluie-dor": {
        "name": "Pluie d'Or",
        "description": "Harpe-cloche en delay croisé + carré doux : un son de hook de "
                       "refrain, à jouer en arpèges.",
        "reverb": ("Hall", 40),
        "parts": [
            {"voice": "Bell Harp", "volume": 105, "effects": [("Cross Delay", 50, 64)]},
            {"voice": "Soft Square", "volume": 62, "cutoff": 55, "release": 70},
        ],
    },
    "solo-nacre": {
        "name": "Solo Nacre",
        "description": "Lead mono doux qui glisse, doublé d'un sifflet synthé à l'octave : "
                       "pour les mélodies et les solos.",
        "reverb": ("Hall", 35),
        "delay": ("Analog", 40, 70),
        "parts": [
            {
                "voice": "Mini Soft", "volume": 110,
                "mono": "Fingered Portamento", "portamento": 40,
            },
            {
                "voice": "Synth Whistle", "volume": 32, "shift": 12,
                "mono": "Fingered Portamento", "portamento": 40,
            },
        ],
    },
    "grand-final": {
        "name": "Grand Final",
        "description": "Sub-basse sinus main gauche ; pad pop + chœur aérien main droite "
                       "pour les fins de morceau (split C3).",
        "split": "A/BC",
        "split_point": "C3",
        "reverb": ("Hall", 55),
        "parts": [
            {"voice": "Fat Sine", "volume": 112, "mono": "Normal"},
            {"voice": "Pop Pad", "volume": 95, "attack": 70, "release": 90},
            {
                "voice": "Air Choir", "volume": 70, "attack": 80, "release": 92,
                "effects": [("SPX Chorus", 40, 30)],
            },
        ],
    },
    "caravane-couplet": {
        "name": "Caravane Nappes",
        "description": "Pad analogique large et chaud + cordes pour les accords ; tout en "
                       "haut du clavier, un glockenspiel avec écho pour les petites réponses.",
        "split": "AB/C",
        "split_point": "F#4",
        "reverb": ("Hall", 48),
        "parts": [
            {
                "voice": "Analog Pad", "volume": 104, "cutoff": 50, "attack": 70, "release": 92,
                "effects": [("Symphonic", 55, 30)],
            },
            {"voice": "Warm Strings", "volume": 74, "cutoff": 52, "attack": 78, "release": 92},
            {
                "voice": "Round Glock", "volume": 72, "release": 70,
                "effects": [("Cross Delay", 45, 64)],
            },
        ],
    },
    "caravane-moderne": {
        "name": "Caravane Pop",
        "description": "Trois zones : pluck synthé à gauche dont le delay en croche pointée "
                       "crée un groove de doubles-croches, pad pop au milieu, cristal en haut.",
        "split": "A/B/C",
        "split_points": ("C3", "G4"),
        "tempo": 100,
        "reverb": ("Hall", 45),
        "delay": ("Tempo", 48, "1/8 Dot."),
        "parts": [
            {"voice": "Funky Poly", "volume": 92, "cutoff": 58, "release": 40},
            {
                "voice": "Pop Pad", "volume": 98, "cutoff": 52, "attack": 72, "release": 90,
                "effects": [("Symphonic", 50, 30)],
            },
            {"voice": "Soft Crystal", "volume": 78, "release": 64},
        ],
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

    if "tempo" in preset:
        tempo = round(preset["tempo"] * 10)
        messages.append(sx.common(sx.TEMPO, [tempo >> 7, tempo & 0x7F], device))

    delay = preset.get("delay")
    if delay:
        # le 3e élément est un temps 0-127, ou une valeur de note pour le delay "Tempo"
        kind, depth, time = delay
        messages += [
            sx.common(sx.DELAY_TYPE, sx.DELAY_TYPES.index(kind), device),
            sx.common(sx.DELAY_DEPTH, depth, device),
        ]
        if kind == "Tempo":
            messages.append(sx.common(sx.DELAY_TEMPO_TIME, sx.TEMPO_DELAY_TIMES.index(time), device))
        else:
            messages.append(sx.common(sx.DELAY_TIME, time, device))
    messages.append(sx.common(sx.DELAY_SWITCH, 1 if delay else 0, device))
    messages.append(sx.common(sx.ROTARY_FAST, 0, device))

    parts = preset["parts"]
    for p in range(3):
        if p < len(parts):
            messages += build_part(p, parts[p], device)
        else:
            messages.append(sx.part(p, sx.PART_SWITCH, 0, device))
    return messages
