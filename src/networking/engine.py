from dataclasses import dataclass, field
from typing import Any
from src.game.state import GameState
from src.characters.protagonist import Protagonist
from src.characters.dragon import ViceCityDragon
from src.ui.text_display import TextDisplayManager


@dataclass
class CommandResult:
    success: bool
    message: str
    game_state: dict | None = None
    updates: dict = field(default_factory=dict)


class GameEngine:
    def __init__(self):
        self.protagonist: Protagonist | None = None
        self.dragon: ViceCityDragon | None = None
        self.text_display = TextDisplayManager()
        self.text_display.display_mode = "instant"

    def create_character(self, name: str, character_type: str) -> CommandResult:
        if character_type not in ("jason", "lucia"):
            return CommandResult(False, "Ungueltiger Charaktertyp. Waehle jason oder lucia.")

        self.protagonist = Protagonist(name, character_type)
        self.protagonist.initialize_missions()
        self.dragon = ViceCityDragon()

        state = self._capture_state()
        return CommandResult(
            success=True,
            message=f"Charakter {name} ({character_type}) erstellt.",
            game_state=state,
            updates={"type": "new_character", "name": name, "character_type": character_type}
        )

    def execute_command(self, command: str, **kwargs) -> CommandResult:
        if not self.protagonist:
            return CommandResult(False, "Kein Charakter erstellt.")

        command_handlers = {
            "explore": self._handle_explore,
            "rest": self._handle_rest,
            "status": self._handle_status,
            "inventory": self._handle_inventory,
            "mission": self._handle_mission,
            "mission_board": self._handle_mission_board,
            "achievements": self._handle_achievements,
            "chapter": self._handle_chapter,
            "settings": self._handle_settings,
            "quit": self._handle_quit,
            "help": self._handle_help,
        }

        handler = command_handlers.get(command)
        if not handler:
            return CommandResult(False, f"Unbekannter Befehl: {command}")

        return handler(**kwargs)

    def _handle_explore(self, district_name: str | None = None) -> CommandResult:
        if not self.protagonist:
            return CommandResult(False, "Kein Charakter erstellt.")

        if district_name:
            if district_name in self.protagonist.district_manager.districts:
                district = self.protagonist.district_manager.districts[district_name]
                self.protagonist.explore_district(district)
            else:
                return CommandResult(False, f"Stadtteil nicht gefunden: {district_name}")
        else:
            self.protagonist.explore_vice_city()

        return CommandResult(
            success=True,
            message="Erkundung abgeschlossen.",
            game_state=self._capture_state()
        )

    def _handle_rest(self, location: str = "sicherer Unterschlupf") -> CommandResult:
        if not self.protagonist:
            return CommandResult(False, "Kein Charakter erstellt.")

        self.protagonist.rest(location)
        return CommandResult(
            success=True,
            message="Ausgeruht. Ausdauer wiederhergestellt.",
            game_state=self._capture_state()
        )

    def _handle_status(self) -> CommandResult:
        if not self.protagonist:
            return CommandResult(False, "Kein Charakter erstellt.")

        self.protagonist.display_attributes()
        return CommandResult(
            success=True,
            message="Status angezeigt.",
            game_state=self._capture_state()
        )

    def _handle_inventory(self) -> CommandResult:
        if not self.protagonist:
            return CommandResult(False, "Kein Charakter erstellt.")

        items = [item.name for item in self.protagonist.inventory]
        return CommandResult(
            success=True,
            message=f"Inventar: {items if items else 'Leer'}",
            game_state=self._capture_state()
        )

    def _handle_mission(self, mission_name: str | None = None) -> CommandResult:
        if not self.protagonist:
            return CommandResult(False, "Kein Charakter erstellt.")

        if mission_name:
            mission = self.protagonist.mission_manager.all_missions.get(mission_name)
            if not mission:
                return CommandResult(False, f"Mission nicht gefunden: {mission_name}")
            self.protagonist.mission_board.start_mission(mission_name)
        else:
            self.protagonist.mission_board.show_available_missions()

        return CommandResult(
            success=True,
            message="Mission abgeschlossen.",
            game_state=self._capture_state()
        )

    def _handle_mission_board(self) -> CommandResult:
        if not self.protagonist:
            return CommandResult(False, "Kein Charakter erstellt.")

        self.protagonist.mission_board.show_available_missions()
        return CommandResult(
            success=True,
            message="Mission-Brett angezeigt.",
            game_state=self._capture_state()
        )

    def _handle_achievements(self) -> CommandResult:
        if not self.protagonist:
            return CommandResult(False, "Kein Charakter erstellt.")

        self.protagonist.display_achievements()
        return CommandResult(
            success=True,
            message="Erfolge angezeigt.",
            game_state=self._capture_state()
        )

    def _handle_chapter(self) -> CommandResult:
        if not self.protagonist:
            return CommandResult(False, "Kein Charakter erstellt.")

        chapter = self.protagonist.chapter
        chapter_info = self.protagonist.story_manager.get_chapter_story(chapter)
        message = f"Kapitel {chapter}: {chapter_info['title']}"
        return CommandResult(
            success=True,
            message=message,
            game_state=self._capture_state()
        )

    def _handle_settings(self, mode: str | None = None) -> CommandResult:
        if not self.protagonist:
            return CommandResult(False, "Kein Charakter erstellt.")

        if mode:
            self.protagonist.text_display.set_display_mode(mode)
        return CommandResult(
            success=True,
            message="Einstellungen angezeigt.",
            game_state=self._capture_state()
        )

    def _handle_quit(self) -> CommandResult:
        return CommandResult(
            success=True,
            message="Spiel beendet.",
            game_state=self._capture_state(),
            updates={"type": "quit"}
        )

    def _handle_help(self) -> CommandResult:
        help_text = (
            "Befehle:\n"
            "  explore [stadtteil] - Stadt erkunden oder bestimmten Stadtteil\n"
            "  rest - Ausruhen und Ausdauer regenerieren\n"
            "  status - Charakterstatus anzeigen\n"
            "  inventory - Inventar anzeigen\n"
            "  mission [name] - Mission starten oder anzeigen\n"
            "  mission_board - verfügbare Missionen anzeigen\n"
            "  achievements - Erfolge anzeigen\n"
            "  chapter - aktuelles Kapitel anzeigen\n"
            "  settings [modus] - Textmodus setzen\n"
            "  quit - Spiel beenden\n"
            "  help - diese Hilfe anzeigen"
        )
        return CommandResult(success=True, message=help_text)

    def _capture_state(self) -> dict[str, Any]:
        if not self.protagonist:
            return {}

        return {
            "name": self.protagonist.name,
            "character_type": self.protagonist.character_type,
            "cash": self.protagonist.cash,
            "level": self.protagonist.level,
            "stamina": self.protagonist.stamina,
            "days": self.protagonist.days,
            "wanted_level": self.protagonist.wanted_level,
            "reputation": self.protagonist.reputation,
            "chapter": self.protagonist.chapter,
            "current_district": self.protagonist.current_district_context,
            "inventory": [item.name for item in self.protagonist.inventory],
            "time": self.protagonist.district_manager.get_time_display(),
            "story_flags": dict(self.protagonist.story_flags),
            "achievements": self.protagonist.achievement_manager.to_dict(),
        }

    def get_state(self) -> dict[str, Any]:
        return self._capture_state()

    def load_state(self, state: dict[str, Any]) -> bool:
        try:
            game_state = GameState.from_dict(state)
            self.protagonist = Protagonist(game_state.name, game_state.character_type)
            self.protagonist.cash = game_state.cash
            self.protagonist.level = game_state.level
            self.protagonist.stamina = game_state.stamina
            self.protagonist.days = game_state.days
            self.protagonist.wanted_level = game_state.wanted_level
            self.protagonist.reputation = game_state.reputation
            self.protagonist.chapter = game_state.chapter
            self.protagonist.story_flags = game_state.story_flags
            self.dragon = ViceCityDragon()
            self.protagonist.initialize_missions()
            return True
        except Exception as e:
            return False