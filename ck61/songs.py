"""Parties de clavier à jouer en MIDI sur le CK61 pour montrer un accompagnement.

Notes MIDI avec C3 = 60 (do central, convention Yamaha). Les voicings sont choisis
pour bouger le moins possible d'un accord à l'autre.
"""

ARRANGEMENTS = {
    # Live Set « Caravane Nappes » : pad tenu, glock au-dessus du fa#4
    "classique": {
        "live_set": (16, 1),
        # quinte à vide, au-dessus du registre de la basse
        "left": {"Dm": [50, 57], "F": [53, 60], "C": [48, 55], "Bb": [46, 53]},
        # la note du haut descend ré → do → do → si♭
        "right": {"Dm": [65, 69, 74], "F": [65, 69, 72], "C": [64, 67, 72], "Bb": [62, 65, 70]},
        "left_rhythm": None,  # main gauche tenue toute la mesure
        # (note, début, durée) en temps : ré – do – la sur les temps 3 et 4
        "gimmick": [(86, 2, 0.5), (84, 2.5, 0.5), (81, 3, 1)],
    },
    # Live Set « Caravane Pop » : pluck + delay en croche pointée à gauche,
    # pad au milieu, cristal au-dessus du sol4
    "moderne": {
        "live_set": (16, 3),
        # une seule note par main gauche : la fondamentale, une fois par temps
        "left": {"Dm": [50], "F": [53], "C": [48], "Bb": [46]},
        # accords suspendus avec un la qui plane en haut (sauf sur Do)
        "right": {"Dm": [62, 64, 69], "F": [60, 64, 69], "C": [60, 62, 67], "Bb": [62, 65, 69]},
        "left_rhythm": [(0, 0.9), (1, 0.9), (2, 0.9), (3, 0.9)],
        # ré – do – la en contretemps, qui pousse vers la mesure suivante
        "gimmick": [(86, 2.5, 0.5), (84, 3, 0.5), (81, 3.5, 0.5)],
    },
}

NOTE_NAMES_FR = ["do", "do#", "ré", "mi♭", "mi", "fa", "fa#", "sol", "sol#", "la", "si♭", "si"]

COUPLET_GRID = ["Dm", "F", "F", "C"]
SUITE_GRID = ["Dm", "F", "C", "Bb"]
CARAVANE_SECTIONS = [
    {"name": "Strophe, 1re moitié", "hands": "droite", "chords": COUPLET_GRID},
    {"name": "Strophe, 2e moitié", "hands": "deux mains", "chords": SUITE_GRID},
    {"name": "Refrain « Allez viens »", "hands": "plein", "chords": COUPLET_GRID + SUITE_GRID},
]

SONGS = {
    "caravane": {
        "title": "Caravane (Raphaël) — capo 5 à la guitare, donc en ré mineur",
        "tempo": 99,
        "arrangement": "classique",
        "sections": CARAVANE_SECTIONS,
    },
    "caravane-moderne": {
        "title": "Caravane (Raphaël), version moderne — en ré mineur",
        "tempo": 100,
        "arrangement": "moderne",
        "sections": CARAVANE_SECTIONS,
    },
}


def chord_notes(chord, hands, arrangement="classique"):
    """Notes main gauche et main droite d'un accord. « droite » : main droite seule ;
    « deux mains » : avec la main gauche ; « plein » : main droite doublée à l'octave."""
    arr = ARRANGEMENTS[arrangement]
    left = [] if hands == "droite" else arr["left"][chord]
    right = arr["right"][chord]
    if hands == "plein":
        right = right + [right[0] + 12]
    return left, right


def bar_events(chord, hands, bar, gimmick, arrangement="classique"):
    """(début, durée, notes) d'une mesure en secondes. Avec le gimmick, la main droite
    lâche l'accord juste avant la réponse jouée tout en haut du clavier."""
    arr = ARRANGEMENTS[arrangement]
    beat = bar / 4
    left, right = chord_notes(chord, hands, arrangement)
    events = []
    if left:
        if arr["left_rhythm"] is None:
            events.append((0.0, bar - 0.02, left))
        else:
            events += [(start * beat, length * beat, left) for start, length in arr["left_rhythm"]]
    if gimmick:
        release = arr["gimmick"][0][1]
        events.append((0.0, release * beat - 0.05, right))
        events += [(start * beat, length * beat - 0.03, [note]) for note, start, length in arr["gimmick"]]
    else:
        events.append((0.0, bar - 0.02, right))
    return events
