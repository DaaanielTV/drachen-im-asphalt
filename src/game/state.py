from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from src.time.day_night_cycle import DayNightCycle


DEFAULT_STORY_FLAGS = {
    "first_crime_committed": False,
    "first_dragon_seen": False,
    "partner_betrayed": False,
    "redemption_offered": False,
    "first_mission_completed": False,
}


@dataclass
class GameState:
    name: str
    character_type: str
    cash: int
    level: int
    inventory: list[dict[str, Any]] = field(default_factory=list)
    stamina: int = 30
    days: int = 0
    wanted_level: int = 0
    reputation: int = 0
    drug_effects: list[dict[str, Any]] = field(default_factory=list)
    dragon_encounters: int = 0
    chapter: int = 1
    partner_trust: int = 100
    ankle_monitor: bool = False
    combat_skill: int = 10
    stealth: int = 10
    dragon_defeated: bool = False
    story_flags: dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_STORY_FLAGS))
    clear_screen_enabled: bool = False
    time_cycle: dict[str, Any] = field(default_factory=lambda: DayNightCycle().to_dict())
    achievements: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw_data: dict[str, Any]) -> "GameState":
        flags = dict(DEFAULT_STORY_FLAGS)
        flags.update(raw_data.get("story_flags", {}))

        return cls(
            name=raw_data["name"],
            character_type=raw_data["character_type"],
            cash=raw_data["cash"],
            level=raw_data["level"],
            inventory=raw_data.get("inventory", []),
            stamina=raw_data["stamina"],
            days=raw_data["days"],
            wanted_level=raw_data["wanted_level"],
            reputation=raw_data["reputation"],
            drug_effects=raw_data.get("drug_effects", []),
            dragon_encounters=raw_data["dragon_encounters"],
            chapter=raw_data["chapter"],
            partner_trust=raw_data["partner_trust"],
            ankle_monitor=raw_data["ankle_monitor"],
            combat_skill=raw_data["combat_skill"],
            stealth=raw_data["stealth"],
            dragon_defeated=raw_data.get("dragon_defeated", False),
            story_flags=flags,
            clear_screen_enabled=raw_data.get("clear_screen_enabled", False),
            time_cycle=raw_data.get("time_cycle", DayNightCycle().to_dict()),
            achievements=raw_data.get("achievements", {}),
        )

    @classmethod
    def from_protagonist(cls, protagonist: Any) -> "GameState":
        return cls(
            name=protagonist.name,
            character_type=protagonist.character_type,
            cash=protagonist.cash,
            level=protagonist.level,
            inventory=[item.__dict__ for item in protagonist.inventory],
            stamina=protagonist.stamina,
            days=protagonist.days,
            wanted_level=protagonist.wanted_level,
            reputation=protagonist.reputation,
            drug_effects=[effect.__dict__ for effect in protagonist.drug_effects],
            dragon_encounters=protagonist.dragon_encounters,
            chapter=protagonist.chapter,
            partner_trust=protagonist.partner_trust,
            ankle_monitor=protagonist.ankle_monitor,
            combat_skill=protagonist.combat_skill,
            stealth=protagonist.stealth,
            dragon_defeated=getattr(protagonist, "dragon_defeated", False),
            story_flags=dict(protagonist.story_flags),
            clear_screen_enabled=protagonist.text_display.clear_screen_enabled,
            time_cycle=protagonist.district_manager.time_cycle.to_dict(),
            achievements=protagonist.achievement_manager.to_dict(),
        )
