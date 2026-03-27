from __future__ import annotations


class GameCommandHandler:
    def __init__(self, protagonist, dragon, renderer):
        self.protagonist = protagonist
        self.dragon = dragon
        self.renderer = renderer

    def execute(self, choice: str) -> bool:
        if choice == "1":
            self.protagonist.display_attributes()
        elif choice == "2":
            self.protagonist.rest()
        elif choice == "3":
            self.protagonist.explore_vice_city()
        elif choice == "4":
            self.protagonist.visit_black_market()
        elif choice == "5":
            self.protagonist.criminal_training()
        elif choice == "6":
            self.protagonist.visit_mission_board(renderer=self.renderer)
        elif choice == "7":
            self.protagonist.confront_dragon(self.dragon)
            self.protagonist.save_dragon(self.dragon)
            if self.protagonist.dragon_defeated:
                print("\n*** VICE CITY DRAGONS BEENDET! ***")
                print("Danke fuers Spielen dieser kriminellen Saga!")
                return False
        elif choice == "8":
            self.protagonist.text_display.toggle_clear_screen()
        elif choice == "9":
            self.protagonist.save_game()
            self.protagonist.save_dragon(self.dragon)
        elif choice == "10":
            save_choice = input("Moechtest du vor dem Beenden speichern? (j/n) ")
            if save_choice.lower() == "j":
                self.protagonist.save_game()
                self.protagonist.save_dragon(self.dragon)
            print("Auf Wiedersehen, Krimineller!")
            return False
        else:
            print("Ungültige Wahl, bitte versuche es erneut.")
        return True
