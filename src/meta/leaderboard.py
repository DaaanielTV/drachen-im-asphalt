from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timedelta
import random
import json
import os


@dataclass
class LeaderboardEntry:
    rank: int
    player_name: str
    score: int
    character_type: str
    days: int
    completion_date: str
    game_mode: str
    special_conditions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "player_name": self.player_name,
            "score": self.score,
            "character_type": self.character_type,
            "days": self.days,
            "completion_date": self.completion_date,
            "game_mode": self.game_mode,
            "special_conditions": self.special_conditions,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LeaderboardEntry":
        return cls(**data)


class Leaderboard:
    CATEGORIES = ["fastest", "richest", "highest_level", "most_missions", "pacifist", "stealth"]

    def __init__(self, leaderboard_file: str = "data/leaderboard.json"):
        self.file_path = leaderboard_file
        self.entries: dict[str, list[LeaderboardEntry]] = {cat: [] for cat in self.CATEGORIES}
        self.max_entries_per_category = 100
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.file_path):
            return
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for category, entries_data in data.get("entries", {}).items():
                    if category in self.entries:
                        self.entries[category] = [
                            LeaderboardEntry.from_dict(e) for e in entries_data
                        ]
        except Exception:
            pass

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        data = {
            "entries": {
                cat: [e.to_dict() for e in entries]
                for cat, entries in self.entries.items()
            }
        }
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_entry(self, category: str, entry: LeaderboardEntry) -> int:
        if category not in self.entries:
            return -1

        self.entries[category].append(entry)
        self.entries[category].sort(key=lambda e: e.score, reverse=True)

        if len(self.entries[category]) > self.max_entries_per_category:
            self.entries[category] = self.entries[category][:self.max_entries_per_category]

        for i, entry in enumerate(self.entries[category]):
            entry.rank = i + 1

        self._save()

        return entry.rank

    def get_top(self, category: str, limit: int = 10) -> list[LeaderboardEntry]:
        if category not in self.entries:
            return []
        return self.entries[category][:limit]

    def get_player_rank(self, category: str, player_name: str) -> Optional[int]:
        for entry in self.entries.get(category, []):
            if entry.player_name == player_name:
                return entry.rank
        return None

    def is_high_score(self, category: str, score: int) -> bool:
        entries = self.entries.get(category, [])
        if len(entries) < self.max_entries_per_category:
            return True
        return score > entries[-1].score

    def calculate_score(self, protagonist, game_mode: str, special_conditions: list[str]) -> int:
        base_score = 0
        base_score += protagonist.level * 100
        base_score += protagonist.days * 10
        base_score += protagonist.cash // 10
        base_score += protagonist.reputation * 5

        completed_missions = len(protagonist.story_flags.get("completed_missions", []))
        base_score += completed_missions * 50

        if protagonist.dragon_defeated:
            base_score += 5000
            if protagonist.days <= 10:
                base_score += 2000

        mode_multiplier = 1.0
        if game_mode == "permadeath":
            mode_multiplier = 1.5
        elif game_mode == "speedrun":
            mode_multiplier = 1.3
        elif game_mode == "pacifist":
            mode_multiplier = 1.4

        condition_bonus = len(special_conditions) * 100
        mode_multiplier += condition_bonus / 1000

        final_score = int(base_score * mode_multiplier)
        return final_score

    def submit_score(self, protagonist, game_mode: str, special_conditions: list[str] = None) -> tuple[int, dict]:
        score = self.calculate_score(protagonist, game_mode, special_conditions or [])

        entry = LeaderboardEntry(
            rank=0,
            player_name=protagonist.name,
            score=score,
            character_type=protagonist.character_type,
            days=protagonist.days,
            completion_date=datetime.now().isoformat(),
            game_mode=game_mode,
            special_conditions=special_conditions or [],
        )

        ranks = {}
        for category in self.CATEGORIES:
            rank = self.add_entry(category, entry)
            ranks[category] = rank

        return score, ranks

    def get_display(self, category: str, limit: int = 10) -> str:
        entries = self.get_top(category, limit)
        if not entries:
            return f"[LEADERBOARD] Keine Einträge für '{category}'"

        display = f"\n[LEADERBOARD] {category.upper()}\n"
        display += "-" * 50 + "\n"
        for entry in entries:
            display += f"{entry.rank:3}. {entry.player_name:<15} {entry.score:>8} Punkte\n"
            display += f"    {entry.character_type} | Tag {entry.days} | {entry.game_mode}\n"
        return display


@dataclass
class DailyChallenge:
    challenge_id: str
    title: str
    description: str
    objective_type: str
    target_value: int
    reward_cash: int
    reward_reputation: int
    difficulty: str
    expires_at: str

    def is_expired(self) -> bool:
        expires = datetime.fromisoformat(self.expires_at)
        return datetime.now() > expires

    def to_dict(self) -> dict:
        return {
            "challenge_id": self.challenge_id,
            "title": self.title,
            "description": self.description,
            "objective_type": self.objective_type,
            "target_value": self.target_value,
            "reward_cash": self.reward_cash,
            "reward_reputation": self.reward_reputation,
            "difficulty": self.difficulty,
            "expires_at": self.expires_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DailyChallenge":
        return cls(**data)


class DailyChallengeManager:
    CHALLENGE_TEMPLATES = [
        {
            "title": "Schnelle Finger",
            "description": "Schließe 3 Missionen in einem Tag ab",
            "objective_type": "missions_completed",
            "target_value": 3,
            "reward_cash": 500,
            "reward_reputation": 50,
        },
        {
            "title": "Im Schatten",
            "description": "Erkunde 5 verschiedene Stadtteile",
            "objective_type": "districts_explored",
            "target_value": 5,
            "reward_cash": 300,
            "reward_reputation": 30,
        },
        {
            "title": "Schießbude",
            "description": "Besiege 10 Gegner",
            "objective_type": "enemies_defeated",
            "target_value": 10,
            "reward_cash": 400,
            "reward_reputation": 40,
        },
        {
            "title": "Millionär",
            "description": "Sammle $2000 in einem Tag",
            "objective_type": "cash_earned",
            "target_value": 2000,
            "reward_cash": 200,
            "reward_reputation": 20,
        },
        {
            "title": "Gesetzloser",
            "description": "Erreiche Wanted Level 5",
            "objective_type": "wanted_level",
            "target_value": 5,
            "reward_cash": 350,
            "reward_reputation": 60,
        },
        {
            "title": "Aufsteiger",
            "description": "Erreiche Level 3",
            "objective_type": "level_reached",
            "target_value": 3,
            "reward_cash": 600,
            "reward_reputation": 40,
        },
        {
            "title": "Kriminelle Karriere",
            "description": "Begehe 5 Verbrechen",
            "objective_type": "crimes_committed",
            "target_value": 5,
            "reward_cash": 250,
            "reward_reputation": 35,
        },
        {
            "title": "Drogenbaron",
            "description": "Probiere 3 verschiedene Drogen",
            "objective_type": "drugs_used",
            "target_value": 3,
            "reward_cash": 400,
            "reward_reputation": 25,
        },
        {
            "title": "Schecken-Jäger",
            "description": "Finde und schließe eine geheime Mission ab",
            "objective_type": "secret_missions",
            "target_value": 1,
            "reward_cash": 800,
            "reward_reputation": 75,
        },
        {
            "title": "Drachentöter",
            "description": "Besiege den Enddrachen",
            "objective_type": "dragon_defeated",
            "target_value": 1,
            "reward_cash": 1000,
            "reward_reputation": 100,
        },
    ]

    def __init__(self):
        self.daily_challenges: list[DailyChallenge] = []
        self.challenge_progress: dict[str, int] = {}
        self.completed_challenges: list[str] = []
        self.last_reset: Optional[str] = None
        self._generate_daily_challenges()

    def _generate_daily_challenges(self) -> None:
        today = datetime.now().date()
        if self.last_reset and self.last_reset.startswith(str(today)):
            return

        self.last_reset = datetime.now().isoformat()
        self.daily_challenges = []
        self.challenge_progress = {}

        templates = random.sample(self.CHALLENGE_TEMPLATES, min(3, len(self.CHALLENGE_TEMPLATES)))

        tomorrow = datetime.now() + timedelta(days=1)
        expires_at = tomorrow.replace(hour=0, minute=0, second=0).isoformat()

        for i, template in enumerate(templates):
            challenge = DailyChallenge(
                challenge_id=f"daily_{today}_{i}",
                title=template["title"],
                description=template["description"],
                objective_type=template["objective_type"],
                target_value=template["target_value"],
                reward_cash=template["reward_cash"],
                reward_reputation=template["reward_reputation"],
                difficulty="normal",
                expires_at=expires_at,
            )
            self.daily_challenges.append(challenge)
            self.challenge_progress[challenge.challenge_id] = 0

    def get_active_challenges(self) -> list[DailyChallenge]:
        self._generate_daily_challenges()
        return [c for c in self.daily_challenges if not c.is_expired()]

    def update_progress(self, objective_type: str, amount: int = 1) -> None:
        for challenge in self.daily_challenges:
            if challenge.objective_type == objective_type:
                self.challenge_progress[challenge.challenge_id] += amount

    def check_completion(self, challenge_id: str) -> bool:
        for challenge in self.daily_challenges:
            if challenge.challenge_id == challenge_id:
                return self.challenge_progress[challenge_id] >= challenge.target_value
        return False

    def claim_reward(self, challenge_id: str, protagonist) -> tuple[bool, str]:
        if challenge_id in self.completed_challenges:
            return False, "Belohnung bereits beansprucht"

        if not self.check_completion(challenge_id):
            return False, "Herausforderung noch nicht abgeschlossen"

        for challenge in self.daily_challenges:
            if challenge.challenge_id == challenge_id:
                protagonist.cash += challenge.reward_cash
                protagonist.reputation += challenge.reward_reputation
                self.completed_challenges.append(challenge_id)
                return True, f"Belohnung beansprucht: ${challenge.reward_cash}, +{challenge.reward_reputation} Reputation"

        return False, "Herausforderung nicht gefunden"

    def get_display(self) -> str:
        challenges = self.get_active_challenges()
        if not challenges:
            return "[TÄGLICHE HERAUSFORDERUNGEN] Keine Herausforderungen verfügbar"

        display = "\n[TÄGLICHE HERAUSFORDERUNGEN]\n"
        display += "-" * 50 + "\n"

        for challenge in challenges:
            progress = self.challenge_progress.get(challenge.challenge_id, 0)
            completed = progress >= challenge.target_value
            status = "[X]" if completed else "[ ]"
            display += f"{status} {challenge.title}\n"
            display += f"    {challenge.description}\n"
            display += f"    Fortschritt: {progress}/{challenge.target_value}\n"
            display += f"    Belohnung: ${challenge.reward_cash}, +{challenge.reward_reputation} Rep\n\n"

        return display

    def to_dict(self) -> dict:
        return {
            "daily_challenges": [c.to_dict() for c in self.daily_challenges],
            "challenge_progress": self.challenge_progress,
            "completed_challenges": self.completed_challenges,
            "last_reset": self.last_reset,
        }

    def load_from_dict(self, data: dict) -> None:
        if "daily_challenges" in data:
            self.daily_challenges = [DailyChallenge.from_dict(c) for c in data["daily_challenges"]]
        if "challenge_progress" in data:
            self.challenge_progress = data["challenge_progress"]
        if "completed_challenges" in data:
            self.completed_challenges = data["completed_challenges"]
        if "last_reset" in data:
            self.last_reset = data["last_reset"]


class SeasonalEvent:
    def __init__(self, event_id: str, name: str, start_date: str, end_date: str, modifier: dict):
        self.event_id = event_id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.modifier = modifier
        self.active = False

    def check_active(self) -> bool:
        now = datetime.now()
        start = datetime.fromisoformat(self.start_date)
        end = datetime.fromisoformat(self.end_date)
        self.active = start <= now <= end
        return self.active

    def get_modifier(self, modifier_type: str) -> float:
        return self.modifier.get(modifier_type, 1.0)


class EventCalendar:
    def __init__(self):
        self.events: list[SeasonalEvent] = []
        self.active_events: list[SeasonalEvent] = []
        self._initialize_events()

    def _initialize_events(self) -> None:
        year = datetime.now().year

        self.events = [
            SeasonalEvent(
                "halloween",
                "Haloween",
                f"{year}-10-25",
                f"{year}-11-01",
                {"reputation": 1.5, "hallucination_intensity": 1.3}
            ),
            SeasonalEvent(
                "christmas",
                "Weihnachten",
                f"{year}-12-20",
                f"{year}-12-26",
                {"cash_bonus": 2.0, "police_activity": 0.5}
            ),
            SeasonalEvent(
                "summer",
                "Sommerevent",
                f"{year}-06-01",
                f"{year}-08-31",
                {"tourist_multiplier": 2.0, "police_activity": 1.2}
            ),
        ]

    def update_active_events(self) -> None:
        self.active_events = [e for e in self.events if e.check_active()]

    def get_event_modifier(self, modifier_type: str) -> float:
        result = 1.0
        for event in self.active_events:
            result *= event.get_modifier(modifier_type)
        return result

    def get_active_event_names(self) -> list[str]:
        return [e.name for e in self.active_events]