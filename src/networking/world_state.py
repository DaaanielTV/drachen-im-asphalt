from dataclasses import dataclass, field
from typing import Any
import json
import time


@dataclass
class DistrictState:
    name: str
    reputation: int = 0
    danger_level: int = 0
    discovered_features: list[str] = field(default_factory=list)
    chaos_level: int = 0


@dataclass
class SharedWorldState:
    chapter: int = 1
    season: str = "normal_season"
    time_of_day: str = "day"
    police_multiplier: float = 1.0
    district_states: dict[str, DistrictState] = field(default_factory=dict)
    story_flags: dict[str, Any] = field(default_factory=dict)
    completed_missions: list[str] = field(default_factory=list)
    active_events: list[str] = field(default_factory=list)
    last_update: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chapter": self.chapter,
            "season": self.season,
            "time_of_day": self.time_of_day,
            "police_multiplier": self.police_multiplier,
            "district_states": {
                name: {
                    "name": ds.name,
                    "reputation": ds.reputation,
                    "danger_level": ds.danger_level,
                    "discovered_features": ds.discovered_features,
                    "chaos_level": ds.chaos_level,
                }
                for name, ds in self.district_states.items()
            },
            "story_flags": self.story_flags,
            "completed_missions": self.completed_missions,
            "active_events": self.active_events,
            "last_update": self.last_update,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SharedWorldState":
        district_states = {}
        for name, ds_data in data.get("district_states", {}).items():
            district_states[name] = DistrictState(
                name=ds_data["name"],
                reputation=ds_data.get("reputation", 0),
                danger_level=ds_data.get("danger_level", 0),
                discovered_features=ds_data.get("discovered_features", []),
                chaos_level=ds_data.get("chaos_level", 0),
            )

        return cls(
            chapter=data.get("chapter", 1),
            season=data.get("season", "normal_season"),
            time_of_day=data.get("time_of_day", "day"),
            police_multiplier=data.get("police_multiplier", 1.0),
            district_states=district_states,
            story_flags=data.get("story_flags", {}),
            completed_missions=data.get("completed_missions", []),
            active_events=data.get("active_events", []),
            last_update=data.get("last_update", time.time()),
        )

    def save(self, filepath: str) -> bool:
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2)
            return True
        except Exception:
            return False

    @classmethod
    def load(cls, filepath: str) -> "SharedWorldState | None":
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception:
            return None

    def update_district(self, name: str, **kwargs) -> bool:
        if name not in self.district_states:
            return False

        ds = self.district_states[name]
        if "reputation" in kwargs:
            ds.reputation = max(-100, min(100, kwargs["reputation"]))
        if "chaos_level" in kwargs:
            ds.chaos_level = max(0, min(10, kwargs["chaos_level"]))
        if "discovered_features" in kwargs:
            ds.discovered_features = kwargs["discovered_features"]

        self.last_update = time.time()
        return True

    def add_completed_mission(self, mission_name: str) -> bool:
        if mission_name not in self.completed_missions:
            self.completed_missions.append(mission_name)
            self.last_update = time.time()
            return True
        return False

    def set_story_flag(self, flag: str, value: Any) -> None:
        self.story_flags[flag] = value
        self.last_update = time.time()

    def get_changes_since(self, timestamp: float) -> dict[str, Any]:
        if self.last_update <= timestamp:
            return {}

        changes = {
            "chapter": self.chapter,
            "season": self.season,
            "time_of_day": self.time_of_day,
            "police_multiplier": self.police_multiplier,
            "completed_missions": self.completed_missions,
            "story_flags": self.story_flags,
            "active_events": self.active_events,
            "last_update": self.last_update,
        }

        district_changes = {}
        for name, ds in self.district_states.items():
            district_changes[name] = {
                "reputation": ds.reputation,
                "chaos_level": ds.chaos_level,
                "discovered_features": ds.discovered_features,
            }

        changes["district_states"] = district_changes
        return changes