# Technische Übersicht (`src/`)

Diese Datei beschreibt die interne Struktur des Spiels **Drachen im Asphalt**.

## Modulstruktur

- `src/main.py` – CLI-Einstiegspunkt und Hauptspielschleife
- `src/game/` – Rendering, Session-Steuerung, Kommandologik, Persistenz
- `src/characters/` – Protagonist und Dragon/Boss-Logik
- `src/missions/` – Missionen, Mission Manager, Mission-Giver
- `src/districts/` – Bezirksdaten und Bezirksverwaltung
- `src/story/` – Kapitel, Konsequenzen und Journal
- `src/effects/` – Drogeneffekte und Halluzinationssystem
- `src/items/` – Item-/Waffenmodelle
- `src/ui/` – Textdarstellung/Lesemodus

## Architekturprinzipien

- Möglichst klare Trennung zwischen Story-, Domänen- und Laufzeitlogik
- Datenpersistenz über JSON statt proprietärer Formate
- Keine Build-Artefakte im Repository

## Testbezug

Tests liegen unter `tests/` und prüfen insbesondere:

- Architektur-Integrität
- Save/Load-Flows

Ausführung aus Repo-Root:

```bash
PYTHONPATH=. pytest -q
```
