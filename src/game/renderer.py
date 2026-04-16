from __future__ import annotations


class GameRenderer:
    def render_start_menu(self):
        print("=== WILLKOMMEN IN VICE CITY DRAGONS! ===")
        print("Ein textbasiertes Krimi-Abenteuer in einer fiktiven Küstenmetropole")
        print("1. Neues Spiel starten")
        print("2. Spiel laden")

    def render_character_menu(self):
        print("\nWaehle deinen Protagonisten:")
        print("1. Jason Duval (Ex-Militaer, gute Kampffaehigkeiten)")
        print("2. Lucia Caminos (Frueher aus dem Gefaengnis, gute Stealth-Faehigkeiten)")

    def render_main_menu(self):
        print("\n=== VICE CITY HAUPTMENUE ===")
        print("1. Attribute anzeigen")
        print("2. Rasten/Unterschlupf")
        print("3. Vice City erkunden")
        print("4. Schwarzmarkt besuchen")
        print("5. Kriminelles Training")
        print("6. Mission-Brett (Neu!)")
        print("7. Drachen der Konsequenzen konfrontieren")
        print("8. Bildschirm-Löschung umschalten")
        print("9. Spiel speichern")
        print("10. Spiel beenden")

    def render_mission_board(self, available_missions):
        print("\n[MISSION] VERFÜGBARE MISSIONEN:")
        for i, mission in enumerate(available_missions):
            print(f"{i+1}. {mission.name} (Kapitel {mission.chapter}, {'*' * mission.difficulty})")
            print(
                f"   Belohnung: ${mission.rewards.get('cash', 0)}, +{mission.rewards.get('reputation', 0)} Reputation"
            )
        print(f"{len(available_missions)+1}. Zurück zum Hauptmenü")
