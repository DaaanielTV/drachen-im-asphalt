# Contributing to Drachen im Asphalt

Vielen Dank für dein Interesse am Projekt.

## Grundsätze

- Halte Änderungen klein, nachvollziehbar und fokussiert.
- Verändere keine Kernlogik ohne klaren Grund (Bugfix, Konsistenz, Wartbarkeit).
- Dokumentiere sichtbare Verhaltensänderungen im Pull Request.

## Entwicklungsablauf

1. Repository forken und Branch erstellen.
2. Entwicklungsumgebung einrichten (siehe `README.md`).
3. Änderungen umsetzen.
4. Tests lokal ausführen:
   ```bash
   PYTHONPATH=. pytest -q
   ```
5. Commit mit klarer Message erstellen.
6. Pull Request mit Motivation, Änderungen und Testnachweis öffnen.

## Code-Stil

- Folge dem bestehenden Python-Stil im Projekt.
- Nutze sprechende Namen und kleine Funktionen.
- Vermeide unnötige Abhängigkeiten.

## Tests

- Neue Funktionalität sollte durch Tests begleitet werden.
- Bestehende Tests dürfen nicht ohne Begründung entfernt werden.

## Dokumentation

Bei relevanten Änderungen bitte auch Dokumentation aktualisieren:

- `README.md` für Nutzerdokumentation
- `src/README.md` für Architektur-/Modulhinweise

## Melden von Fehlern

Bitte öffne ein Issue mit:

- erwartetes Verhalten
- tatsächliches Verhalten
- Reproduktionsschritten
- Umgebung (OS, Python-Version)

## Verhaltenskodex

Mit dem Beitragen stimmst du dem [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) zu.
