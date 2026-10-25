# Yamaha CK61 — sons de scène via MIDI

Envoie des sons de scène prêts à jouer au Yamaha CK61 (et CK76/CK88) depuis un
ordinateur relié en USB. Le script programme le Live Set Sound affiché (Parts A/B/C,
voix, split, tirettes d'orgue, drive, effets, reverb et delay) à l'aide des
Parameter Changes SysEx documentés dans le *Data List* du manuel (p.52-63).

Rien n'est écrit en mémoire : pour garder un son, appuyez sur **[STORE]** sur le clavier.

## Installation

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Branchez le CK61 en USB. Les réglages d'usine conviennent (MIDI Device Number = All).

## Utilisation

```sh
.venv/bin/python -m ck61 list                  # presets disponibles
.venv/bin/python -m ck61 send rhodes           # charge le Rhodes dans le Live Set en cours
.venv/bin/python -m ck61 send jazz-organ --dry-run   # affiche les messages sans les envoyer
.venv/bin/python -m ck61 voices pad            # cherche une voix interne
.venv/bin/python -m ck61 voice B "Warm Strings"     # change la voix d'une Part
.venv/bin/python -m ck61 recall 1 3            # rappelle le Live Set page 1, slot 3
.venv/bin/python -m ck61 export syx            # un fichier .syx par preset
```

### Enregistrer les sons dans le clavier

```sh
.venv/bin/python -m ck61 slots                 # noms des 160 Live Sets
.venv/bin/python -m ck61 store                 # tous les presets, à la suite de vos Live Sets
.venv/bin/python -m ck61 store rhodes clav     # seulement certains presets
.venv/bin/python -m ck61 store --start 10-1    # à partir d'un slot précis
```

`store` sauvegarde d'abord les 160 Live Sets dans `backups/`, place les sons après le
dernier Live Set qui ne s'appelle pas « Init Sound », affiche le plan et demande
confirmation. Chaque slot est relu après l'écriture pour vérifier, puis le tout est
inscrit en mémoire flash pour survivre à l'extinction. Pour revenir en arrière :

```sh
.venv/bin/python -m ck61 restore backups/ck61-AAAAMMJJ-HHMMSS.syx
```

Les fichiers `.syx` peuvent être envoyés avec n'importe quel outil SysEx
(SysEx Librarian, MIDI-OX, un DAW…).

## Presets

| Clé | Son |
|---|---|
| `grand` | Piano à queue CFX, réverbe de salle |
| `piano-strings` | Piano + nappe de cordes |
| `rhodes` | Rhodes 73, auto-pan, léger overdrive |
| `wurli` | Wurlitzer avec trémolo |
| `dx-ballad` | E.Piano DX7 chorusé + pad |
| `jazz-organ` | Orgue 888000000, percussion 3rd rapide, chorus C3 |
| `rock-organ` | Orgue saturé 888000000 |
| `gospel-organ` | Orgue 888888888 |
| `bass-piano` | Basse main gauche / piano main droite, split en C3 |
| `brass` | Section cuivres |
| `jump` | Synth brass « Jump » |
| `80s-pad` | Cordes JP + Pad 80 |
| `strings-choir` | Cordes + chœur |
| `clav` | Clavinet avec touch wah |
| `lead` | Lead analogique mono, portamento, delay |
| `velours` | DX tine chorusé + nappe vocodeur + glock à l'octave (ballade pop) |
| `french-touch` | Basse synthé glissante / poly funky phasé + pad flangé, split C3 |
| `retro-futur` | Cordes analogiques chorusées + pad à balayage |
| `cp-grand-ecran` | CP80 + cordes légères + cristal à l'octave |
| `annees-80` | E.Piano DX7 doublé de cuivres OB |
| `pluie-dor` | Harpe-cloche en delay croisé + carré doux (hook) |
| `solo-nacre` | Lead mono glissant + sifflet synthé à l'octave |
| `grand-final` | Sub-basse sinus / pad pop + chœur aérien, split C3 |

Pour créer un son, ajoutez une entrée dans `PRESETS` ([ck61/presets.py](ck61/presets.py)).
Les noms de voix viennent de [ck61/voices.py](ck61/voices.py).
