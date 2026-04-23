import time as time_module

from src.game.renderer import GameRenderer
from src.game.session import GameSession
from src.telemetry import initialize_telemetry, shutdown_telemetry
from src.telemetry import metrics as telemetrics
from src.telemetry import settings as teleSettings
from src.telemetry.logging import get_logger

_telemetry_logger = get_logger(__name__)


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


def _handle_telemetry_menu():
    settings = teleSettings.load_user_settings()
    enabled = settings.get("telemetry_enabled", True)
    log_enabled = settings.get("logging_enabled", True)
    log_level = settings.get("log_level", "INFO")

    print("\n[TELEMETRIE] Einstellungen:")
    print(f"1) Telemetrie aktiviert:  {'Ja' if enabled else 'Nein'}")
    print(f"2) Logging aktiviert:   {'Ja' if log_enabled else 'Nein'}")
    print(f"3) Log-Level:          {log_level}")
    print("4) Einstellungen zuruecksetzen")
    print("0) Zurueck")

    choice = input("Auswahl: ").strip()

    if choice == "1":
        new_enabled = not enabled
        teleSettings.set_telemetry_enabled(new_enabled)
        print(f"Telemetrie {'aktiviert' if new_enabled else 'deaktiviert'}.")
    elif choice == "2":
        new_log_enabled = not log_enabled
        teleSettings.set_logging_enabled(new_log_enabled)
        print(f"Logging {'aktiviert' if new_log_enabled else 'deaktiviert'}.")
    elif choice == "3":
        print("\nLog-Level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
        level_input = input("Neuer Level: ").strip().upper()
        if level_input in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            teleSettings.set_log_level(level_input)
            print(f"Log-Level auf {level_input} gesetzt.")
        else:
            print("Ungueltiger Level, keine Aenderung.")
    elif choice == "4":
        teleSettings.reset_settings()
        print("Einstellungen zurueckgesetzt.")
    elif choice == "0":
        return
    else:
        print("Ungueltige Wahl.")


def main():
    initialize_telemetry()

    renderer = GameRenderer()
    session = GameSession(renderer=renderer)

    renderer.render_start_menu()
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
        from src.characters.protagonist import Protagonist
        from src.characters.dragon import ViceCityDragon

        protagonist = Protagonist(hero_name, "jason")
        protagonist.initialize_missions()
        dragon = ViceCityDragon()

    game_loop(protagonist, dragon)


def game_loop(protagonist, dragon):
    start_time = time_module.time()

    telemetrics.record_session_start(
        player_name=protagonist.name,
        character_type=protagonist.character_type,
    )
    telemetrics.set_player_level(protagonist.level)

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
        "13": "telem", "telem": "telem",
    }

    while True:
        print("\n=== VICE CITY HAUPTMENUE ===")
        print("1. Attribute anzeigen")
        print("2. Rasten/Unterschlupf")
        print("3. Vice City erkunden")
        print("4. Schwarzmarkt besuchen")
        print("5. Kriminelles Training")
        print("6. Mission-Brett")
        print("7. Journal & Quest-Log")
        print("8. Erfolge")
        print("9. Drachen der Konsequenzen konfrontieren")
        print("10. Bildschirm-Loeschung umschalten")
        print("11. Spiel speichern")
        print("12. Spiel beenden")
        print("13. Telemetrie-Einstellungen    (telem)")
        choice = input("Waehle eine Aktion (1-13): ")
        command = command_aliases.get(choice, None)

        if command:
            telemetrics.record_command(command)

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
            protagonist.open_journal()
        elif choice == "8":
            protagonist.display_achievements()
        elif choice == "9":
            protagonist.confront_dragon(dragon)
            protagonist.save_dragon(dragon)
            if protagonist.run_completed:
                protagonist.show_endgame_summary()
                if protagonist.ng_plus_unlocked:
                    replay_choice = input("\nMoechtest du New Game+ starten? (j/n) ")
                    if replay_choice.lower() == "j":
                        if protagonist.start_new_game_plus():
                            dragon = ViceCityDragon()
                            protagonist.save_dragon(dragon)
                            continue
                print("\n*** VICE CITY DRAGONS BEENDET! ***")
                print("Danke fuers Spielen dieser kriminellen Saga!")
                duration = time_module.time() - start_time
                telemetrics.record_session_duration(duration)
                shutdown_telemetry()
                break
        elif choice == "10":
            protagonist.text_display.toggle_clear_screen()
        elif choice == "11":
            protagonist.save_game()
            protagonist.save_dragon(dragon)
        elif choice == "12":
            save_choice = input("Moechtest du vor dem Beenden speichern? (j/n) ")
            if save_choice.lower() == "j":
                protagonist.save_game()
                protagonist.save_dragon(dragon)
            duration = time_module.time() - start_time
            telemetrics.record_session_duration(duration)
            print("Auf Wiedersehen, Krimineller!")
            shutdown_telemetry()
            break
        elif choice == "13":
            _handle_telemetry_menu()
        else:
            print("Ungueltige Wahl, bitte versuche es erneut.")


if __name__ == "__main__":
    main()
