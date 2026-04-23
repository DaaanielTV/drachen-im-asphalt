from __future__ import annotations

import time as time_module

from src.characters.dragon import ViceCityDragon
from src.characters.protagonist import Protagonist
from src.game.commands import GameCommandHandler
from src.game.renderer import GameRenderer
from src.telemetry import metrics as telemetrics
from src.telemetry import settings as teleSettings


class GameSession:
    def __init__(self, renderer=None):
        self.renderer = renderer or GameRenderer()
        self.start_time = None

    def build_new_game(self):
        self.renderer.render_character_menu()
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
        protagonist.text_display.display_progressive(chapter_info["opening"])
        protagonist.text_display.display_progressive(chapter_info["motivation"][character_type])
        print("\n[MISSION] NEUE FUNKTION: Mission-Brett im Hauptmenü verfügbar!")
        return protagonist, dragon

    def build_loaded_game(self):
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
            protagonist.text_display.display_progressive(chapter_info["opening"])
            if teleSettings.get_telemetry_enabled():
                telemetrics.record_load(protagonist.name)
            return protagonist, dragon

        print("Kein gueltiger Speicherstand gefunden. Neues Spiel wird gestartet.")
        hero_name = input("Gib den Namen deines Helden ein: ")
        protagonist = Protagonist(hero_name, "jason")
        protagonist.initialize_missions()
        return protagonist, ViceCityDragon()

    def game_loop(self, protagonist, dragon):
        self.start_time = time_module.time()
        if teleSettings.get_telemetry_enabled():
            telemetrics.record_session_start(
                player_name=protagonist.name,
                character_type=protagonist.character_type,
            )
            telemetrics.set_player_level(protagonist.level)

        handler = GameCommandHandler(protagonist, dragon, self.renderer)
        running = True
        while running:
            self.renderer.render_main_menu()
            choice = input("Waehle eine Aktion (1-10): ")
            running = handler.execute(choice)

        if self.start_time and teleSettings.get_telemetry_enabled():
            duration = time_module.time() - self.start_time
            telemetrics.record_session_duration(duration)
