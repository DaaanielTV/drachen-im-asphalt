from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class GameMode(Enum):
    STANDARD = "standard"
    PERMADEATH = "permadeath"
    SPEEDRUN = "speedrun"
    PACIFIST = "pacifist"
    CHALLENGE = "challenge"


@dataclass
class GameModeSettings:
    mode: GameMode
    permadeath_enabled: bool = False
    speedrun_timer_active: bool = False
    pacifist_mode: bool = False
    target_days: Optional[int] = None
    challenge_rules: list[str] = field(default_factory=list)
    restrictions: list[str] = field(default_factory=list)
    modifiers: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "mode": self.mode.value,
            "permadeath_enabled": self.permadeath_enabled,
            "speedrun_timer_active": self.speedrun_timer_active,
            "pacifist_mode": self.pacifist_mode,
            "target_days": self.target_days,
            "challenge_rules": self.challenge_rules,
            "restrictions": self.restrictions,
            "modifiers": self.modifiers,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GameModeSettings":
        return cls(
            mode=GameMode(data.get("mode", "standard")),
            permadeath_enabled=data.get("permadeath_enabled", False),
            speedrun_timer_active=data.get("speedrun_timer_active", False),
            pacifist_mode=data.get("pacifist_mode", False),
            target_days=data.get("target_days"),
            challenge_rules=data.get("challenge_rules", []),
            restrictions=data.get("restrictions", []),
            modifiers=data.get("modifiers", {}),
        )


@dataclass
class PermadeathMode:
    enabled: bool = False
    death_count: int = 0
    best_run_days: Optional[int] = None
    total_deaths: int = 0
    escape_attempts: int = 0
    successful_escapes: int = 0

    def start_run(self) -> None:
        self.death_count = 0
        self.escape_attempts = 0
        self.successful_escapes = 0

    def record_death(self) -> None:
        self.death_count += 1
        self.total_deaths += 1

    def record_escape(self) -> bool:
        self.escape_attempts += 1
        if self.death_count == 0:
            self.successful_escapes += 1
            return True
        return False

    def get_survival_rate(self) -> float:
        if self.escape_attempts == 0:
            return 0.0
        return self.successful_escapes / self.escape_attempts

    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "death_count": self.death_count,
            "best_run_days": self.best_run_days,
            "total_deaths": self.total_deaths,
            "escape_attempts": self.escape_attempts,
            "successful_escapes": self.successful_escapes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PermadeathMode":
        return cls(
            enabled=data.get("enabled", False),
            death_count=data.get("death_count", 0),
            best_run_days=data.get("best_run_days"),
            total_deaths=data.get("total_deaths", 0),
            escape_attempts=data.get("escape_attempts", 0),
            successful_escapes=data.get("successful_escapes", 0),
        )


@dataclass
class SpeedrunMode:
    enabled: bool = False
    start_time: float = 0.0
    end_time: float = 0.0
    target_days: int = 10
    checkpoints: dict = field(default_factory=dict)
    current_checkpoint: Optional[str] = None
    best_time: Optional[float] = None

    def start(self, start_time: float) -> None:
        self.enabled = True
        self.start_time = start_time
        self.end_time = 0.0
        self.checkpoints = {}
        self.current_checkpoint = None

    def finish(self, end_time: float) -> None:
        self.end_time = end_time
        if self.best_time is None or end_time < self.best_time:
            self.best_time = end_time

    def get_elapsed_time(self, current_time: float) -> float:
        if self.start_time == 0:
            return 0.0
        end = self.end_time if self.end_time > 0 else current_time
        return end - self.start_time

    def set_checkpoint(self, checkpoint_name: str, current_time: float) -> None:
        elapsed = self.get_elapsed_time(current_time)
        self.checkpoints[checkpoint_name] = elapsed
        self.current_checkpoint = checkpoint_name

    def get_remaining_time(self, current_time: float) -> Optional[float]:
        elapsed = self.get_elapsed_time(current_time)
        target_seconds = self.target_days * 60
        remaining = target_seconds - elapsed
        return remaining if remaining > 0 else None

    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "target_days": self.target_days,
            "checkpoints": self.checkpoints,
            "current_checkpoint": self.current_checkpoint,
            "best_time": self.best_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SpeedrunMode":
        return cls(
            enabled=data.get("enabled", False),
            start_time=data.get("start_time", 0.0),
            end_time=data.get("end_time", 0.0),
            target_days=data.get("target_days", 10),
            checkpoints=data.get("checkpoints", {}),
            current_checkpoint=data.get("current_checkpoint"),
            best_time=data.get("best_time"),
        )


@dataclass
class PacifistMode:
    enabled: bool = False
    kills_made: int = 0
    violent_actions: int = 0
    stealth_completions: int = 0
    non_lethal_kills: int = 0

    def record_kill(self) -> bool:
        self.kills_made += 1
        return self.enabled and self.kills_made > 0

    def record_violent_action(self) -> bool:
        self.violent_actions += 1
        return False

    def record_stealth_completion(self) -> None:
        self.stealth_completions += 1

    def can_complete_pacifist(self) -> bool:
        return self.enabled and self.kills_made == 0

    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "kills_made": self.kills_made,
            "violent_actions": self.violent_actions,
            "stealth_completions": self.stealth_completions,
            "non_lethal_kills": self.non_lethal_kills,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PacifistMode":
        return cls(
            enabled=data.get("enabled", False),
            kills_made=data.get("kills_made", 0),
            violent_actions=data.get("violent_actions", 0),
            stealth_completions=data.get("stealth_completions", 0),
            non_lethal_kills=data.get("non_lethal_kills", 0),
        )


class GameModeManager:
    def __init__(self):
        self.current_mode: GameMode = GameMode.STANDARD
        self.settings: GameModeSettings = GameModeSettings(mode=GameMode.STANDARD)
        self.permadeath: PermadeathMode = PermadeathMode()
        self.speedrun: SpeedrunMode = SpeedrunMode()
        self.pacifist: PacifistMode = PacifistMode()
        self.challenge_list: list[str] = []

    def set_mode(self, mode: GameMode, **kwargs) -> None:
        self.current_mode = mode
        self.settings = GameModeSettings(mode=mode, **kwargs)

        if mode == GameMode.PERMADEATH:
            self.permadeath.enabled = True
            self.permadeath.start_run()
        else:
            self.permadeath.enabled = False

        if mode == GameMode.SPEEDRUN:
            self.speedrun.enabled = True
            self.speedrun.target_days = kwargs.get("target_days", 10)
        else:
            self.speedrun.enabled = False

        if mode == GameMode.PACIFIST:
            self.pacifist.enabled = True
        else:
            self.pacifist.enabled = False

    def get_mode(self) -> GameMode:
        return self.current_mode

    def is_permadeath(self) -> bool:
        return self.permadeath.enabled

    def is_speedrun(self) -> bool:
        return self.speedrun.enabled

    def is_pacifist(self) -> bool:
        return self.pacifist.enabled

    def get_modifier(self, modifier_type: str, default: float = 1.0) -> float:
        return self.settings.modifiers.get(modifier_type, default)

    def add_restriction(self, restriction: str) -> None:
        if restriction not in self.settings.restrictions:
            self.settings.restrictions.append(restriction)

    def has_restriction(self, restriction: str) -> bool:
        return restriction in self.settings.restrictions

    def get_restrictions_text(self) -> str:
        if not self.settings.restrictions:
            return "Keine Einschränkungen"
        return ", ".join(self.settings.restrictions)

    def to_dict(self) -> dict:
        return {
            "current_mode": self.current_mode.value,
            "settings": self.settings.to_dict(),
            "permadeath": self.permadeath.to_dict(),
            "speedrun": self.speedrun.to_dict(),
            "pacifist": self.pacifist.to_dict(),
            "challenge_list": self.challenge_list,
        }

    def load_from_dict(self, data: dict) -> None:
        if "current_mode" in data:
            mode = GameMode(data["current_mode"])
            self.set_mode(mode)

        if "permadeath" in data:
            self.permadeath = PermadeathMode.from_dict(data["permadeath"])
        if "speedrun" in data:
            self.speedrun = SpeedrunMode.from_dict(data["speedrun"])
        if "pacifist" in data:
            self.pacifist = PacifistMode.from_dict(data["pacifist"])
        if "challenge_list" in data:
            self.challenge_list = data["challenge_list"]


def create_challenge(challenge_name: str) -> GameModeSettings:
    challenges = {
        "ghost_run": GameModeSettings(
            mode=GameMode.CHALLENGE,
            pacifist_mode=False,
            restrictions=["no_detection", "stealth_only"],
            modifiers={"stealth_bonus": 2.0, "detection_penalty": 3.0},
        ),
        "money_maker": GameModeSettings(
            mode=GameMode.CHALLENGE,
            pacifist_mode=False,
            target_days=15,
            modifiers={"cash_multiplier": 3.0},
        ),
        "street_saint": GameModeSettings(
            mode=GameMode.CHALLENGE,
            pacifist_mode=True,
            restrictions=["no_kills", "no_violence"],
        ),
        "speed_demon": GameModeSettings(
            mode=GameMode.CHALLENGE,
            speedrun_timer_active=True,
            target_days=7,
            modifiers={"stamina_cost": 1.5, "police_sensitivity": 2.0},
        ),
    }
    return challenges.get(challenge_name, GameModeSettings(mode=GameMode.STANDARD))