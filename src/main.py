from src.characters.protagonist import Protagonist
from src.characters.dragon import ViceCityDragon


def show_main_help(protagonist):
    print("\n=== HILFE / STEUERUNG ===")
    print("Dieses Spiel ist komplett textbasiert.")
    print("Tipps fuer schnelleres Spielen:")
    print("- In Story-Texten: Enter = weiter, s = Rest ueberspringen, i = sofort anzeigen")
    print("- Menues akzeptieren die Nummer oder den Kurzbefehl in Klammern")
    print("- Nutze den Lesemodus fuer kuerzere oder ausfuehrlichere Textabschnitte")
    print()
    print(protagonist.text_display.get_controls_help())


def _snapshot_player_state(protagonist):
    return {
        "cash": protagonist.cash,
        "level": protagonist.level,
        "stamina": protagonist.stamina,
        "wanted_level": protagonist.wanted_level,
        "reputation": protagonist.reputation,
        "days": protagonist.days,
        "partner_trust": protagonist.partner_trust,
        "dragon_encounters": protagonist.dragon_encounters,
    }


def _print_state_change_feedback(before, after):
    tracked_stats = {
        "cash": "Cash",
        "level": "Level",
        "stamina": "Ausdauer",
        "wanted_level": "Wanted",
        "reputation": "Reputation",
        "days": "Tage",
        "partner_trust": "Partner-Vertrauen",
        "dragon_encounters": "Drachen-Begegnungen",
    }

    changes = []
    for key, label in tracked_stats.items():
        delta = after[key] - before[key]
        if delta == 0:
            continue
        prefix = "+" if delta > 0 else ""
        changes.append(f"{label}: {before[key]} -> {after[key]} ({prefix}{delta})")

    if changes:
        print("\n[STATUS-UPDATE] Veraenderungen seit deiner letzten Aktion:")
        for change in changes:
            print(f"- {change}")


def _print_menu():
    print("\n=== VICE CITY HAUPTMENUE ===")
    print("Charakter")
    print("  1) Attribute anzeigen           (attr)")
    print("  2) Rasten / Unterschlupf        (rest)")
    print("Aktionen")
    print("  3) Vice City erkunden           (erk)")
    print("  4) Schwarzmarkt besuchen        (markt)")
    print("  5) Kriminelles Training         (train)")
    print("  6) Mission-Brett                (mission)")
    print("Fortschritt")
    print("  7) Drachen konfrontieren        (boss)")
    print("Anzeige & System")
    print("  8) Bildschirm-Loeschung an/aus  (clear)")
    print("  9) Lesemodus waehlen            (lesen)")
    print(" 10) Hilfe anzeigen               (hilfe)")
    print(" 11) Spiel speichern              (save)")
    print(" 12) Spiel beenden                (exit)")


def _handle_readability_menu(protagonist):
    print("\n[TEXT] Lesemodus waehlen:")
    print("1) schnell   - laengere Abschnitte, weniger Unterbrechungen")
    print("2) standard  - ausgeglichen")
    print("3) fokussiert- kuerzere Abschnitte, mehr Leerraum")
    mode_choice = input("Auswahl (1-3): ").strip().lower()

    mapping = {
        "1": "schnell",
        "2": "standard",
        "3": "fokussiert",
        "schnell": "schnell",
        "standard": "standard",
        "fokussiert": "fokussiert",
    }

    mode = mapping.get(mode_choice)
    if not mode:
        print("Ungueltige Wahl. Lesemodus unveraendert.")
        return

    protagonist.text_display.set_readability_mode(mode)


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

        print("\nKAPITEL 1: DER ANFANG")
        chapter_info = protagonist.story_manager.get_chapter_story(1)
        protagonist.text_display.display_progressive(chapter_info['opening'])
        protagonist.text_display.display_progressive(chapter_info['motivation'][character_type])
        print("\n[MISSION] Mission-Brett im Hauptmenue verfuegbar!")

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
    command_aliases = {
        "1": "attr", "attr": "attr",
        "2": "rest", "rest": "rest",
        "3": "erk", "erk": "erk",
        "4": "markt", "markt": "markt",
        "5": "train", "train": "train",
        "6": "mission", "mission": "mission",
        "7": "boss", "boss": "boss",
        "8": "clear", "clear": "clear",
        "9": "lesen", "lesen": "lesen",
        "10": "hilfe", "hilfe": "hilfe",
        "11": "save", "save": "save",
        "12": "exit", "exit": "exit",
    }

    while True:
        _print_menu()
        raw_choice = input("Aktion waehlen (1-12 oder Alias): ").strip().lower()
        action = command_aliases.get(raw_choice)

        if not action:
            print("Ungueltige Wahl, bitte versuche es erneut.")
            continue

        state_before = _snapshot_player_state(protagonist)

        if action == "attr":
            protagonist.display_attributes()
        elif action == "rest":
            protagonist.rest()
        elif action == "erk":
            protagonist.explore_vice_city()
        elif action == "markt":
            protagonist.visit_black_market()
        elif action == "train":
            protagonist.criminal_training()
        elif action == "mission":
            protagonist.visit_mission_board()
        elif action == "boss":
            protagonist.confront_dragon(dragon)
            protagonist.save_dragon(dragon)
            if protagonist.dragon_defeated:
                print("\n*** VICE CITY DRAGONS BEENDET! ***")
                print("Danke fuers Spielen dieser kriminellen Saga!")
                break
        elif action == "clear":
            protagonist.text_display.toggle_clear_screen()
        elif action == "lesen":
            _handle_readability_menu(protagonist)
        elif action == "hilfe":
            show_main_help(protagonist)
        elif action == "save":
            protagonist.save_game()
            protagonist.save_dragon(dragon)
        elif action == "exit":
            save_choice = input("Moechtest du vor dem Beenden speichern? (j/n) ")
            if save_choice.lower() == "j":
                protagonist.save_game()
                protagonist.save_dragon(dragon)
            print("Auf Wiedersehen, Krimineller!")
            break

        state_after = _snapshot_player_state(protagonist)
        _print_state_change_feedback(state_before, state_after)


if __name__ == "__main__":
    main()
