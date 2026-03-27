import json
import os
import tempfile
import unittest

from src.characters.protagonist import Protagonist


class SaveLoadDistrictReputationTests(unittest.TestCase):
    def test_save_and_load_persists_district_reputation(self):
        hero = Protagonist("Test", "jason")
        hero.district_manager.districts["Ocean Beach"].reputation = 25
        hero.district_manager.districts["Viceport"].reputation = -15

        with tempfile.TemporaryDirectory() as tmp:
            save_file = os.path.join(tmp, "save.json")
            hero.save_game(save_file)

            loaded_hero = Protagonist("", "jason")
            loaded = loaded_hero.load_game(save_file)

            self.assertTrue(loaded)
            self.assertEqual(25, loaded_hero.district_manager.districts["Ocean Beach"].reputation)
            self.assertEqual(-15, loaded_hero.district_manager.districts["Viceport"].reputation)

    def test_load_defaults_district_reputation_when_missing_in_save(self):
        hero = Protagonist("Legacy", "jason")

        with tempfile.TemporaryDirectory() as tmp:
            save_file = os.path.join(tmp, "save_legacy.json")
            hero.save_game(save_file)

            with open(save_file, "r", encoding="utf-8") as f:
                save_data = json.load(f)
            save_data.pop("district_reputations", None)
            with open(save_file, "w", encoding="utf-8") as f:
                json.dump(save_data, f)

            loaded_hero = Protagonist("", "jason")
            loaded = loaded_hero.load_game(save_file)

            self.assertTrue(loaded)
            for district in loaded_hero.district_manager.districts.values():
                self.assertEqual(0, district.reputation)


if __name__ == "__main__":
    unittest.main()
