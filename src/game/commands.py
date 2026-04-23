from __future__ import annotations

from src.telemetry import metrics as telemetrics
from src.telemetry import settings as teleSettings


class GameCommandHandler:
    def __init__(self, protagonist, dragon, renderer):
        self.protagonist = protagonist
        self.dragon = dragon
        self.renderer = renderer

    def _record_command(self, command: str) -> None:
        if teleSettings.get_telemetry_enabled():
            telemetrics.record_command(command)

    def execute(self, choice: str) -> bool:
        if choice == "1":
            self._record_command("attr")
            self.protagonist.display_attributes()
        elif choice == "2":
            self._record_command("rest")
            self.protagonist.rest()
        elif choice == "3":
            self._record_command("explore")
            self.protagonist.explore_vice_city()
        elif choice == "4":
            self._record_command("blackmarket")
            self.protagonist.visit_black_market()
        elif choice == "5":
            self._record_command("training")
            self.protagonist.criminal_training()
        elif choice == "6":
            self._record_command("mission")
            self.protagonist.visit_mission_board(renderer=self.renderer)
        elif choice == "7":
            self._record_command("boss")
            self.protagonist.confront_dragon(self.dragon)
            self.protagonist.save_dragon(self.dragon)
            if self.protagonist.dragon_defeated:
                print("\n*** VICE CITY DRAGONS BEENDET! ***")
                print("Danke fuers Spielen dieser kriminellen Saga!")
                return False
        elif choice == "8":
            self._record_command("clear")
            self.protagonist.text_display.toggle_clear_screen()
        elif choice == "9":
            self._record_command("save")
            self.protagonist.save_game()
            self.protagonist.save_dragon(self.dragon)
        elif choice == "10":
            self._record_command("exit")
            save_choice = input("Moechtest du vor dem Beenden speichern? (j/n) ")
            if save_choice.lower() == "j":
                self.protagonist.save_game()
                self.protagonist.save_dragon(self.dragon)
            print("Auf Wiedersehen, Krimineller!")
            return False
        elif choice == "h":
            self._record_command("hints")
            hints = self.protagonist.hint_system.get_contextual_hints(self.protagonist)
            if hints:
                for hint in hints:
                    self.protagonist.hint_system.show_hint(hint)
            else:
                print("\n[INFO] Keine Hinweise verfügbar.")
        elif choice == "t":
            self._record_command("tutorial")
            self.protagonist.hint_system.enable_tutorial_mode()
            print("\n[TUTORIAL] Tutorial-Modus aktiviert!")
        else:
            self._record_command("invalid")
            print("Ungültige Wahl, bitte versuche es erneut.")
        return True

    def get_menu_display(self) -> str:
        base_menu = """[AKTIONEN] Was moechtest du tun?

  1. Attribute anzeigen
  2. Ausruhen
  3. Erkunden
  4. Schwarzmarkt besuchen
  5. Kriminelles Training
  6. Missionsbrett
  7. Den Drachen konfrontieren
  8. Bildschirm-Loeschung umschalten
  9. Spielstand speichern
  10. Spiel beenden"""

        if hasattr(self.protagonist, 'hint_system') and self.protagonist.hint_system.tutorial_mode:
            base_menu += """
  h. Hinweise anzeigen
  t. Tutorial-Modus"""

        return base_menu