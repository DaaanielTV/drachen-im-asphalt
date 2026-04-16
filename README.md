# Drachen im Asphalt

Ein textbasiertes Krimi-Adventure in Python. Das Projekt kombiniert Story-Entscheidungen, Missionsfortschritt und persistente Spielstände in einer modularen Codebasis.

## Projektüberblick

**Drachen im Asphalt** ist ein deutschsprachiges Terminal-Spiel mit Fokus auf:

- erzählerische Progression über Kapitel,
- ein Missions- und Begegnungssystem,
- Charakterentwicklung inklusive Ressourcen- und Risiko-Management,
- speicherbare Spielstände (JSON-basiert).

Die Handlung spielt in einer fiktiven, neongeprägten Küstenstadt mit verschiedenen Bezirken und eskalierenden Konsequenzen für Spielerentscheidungen.

## Features / Zweck

- Zwei spielbare Protagonisten mit unterschiedlichen Startwerten.
- Modulares Domänenmodell (`characters`, `missions`, `districts`, `effects`, `story`, `game`, `ui`).
- Persistenz für Spielstand und Story-Fortschritt.
- Textausgabe mit Lesemodi und optionaler Bildschirmbereinigung.
- Automatisierte Tests für Kernarchitektur und Save/Load-Verhalten.

## Installation

### Voraussetzungen

- Python **3.10+** (empfohlen: 3.11)
- `pip`

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip pytest
```

## Nutzung

Spielstart aus dem Repository-Root:

```bash
python -m src.main
```


## Development Setup

```bash
git clone <repository-url>
cd drachen-im-asphalt
python -m venv .venv
source .venv/bin/activate
pip install -U pip pytest
```

Tests ausführen:

```bash
PYTHONPATH=. pytest -q
```

## Konfiguration

Das Projekt nutzt aktuell keine externe `.env`-Konfiguration. Relevante Datenquellen:

- `data/dragon.json`: persistente Drachen-/Bossdaten
- Savegames werden zur Laufzeit als JSON im Arbeitsverzeichnis abgelegt

Empfehlung für Beiträge: Laufzeitdaten nicht versionieren und stattdessen reproduzierbar erzeugen.

## Build- / Run-Instruktionen

Dieses Projekt erzeugt keine distributierten Build-Artefakte. Der empfohlene Ablauf ist:

1. Quellcode auschecken
2. Python-Umgebung einrichten
3. Spiel direkt per `python -m src.main` starten
4. Tests per `PYTHONPATH=. pytest -q` validieren

Falls früher generierte oder temporäre Dateien im Repository enthalten waren, wurden sie entfernt. Sie sollen lokal neu erzeugt statt eingecheckt werden.

## Troubleshooting

### `ModuleNotFoundError: No module named 'src'`

Führe Tests mit gesetztem `PYTHONPATH` aus:

```bash
PYTHONPATH=. pytest -q
```

### Kodierungsprobleme bei Umlauten

Stelle sicher, dass das Terminal UTF-8 verwendet.

### Kein Speicherstand gefunden

Das ist beim ersten Start normal. Starte ein neues Spiel und speichere danach.

## Zusätzliche Dokumentation

- [`CONTRIBUTING.md`](CONTRIBUTING.md) – Beitragshinweise
- [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) – Verhaltensregeln
- [`src/README.md`](src/README.md) – technische Modulübersicht
- [`LICENSE`](LICENSE) – GNU GPLv3
