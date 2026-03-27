from src.characters.protagonist import Protagonist
from src.characters.dragon import ViceCityDragon


def main():
    print("=== WILLKOMMEN IN VICE CITY DRAGONS! ===")
    print("Ein kriminelles Abenteuer inspiriert von GTA 6")
    print("1. Neues Spiel starten")
    print("2. Spiel laden")
    choice = input("Waehle eine Option (1-2): ")
    
    if choice == "1":
        print("\nWaehle deinen Protagonisten:")
        print("1. Jason Duval (Ex-Militaer, gute Kampffaehigkeiten)")
        print("2. Lucia Caminos (Frueher aus dem Gefaengnis, gute Stealth-Faehigkeiten)")
        
        protagonist_choice = input("Waehle deinen Charakter (1-2): ")
        if protagonist_choice == "1":
            character_type = "jason"
        elif protagonist_choice == "2":
            character_type = "lucia"
        else:
            print("Standardwahl: Jason")
            character_type = "jason"
        
        hero_name = input(f"Gib den Namen deines {character_type.title()} ein: ")
        protagonist = Protagonist(hero_name, character_type)
        protagonist.initialize_missions()
        dragon = ViceCityDragon()
        
        print(f"\nKAPITEL 1: DER ANFANG")
        chapter_info = protagonist.story_manager.get_chapter_story(1)
        protagonist.text_display.display_progressive(chapter_info['opening'])
        protagonist.text_display.display_progressive(chapter_info['motivation'][character_type])
        print("\n[MISSION] NEUE FUNKTION: Mission-Brett im Hauptmenü verfügbar!")
            
    elif choice == "2":
        protagonist = Protagonist("", "jason")
        if protagonist.load_game():
            protagonist.initialize_missions()
            for mission_name, mission in protagonist.mission_manager.all_missions.items():
                if mission_name in protagonist.story_flags.get("completed_missions", []):
                    mission.completed = True
                if mission_name in protagonist.story_flags.get("available_missions", []):
                    mission.available = True
            
            dragon = protagonist.load_dragon()
            print(f"\nWillkommen zurueck, {protagonist.name}!")
            chapter_info = protagonist.story_manager.get_chapter_story(protagonist.chapter)
            print(f"Kapitel {protagonist.chapter}: {chapter_info['title']}")
            protagonist.text_display.display_progressive(chapter_info['opening'])
        else:
            print("Kein gueltiger Speicherstand gefunden. Neues Spiel wird gestartet.")
            hero_name = input("Gib den Namen deines Helden ein: ")
            protagonist = Protagonist(hero_name, "jason")
            protagonist.initialize_missions()
            dragon = ViceCityDragon()
    else:
        print("Ungueltige Wahl! Neues Spiel wird gestartet.")
        hero_name = input("Gib den Namen deines Helden ein: ")
        protagonist = Protagonist(hero_name, "jason")
        protagonist.initialize_missions()
        dragon = ViceCityDragon()
    
    game_loop(protagonist, dragon)


def game_loop(protagonist, dragon):
    while True:
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
        choice = input("Waehle eine Aktion (1-10): ")
        
        if choice == "1":
            protagonist.display_attributes()
        elif choice == "2":
            protagonist.rest()
        elif choice == "3":
            protagonist.explore_vice_city()
        elif choice == "4":
            protagonist.visit_black_market()
        elif choice == "5":
            protagonist.criminal_training()
        elif choice == "6":
            protagonist.visit_mission_board()
        elif choice == "7":
            protagonist.confront_dragon(dragon)
            protagonist.save_dragon(dragon)
            if protagonist.dragon_defeated:
                print("\n*** VICE CITY DRAGONS BEENDET! ***")
                print("Danke fuers Spielen dieser kriminellen Saga!")
                break
        elif choice == "8":
            protagonist.text_display.toggle_clear_screen()
        elif choice == "9":
            protagonist.save_game()
            protagonist.save_dragon(dragon)
        elif choice == "10":
            save_choice = input("Moechtest du vor dem Beenden speichern? (j/n) ")
            if save_choice.lower() == "j":
                protagonist.save_game()
                protagonist.save_dragon(dragon)
            print("Auf Wiedersehen, Krimineller!")
            break
        else:
            print("Ungültige Wahl, bitte versuche es erneut.")


if __name__ == "__main__":
    main()
