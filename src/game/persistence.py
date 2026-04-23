from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime

from src.characters.dragon import ViceCityDragon
from src.effects.drug_effect import DrugEffect
from src.game.state import GameState
from src.items.weapon import Weapon


SAVE_DIRECTORY = "data/saves"
MAX_SAVE_SLOTS = 10


@dataclass
class SaveSlot:
    slot_id: int
    name: str
    character_name: str
    character_type: str
    level: int
    chapter: int
    days: int
    cash: int
    created_at: str
    modified_at: str
    game_mode: str = "standard"
    permadeath: bool = False
    completed: bool = False

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SaveSlot":
        return cls(**data)


class SaveSlotManager:
    def __init__(self, save_dir: str = SAVE_DIRECTORY):
        self.save_dir = Path(save_dir)
        self.slots_file = self.save_dir / "slots.json"
        self._ensure_save_directory()

    def _ensure_save_directory(self) -> None:
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def _get_slot_filename(self, slot_id: int) -> str:
        return str(self.save_dir / f"slot_{slot_id}.json")

    def get_all_slots(self) -> list[SaveSlot]:
        if not self.slots_file.exists():
            return []

        with open(self.slots_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [SaveSlot.from_dict(slot) for slot in data.get("slots", [])]

    def _save_slots_registry(self, slots: list[SaveSlot]) -> None:
        with open(self.slots_file, "w", encoding="utf-8") as f:
            json.dump({"slots": [s.to_dict() for s in slots]}, f, ensure_ascii=False, indent=2)

    def get_slot_info(self, slot_id: int) -> SaveSlot | None:
        slots = self.get_all_slots()
        for slot in slots:
            if slot.slot_id == slot_id:
                return slot
        return None

    def create_slot(self, slot_id: int, protagonist) -> SaveSlot:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return SaveSlot(
            slot_id=slot_id,
            name=f"Spielstand {slot_id}",
            character_name=protagonist.name,
            character_type=protagonist.character_type,
            level=protagonist.level,
            chapter=protagonist.chapter,
            days=protagonist.days,
            cash=protagonist.cash,
            created_at=now,
            modified_at=now,
            game_mode=getattr(protagonist, 'game_mode', 'standard'),
            permadeath=getattr(protagonist, 'permadeath', False),
            completed=protagonist.dragon_defeated
        )

    def update_slot_info(self, slot: SaveSlot, protagonist) -> SaveSlot:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        slot.character_name = protagonist.name
        slot.character_type = protagonist.character_type
        slot.level = protagonist.level
        slot.chapter = protagonist.chapter
        slot.days = protagonist.days
        slot.cash = protagonist.cash
        slot.modified_at = now
        slot.game_mode = getattr(protagonist, 'game_mode', 'standard')
        slot.permadeath = getattr(protagonist, 'permadeath', False)
        slot.completed = protagonist.dragon_defeated
        return slot


class MultiSavePersistence:
    def __init__(self, save_dir: str = SAVE_DIRECTORY):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.slot_manager = SaveSlotManager(save_dir)

    def save_game(self, protagonist, slot_id: int = 1) -> bool:
        filename = self.slot_manager._get_slot_filename(slot_id)
        state = GameState.from_protagonist(protagonist)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, ensure_ascii=False, indent=2)

        slot = self.slot_manager.get_slot_info(slot_id)
        if slot:
            self.slot_manager.update_slot_info(slot, protagonist)
        else:
            slot = self.slot_manager.create_slot(slot_id, protagonist)

        slots = self.slot_manager.get_all_slots()
        existing_idx = None
        for i, s in enumerate(slots):
            if s.slot_id == slot_id:
                existing_idx = i
                break

        if existing_idx is not None:
            slots[existing_idx] = slot
        else:
            slots.append(slot)

        self.slot_manager._save_slots_registry(slots)
        return True

    def load_game(self, slot_id: int = 1, protagonist=None):
        filename = self.slot_manager._get_slot_filename(slot_id)
        if not os.path.exists(filename):
            return None

        with open(filename, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        if protagonist is None:
            from src.characters.protagonist import Protagonist
            raw_data["name"] = raw_data.get("name", "Player")
            raw_data["character_type"] = raw_data.get("character_type", "jason")
            protagonist = Protagonist(raw_data["name"], raw_data["character_type"])

        state = GameState.from_dict(raw_data)
        self._apply_state_to_protagonist(state, protagonist)
        return protagonist

    def _apply_state_to_protagonist(self, state: GameState, protagonist) -> None:
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
        protagonist.achievement_manager.load_from_dict(state.achievements)

    def delete_save(self, slot_id: int) -> bool:
        filename = self.slot_manager._get_slot_filename(slot_id)
        if os.path.exists(filename):
            os.remove(filename)

        slots = self.slot_manager.get_all_slots()
        slots = [s for s in slots if s.slot_id != slot_id]
        self.slot_manager._save_slots_registry(slots)
        return True

    def list_saves(self) -> list[SaveSlot]:
        return self.slot_manager.get_all_slots()

    def has_save(self, slot_id: int) -> bool:
        filename = self.slot_manager._get_slot_filename(slot_id)
        return os.path.exists(filename)


class GamePersistence:
    def __init__(self):
        self.multi_save = MultiSavePersistence()

    def save_protagonist(self, protagonist, filename: str = "data/saves/savegame.json") -> bool:
        state = GameState.from_protagonist(protagonist)
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as handle:
            json.dump(state.to_dict(), handle, ensure_ascii=False, indent=2)
        return True

    def load_protagonist(self, protagonist, filename: str = "data/saves/savegame.json") -> bool:
        with open(filename, "r", encoding="utf-8") as handle:
            raw_data = json.load(handle)

        state = GameState.from_dict(raw_data)
        multi_save = MultiSavePersistence()
        multi_save._apply_state_to_protagonist(state, protagonist)
        return True

    def save_dragon(self, dragon: ViceCityDragon, filename: str = "data/dragon.json") -> bool:
        state = {
            "stamina": dragon.stamina,
            "defeated": dragon.defeated,
            "manifestation": dragon.manifestation,
        }
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as handle:
            json.dump(state, handle, ensure_ascii=False, indent=2)
        return True

    def load_dragon(self, filename: str = "data/dragon.json") -> ViceCityDragon:
        with open(filename, "r", encoding="utf-8") as handle:
            raw_data = json.load(handle)

        dragon = ViceCityDragon()
        dragon.stamina = raw_data["stamina"]
        dragon.defeated = raw_data["defeated"]
        dragon.manifestation = raw_data.get("manifestation", "metaphorisch")
        return dragon

    def save_to_slot(self, protagonist, slot_id: int = 1) -> bool:
        return self.multi_save.save_game(protagonist, slot_id)

    def load_from_slot(self, slot_id: int = 1, protagonist=None):
        return self.multi_save.load_game(slot_id, protagonist)