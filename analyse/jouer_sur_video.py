"""Joue une partie de clavier sur le CK61 par-dessus un enregistrement, et enregistre le CK.

L'audio du concert sort sur la sortie son par défaut du Mac, les notes partent vers le
CK en MIDI et la sortie USB du CK est enregistrée, tout cela sur l'horloge de
PortAudio : la piste enregistrée est calée sur le concert sans note-repère.

    .venv-analyse/bin/python analyse/jouer_sur_video.py analyse/caravane/grille.json \
        concert.wav clavier.wav --live-set 16-1

La grille est un JSON {"bars": [{"t", "end", "chord", "hands", "gimmick"}, ...]}
(temps en secondes depuis le début de l'enregistrement).
"""

import argparse
import json
import sys
import threading
import time
from pathlib import Path

import mido
import numpy as np
import sounddevice as sd
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ck61 import sysex as sx  # noqa: E402
from ck61.songs import ARRANGEMENTS, bar_events  # noqa: E402

GLOCK_ZONE = 79  # au-dessus du point de split du Live Set Caravane


# Zones de notes de chaque partie (main gauche sous le do central, réponses tout en haut)
PARTS = {
    "tout": (0, 128),
    "pulsation": (0, 60),
    "pad": (60, GLOCK_ZONE),
}


def schedule_from_grid(grid, arrangement="classique", part="tout"):
    """Notes à jouer ; une partie autre que « tout » ne garde que sa zone du clavier,
    et la main droite reste alors tenue toute la mesure (pas de réponse)."""
    low, high = PARTS[part]
    events = []
    for bar in grid["bars"]:
        gimmick = bar.get("gimmick", False) and part == "tout"
        for offset, length, notes in bar_events(
                bar["chord"], bar["hands"], bar["end"] - bar["t"], gimmick, arrangement):
            notes = [n for n in notes if low <= n < high]
            if not notes:
                continue
            events.append((bar["t"] + offset, 1, "note_on", notes))
            events.append((bar["t"] + offset + length, 0, "note_off", notes))
    return sorted(events, key=lambda e: (e[0], e[1]))


def find_ck_input():
    for index, device in enumerate(sd.query_devices()):
        if "CK" in device["name"] and device["max_input_channels"] > 0:
            return index
    raise SystemExit("Entrée audio du CK introuvable (câble USB ?)")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("grid")
    parser.add_argument("concert", help="audio du concert (wav)")
    parser.add_argument("output", help="wav du clavier enregistré, calé sur le concert")
    parser.add_argument("--arrangement", default="classique", choices=list(ARRANGEMENTS))
    parser.add_argument("--partie", default="tout", choices=list(PARTS), help="ne jouer qu'une partie")
    args = parser.parse_args()

    concert, sr = sf.read(args.concert, dtype="float32", always_2d=True)
    events = schedule_from_grid(json.load(open(args.grid)), args.arrangement, args.partie)
    port = mido.open_output(next(n for n in mido.get_output_names() if "CK" in n))
    for message in sx.live_set_select(*ARRANGEMENTS[args.arrangement]["live_set"]):
        port.send(mido.Message.from_bytes(message))
    time.sleep(0.5)

    recorded, playhead = [], {"pos": 0, "start": None}
    finished = threading.Event()

    def record(indata, frames, timing, status):
        recorded.append((timing.inputBufferAdcTime, indata.copy()))

    def play(outdata, frames, timing, status):
        pos = playhead["pos"]
        if playhead["start"] is None:
            playhead["start"] = timing.outputBufferDacTime  # instant où le concert démarre
        chunk = concert[pos:pos + frames]
        outdata[:len(chunk)] = chunk[:, :outdata.shape[1]]
        outdata[len(chunk):] = 0
        playhead["pos"] = pos + frames
        if pos >= len(concert):
            finished.set()

    ck_input = find_ck_input()
    # le CK n'envoie le son que sur un canal ; après certaines applications (GarageBand),
    # macOS refuse même de l'ouvrir en stéréo
    try:
        with sd.InputStream(device=ck_input, channels=2, samplerate=sr):
            pass
        channels = 2
    except sd.PortAudioError:
        channels = 1
    with sd.InputStream(device=ck_input, channels=channels, samplerate=sr, callback=record) as inp, \
            sd.OutputStream(channels=concert.shape[1], samplerate=sr, callback=play) as out:
        while playhead["start"] is None:
            time.sleep(0.001)
        start = playhead["start"]
        try:
            for moment, _, kind, notes in events:
                while out.time < start + moment:
                    time.sleep(0.001)
                for note in notes:
                    velocity = 72 if note >= GLOCK_ZONE else 90
                    port.send(mido.Message(kind, note=note, velocity=velocity))
            finished.wait(timeout=len(concert) / sr + 5)
        finally:
            port.send(mido.Message("control_change", control=123, value=0))
        in_start = recorded[0][0]

    audio = np.concatenate([chunk for _, chunk in recorded])
    if audio.shape[1] == 1:
        audio = np.repeat(audio, 2, axis=1)
    first = int(round((start - in_start) * sr))  # échantillon du CK correspondant au début du concert
    audio = audio[first:first + len(concert)]
    audio = np.vstack([audio, np.zeros((len(concert) - len(audio), 2), dtype=audio.dtype)])
    sf.write(args.output, audio, sr, subtype="PCM_24")
    print(f"{args.output} : {len(audio) / sr:.1f} s, calé sur le concert (décalage {first / sr:.3f} s)")


if __name__ == "__main__":
    main()
