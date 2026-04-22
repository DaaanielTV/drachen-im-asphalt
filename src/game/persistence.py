from __future__ import annotations

import json
from dataclasses import dataclass

from src.characters.dragon import ViceCityDragon
from src.effects.drug_effect import DrugEffect
from src.game.state import GameState
from src.items.weapon import Weapon


@dataclass
class DragonState:
    stamina: int
    defeated: bool
    manifestation: str

    def to_dict(self) -> dict:
        return {
            "stamina": self.stamina,
            "defeated": self.defeated,
            "manifestation": self.manifestation,
        }

    @classmethod
    def from_dragon(cls, dragon: ViceCityDragon) -> "DragonState":
        return cls(
            stamina=dragon.stamina,
            defeated=dragon.defeated,
            manifestation=dragon.manifestation,
        )


class GamePersistence:
    def save_protagonist(self, protagonist, filename: str = "data/saves/savegame.json") -> bool:
        state = GameState.from_protagonist(protagonist)
        with open(filename, "w", encoding="utf-8") as handle:
            json.dump(state.to_dict(), handle, ensure_ascii=False, indent=2)
        return True

    def load_protagonist(self, protagonist, filename: str = "data/saves/savegame.json") -> bool:
        with open(filename, "r", encoding="utf-8") as handle:
            raw_data = json.load(handle)

        state = GameState.from_dict(raw_data)
        protagonist.name = state.name
        protagonist.character_type = state.character_type
        protagonist.cash = state.cash
        protagonist.level = state.level
        protagonist.inventory = [Weapon(**item) for item in state.inventory]
        protagonist.stamina = state.stamina
        protagonist.days = state.days
        protagonist.wanted_level = state.wanted_level
        protagonist.reputation = state.reputation
        protagonist.drug_effects = [DrugEffect(**effect) for effect in state.drug_effects]
        protagonist.dragon_encounters = state.dragon_encounters
        protagonist.chapter = state.chapter
        protagonist.partner_trust = state.partner_trust
        protagonist.ankle_monitor = state.ankle_monitor
        protagonist.combat_skill = state.combat_skill
        protagonist.stealth = state.stealth
        protagonist.dragon_defeated = state.dragon_defeated
        protagonist.story_flags = state.story_flags
        protagonist.text_display.clear_screen_enabled = state.clear_screen_enabled
        protagonist.district_manager.load_from_dict(state.time_cycle)
        return True

    def save_dragon(self, dragon: ViceCityDragon, filename: str = "data/dragon.json") -> bool:
        state = DragonState.from_dragon(dragon)
        with open(filename, "w", encoding="utf-8") as handle:
            json.dump(state.to_dict(), handle, ensure_ascii=False, indent=2)
        return True

    def load_dragon(self, filename: str = "data/dragon.json") -> ViceCityDragon:
        with open(filename, "r", encoding="utf-8") as handle:
            raw_data = json.load(handle)

        dragon = ViceCityDragon()
        dragon.stamina = raw_data["stamina"]
        dragon.defeated = raw_data["defeated"]
        dragon.manifestation = raw_data.get("manifestation", "metaphorisch")
        return dragon
