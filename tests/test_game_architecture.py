import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from src.characters.dragon import ViceCityDragon
from src.characters.protagonist import Protagonist
from src.game.commands import GameCommandHandler
from src.game.mission_logic import MissionBoardService
from src.game.persistence import GamePersistence
from src.game.state import GameState
from src.items.weapon import Weapon


class GameStateTests(unittest.TestCase):
    def test_game_state_roundtrip_dict(self):
        state = GameState(
            name="Test",
            character_type="jason",
            cash=900,
            level=2,
            stamina=40,
            days=1,
            wanted_level=3,
            reputation=7,
            dragon_encounters=2,
            chapter=2,
            partner_trust=80,
            ankle_monitor=False,
            combat_skill=20,
            stealth=11,
            story_flags={"first_crime_committed": True},
        )

        payload = state.to_dict()
        loaded = GameState.from_dict(payload)

        self.assertEqual(loaded.name, "Test")
        self.assertTrue(loaded.story_flags["first_crime_committed"])
        self.assertIn("first_dragon_seen", loaded.story_flags)


class GamePersistenceTests(unittest.TestCase):
    def test_save_and_load_protagonist(self):
        persistence = GamePersistence()
        protagonist = Protagonist("Alex", "jason")
        protagonist.inventory = [Weapon("Messer", 100, 5, 2)]
        protagonist.cash = 1111
        protagonist.story_flags["first_crime_committed"] = True

        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = Path(temp_dir) / "savegame.json"
            persistence.save_protagonist(protagonist, str(save_path))

            loaded = Protagonist("", "jason")
            persistence.load_protagonist(loaded, str(save_path))

            self.assertEqual(loaded.name, "Alex")
            self.assertEqual(loaded.cash, 1111)
            self.assertEqual(loaded.inventory[0].name, "Messer")
            self.assertTrue(loaded.story_flags["first_crime_committed"])

    def test_save_and_load_dragon(self):
        persistence = GamePersistence()
        dragon = ViceCityDragon()
        dragon.stamina = 77
        dragon.defeated = True

        with tempfile.TemporaryDirectory() as temp_dir:
            dragon_path = Path(temp_dir) / "dragon.json"
            persistence.save_dragon(dragon, str(dragon_path))
            loaded = persistence.load_dragon(str(dragon_path))

            self.assertEqual(loaded.stamina, 77)
            self.assertTrue(loaded.defeated)


class MissionBoardServiceTests(unittest.TestCase):
    def test_select_mission_by_index(self):
        mission_manager = Mock()
        service = MissionBoardService(mission_manager)
        missions = [Mock(name="m1"), Mock(name="m2")]

        self.assertIsNotNone(service.select_mission(missions, 0))
        self.assertIsNone(service.select_mission(missions, 4))


class GameCommandHandlerTests(unittest.TestCase):
    def test_invalid_command_keeps_game_running(self):
        protagonist = Mock()
        dragon = Mock()
        renderer = Mock()
        handler = GameCommandHandler(protagonist, dragon, renderer)

        still_running = handler.execute("unbekannt")

        self.assertTrue(still_running)


if __name__ == "__main__":
    unittest.main()
