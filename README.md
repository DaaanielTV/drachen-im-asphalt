# Die Legende des Drachen: Vice City

Ein textbasiertes Kriminal-Abenteuerspiel inspiriert von GTA 6, entwickelt als Schulprojekt für Fachinformatiker.

## Spielbeschreibung

"Die Legende des Drachen: Vice City" ist ein reifes Text-Adventure, in dem der Spieler zwischen zwei Protagonisten wählt - Jason oder Lucia - und durch die kriminelle Unterwelt von Vice City navigiert. Der Drache erscheint als psychologische Metapher für die Konsequenzen des kriminellen Lebens, die sich durch Drogeneinflüsse und Stress manifestieren.

## Hauptfunktionen

### Charaktersystem
- **Zwei Protagonisten**: Wähle zwischen Jason (militärischer Hintergrund) oder Lucia (Gefängniserfahrung)
- **Eindeutige Fähigkeiten**: Jeder Charakter hat unterschiedliche Combat- und Stealth-Werte
- **Fußfessel-System**: Lucia startet mit einer Fußfessel, die Gameplay beeinflusst

### Missions-System
- **Mehrphasige Missionen**: Dialog, Reise, Action und Escape-Phasen
- **Spielerentscheidungen**: Wichtige Entscheidungen beeinflussen den Ausgang
- **Missionsschaltung**: Erfolgreiche Missionen schalten neue Inhalte frei

### Stadtteil-Exploration
- **9 Stadtteile**: Ocean Beach, Washington Beach, Vice Point, Viceport, Downtown, Little Haiti, Starfish Island, Everglades, Vice Keys
- **Jeder Stadtteil hat**: Einzigartige Gefahrenlevel, Begegnungen und Spezial-Features
- **Saisonsystem**: Dynamische Saisonwechsel in Ocean Beach beeinflussen Belohnungen

### Story-Progression
- **6 Kapitel**: Von der Ankunft bis zur finalen Konfrontation
- **Story-Events**: Wichtige Momente triggern basierend auf Spieleraktionen
- **Charakter-Entwicklung**: Psychologische Elemente und Partner-Vertrauen

### Kriminal-System
- **Vielfältige Begegnungen**: Polizei, Gangs, Drogendealer, zivile Opfer
- **Kampf-Optionen**: Kämpfen, fliehen oder bestechen
- **Wanted Level**: Steigende Polizeiaufmerksamkeit mit Konsequenzen

### Psychologische Elemente
- **Drogeneffekte**: Temporäre Effekte mit Halluzinationen
- **Drachen-Metapher**: Psychologische Konsequenzen als Drachen-Halluzinationen
- **Stress-System**: Hoher Stress löst mentale Auswirkungen aus

## Spielanleitung

1. Starte das Spiel mit `python main.py`
2. Wähle deinen Protagonisten (Jason oder Lucia)
3. Erstelle deinen Charakter mit einem Namen
4. Nutze das Hauptmenü für folgende Aktionen:
   - **Attribute anzeigen**: Zeigt alle Charakter-Informationen
   - **Rasten**: Stellt Ausdauer wieder her und reduziert Wanted Level
   - **Vice City erkunden**: Wähle Stadtteile für Kriminal-Aktivitäten
   - **Missionen annehmen**: Erfülle Missionen für Geld und Reputation
   - **Spiel speichern**: Speichere deinen Fortschritt
   - **Spiel beenden**: Verlasse das Spiel

## Stadtteil-Übersicht

| Stadtteil | Gefahrenlevel | Spezial-Feature | Typische Aktivitäten |
|-----------|---------------|-----------------|---------------------|
| Ocean Beach | ⭐⭐⭐ | Tourismus-Saison | Taschendiebstahl, Touristen abzocken |
| Washington Beach | ⭐⭐⭐⭐ | Motel-Netzwerk | Motel-Raids, Erpressung |
| Vice Point | ⭐⭐⭐⭐⭐ | Überwachung | Einbrüche, Autodiebstahl |
| Viceport | ⭐⭐⭐⭐⭐⭐ | Container-Management | Schmuggel, Dockyard-Heists |
| Downtown | ⭐⭐⭐⭐⭐⭐⭐ | Unternehmenskriminalität | Überfälle, Erpressung |
| Little Haiti | ⭐⭐⭐⭐⭐⭐⭐⭐ | Gebiets-Kontrolle | Gang-Kämpfe, Drogendeals |
| Starfish Island | ⭐⭐⭐⭐⭐⭐⭐ | Gesellschaftlicher Aufstieg | Villa-Einbrüche, Elite-Kriminalität |
| Everglades | ⭐⭐⭐⭐⭐⭐⭐⭐⭐ | Sumpf-Basis | Schmuggel, Drogenlabore |
| Vice Keys | ⭐⭐⭐⭐⭐⭐ | Insel-Schmuggel | Schwarzmarkt, Menschenhandel |

## Klassenstruktur

### Hauptklassen
- **Protagonist**: Spielerklasse mit allen Attributen und Aktionen
- **StoryManager**: Verwaltet Kapitel und Story-Events
- **MissionManager**: Koordiniert alle Missionen und Mission-Geber
- **DistrictManager**: Verwaltet Stadtteile und Saisons

### Gameplay-Klassen
- **Mission**: Einzelne Missionen mit Phasen-System
- **MissionPhase**: Dialog, Reise, Action oder Escape-Phasen
- **District**: Stadtteil mit Eigenschaften und Features
- **DrugEffect**: Drogeneffekte mit Halluzinationen
- **DragonHallucination**: Psychologische Drachen-Begegnungen

### KI-Klassen
- **ViceCityDragon**: Der finale Endgegner als Metapher
- **MissionGiver**: NPCs die Missionen anbieten

## Technische Details

- **Sprache**: Python 3.11+
- **Speicherformat**: JSON für Spielstände und Drachen-Daten
- **Benötigte Module**: `json`, `os`, `random`, `time`
- **Zeichencodierung**: UTF-8 (für deutsche Sonderzeichen)
- **Testabdeckung**: Automatisierte Tests in `test_game.py`

## Installation und Ausführung

1. Stelle sicher, dass Python 3.11+ installiert ist
2. Lade alle Spiel-Dateien in einen Ordner
3. Stelle sicher, dass `dragon.json` im selben Verzeichnis liegt
4. Führe `python main.py` in der Kommandozeile aus

### Tests ausführen
```bash
python test_game.py
```

## Spiel-Features im Detail

### Charakter-Entwicklung
- **Level-System**: Erfahrung durch Missionen und kriminelle Aktivitäten
- **Skill-Progression**: Combat und Stealth verbessern sich durch Nutzung
- **Partner-Vertrauen**: Wichtig für bestimmte Missionen und Story-Elemente

### Missionen
- **Verschiedene Schwierigkeitsgrade**: 1-10 Sterne
- **Vielfältige Belohnungen**: Geld, Reputation, Items, Vertrauen
- **Konsequenzen**: Fehlschläge erhöhen Wanted Level und reduzieren Ausdauer

### Psychologische Systeme
- **Stress-Mechanik**: Hoher Stress und Drogen lösen Drachen-Halluzinationen aus
- **Moralische Entscheidungen**: Wahlen beeinflussen die Story und Charakter-Entwicklung
- **Konsequenzen-System**: Jede Aktion hat langfristige Auswirkungen

## Speicherstand-Struktur

Spielstände werden als JSON gespeichert mit:
- Charakter-Attributen (Name, Level, Cash, etc.)
- Story-Flags und Fortschritt
- Mission-Status
- Inventar und Ausrüstung

## Hinweise

- Das Spiel enthält mature Inhalte und ist für erwachsene Spieler gedacht
- Die Drachen-Darstellung ist metaphorisch und psychologisch
- Deutsche Sprache mit regionalen Vice City-Elementen

Viel Spaß bei "Die Legende des Drachen: Vice City"!
