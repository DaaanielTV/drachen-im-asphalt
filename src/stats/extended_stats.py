from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import time


@dataclass
class SessionStats:
    start_time: float = 0.0
    end_time: float = 0.0
    actions_taken: int = 0
    missions_completed: int = 0
    encounters_fought: int = 0
    crimes_committed: int = 0
    cash_earned: int = 0
    cash_spent: int = 0
    distance_traveled: int = 0

    def get_duration(self) -> float:
        end = self.end_time if self.end_time > 0 else time.time()
        return end - self.start_time

    def to_dict(self) -> dict:
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "actions_taken": self.actions_taken,
            "missions_completed": self.missions_completed,
            "encounters_fought": self.encounters_fought,
            "crimes_committed": self.crimes_committed,
            "cash_earned": self.cash_earned,
            "cash_spent": self.cash_spent,
            "distance_traveled": self.distance_traveled,
        }


@dataclass
class LifetimeStats:
    games_played: int = 0
    total_playtime_seconds: float = 0.0
    total_missions_completed: int = 0
    total_crimes_committed: int = 0
    total_cash_earned: int = 0
    total_kills: int = 0
    total_deaths: int = 0
    furthest_day_reached: int = 0
    highest_level: int = 1
    highest_cash: int = 0
    highest_reputation: int = 0
    most_wanted_achieved: int = 0
    dragons_defeated: int = 0
    achievements_unlocked: int = 0
    districts_fully_explored: int = 0
    perfect_runs: int = 0
    pacifist_runs: int = 0
    speedrun_completions: int = 0
    best_speedrun_time: Optional[float] = None

    def update_from_session(self, session: SessionStats) -> None:
        self.total_playtime_seconds += session.get_duration()
        self.total_missions_completed += session.missions_completed
        self.total_crimes_committed += session.crimes_committed
        self.total_cash_earned += session.cash_earned

    def to_dict(self) -> dict:
        return {
            "games_played": self.games_played,
            "total_playtime_seconds": self.total_playtime_seconds,
            "total_missions_completed": self.total_missions_completed,
            "total_crimes_committed": self.total_crimes_committed,
            "total_cash_earned": self.total_cash_earned,
            "total_kills": self.total_kills,
            "total_deaths": self.total_deaths,
            "furthest_day_reached": self.furthest_day_reached,
            "highest_level": self.highest_level,
            "highest_cash": self.highest_cash,
            "highest_reputation": self.highest_reputation,
            "most_wanted_achieved": self.most_wanted_achieved,
            "dragons_defeated": self.dragons_defeated,
            "achievements_unlocked": self.achievements_unlocked,
            "districts_fully_explored": self.districts_fully_explored,
            "perfect_runs": self.perfect_runs,
            "pacifist_runs": self.pacifist_runs,
            "speedrun_completions": self.speedrun_completions,
            "best_speedrun_time": self.best_speedrun_time,
        }


@dataclass
class DistrictStats:
    district_name: str
    times_visited: int = 0
    crimes_committed: int = 0
    missions_completed: int = 0
    cash_earned: int = 0
    encounters_survived: int = 0
    favorite_activities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "district_name": self.district_name,
            "times_visited": self.times_visited,
            "crimes_committed": self.crimes_committed,
            "missions_completed": self.missions_completed,
            "cash_earned": self.cash_earned,
            "encounters_survived": self.encounters_survived,
            "favorite_activities": self.favorite_activities,
        }


@dataclass
class WeaponStats:
    weapon_name: str
    times_used: int = 0
    enemies_killed: int = 0
    accuracy: float = 0.0
    shots_fired: int = 0
    shots_hit: int = 0

    def update_accuracy(self) -> float:
        if self.shots_fired > 0:
            self.accuracy = self.shots_hit / self.shots_fired
        return self.accuracy

    def to_dict(self) -> dict:
        return {
            "weapon_name": self.weapon_name,
            "times_used": self.times_used,
            "enemies_killed": self.enemies_killed,
            "accuracy": self.accuracy,
            "shots_fired": self.shots_fired,
            "shots_hit": self.shots_hit,
        }


@dataclass
class MissionStats:
    mission_name: str
    attempts: int = 0
    completions: int = 0
    failures: int = 0
    fastest_completion: Optional[float] = None
    average_stamina_spent: float = 0.0

    def get_success_rate(self) -> float:
        if self.attempts == 0:
            return 0.0
        return self.completions / self.attempts

    def to_dict(self) -> dict:
        return {
            "mission_name": self.mission_name,
            "attempts": self.attempts,
            "completions": self.completions,
            "failures": self.failures,
            "fastest_completion": self.fastest_completion,
            "average_stamina_spent": self.average_stamina_spent,
        }


class ExtendedStatistics:
    def __init__(self):
        self.current_session = SessionStats()
        self.lifetime = LifetimeStats()
        self.district_stats: dict[str, DistrictStats] = {}
        self.weapon_stats: dict[str, WeaponStats] = {}
        self.mission_stats: dict[str, MissionStats] = {}
        self.game_history: list[dict] = []

    def start_session(self) -> None:
        self.current_session = SessionStats()
        self.current_session.start_time = time.time()

    def end_session(self) -> None:
        self.current_session.end_time = time.time()
        self.lifetime.update_from_session(self.current_session)
        self.lifetime.games_played += 1

        game_record = {
            "date": datetime.now().isoformat(),
            "duration": self.current_session.get_duration(),
            "missions": self.current_session.missions_completed,
            "crimes": self.current_session.crimes_committed,
            "cash": self.current_session.cash_earned - self.current_session.cash_spent,
        }
        self.game_history.append(game_record)

        if len(self.game_history) > 100:
            self.game_history = self.game_history[-100:]

    def record_action(self) -> None:
        self.current_session.actions_taken += 1

    def record_mission_completed(self) -> None:
        self.current_session.missions_completed += 1
        self.lifetime.total_missions_completed += 1

    def record_crime(self) -> None:
        self.current_session.crimes_committed += 1
        self.lifetime.total_crimes_committed += 1

    def record_cash_change(self, earned: int = 0, spent: int = 0) -> None:
        if earned > 0:
            self.current_session.cash_earned += earned
            self.lifetime.highest_cash = max(self.lifetime.highest_cash, earned)
        if spent > 0:
            self.current_session.cash_spent += spent

    def record_district_visit(self, district_name: str) -> None:
        if district_name not in self.district_stats:
            self.district_stats[district_name] = DistrictStats(district_name=district_name)
        self.district_stats[district_name].times_visited += 1

    def record_weapon_use(self, weapon_name: str, hit: bool = False, kill: bool = False) -> None:
        if weapon_name not in self.weapon_stats:
            self.weapon_stats[weapon_name] = WeaponStats(weapon_name=weapon_name)
        stats = self.weapon_stats[weapon_name]
        stats.times_used += 1
        stats.shots_fired += 1
        if hit:
            stats.shots_hit += 1
        if kill:
            stats.enemies_killed += 1
        stats.update_accuracy()

    def update_high_scores(self, protagonist) -> None:
        self.lifetime.furthest_day_reached = max(self.lifetime.furthest_day_reached, protagonist.days)
        self.lifetime.highest_level = max(self.lifetime.highest_level, protagonist.level)
        self.lifetime.highest_reputation = max(self.lifetime.highest_reputation, protagonist.reputation)
        self.lifetime.most_wanted_achieved = max(self.lifetime.most_wanted_achieved, protagonist.wanted_level)

    def get_session_summary(self) -> str:
        duration = self.current_session.get_duration()
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        return f"""[STATISTIK] Aktuelle Sitzung:
  Dauer: {hours}h {minutes}m
  Aktionen: {self.current_session.actions_taken}
  Missionen: {self.current_session.missions_completed}
  Verbrechen: {self.current_session.crimes_committed}
  Verdient: ${self.current_session.cash_earned}
  Ausgegeben: ${self.current_session.cash_spent}"""

    def get_lifetime_summary(self) -> str:
        hours = int(self.lifetime.total_playtime_seconds // 3600)
        minutes = int((self.lifetime.total_playtime_seconds % 3600) // 60)
        return f"""[STATISTIK] Gesamte Statistik:
  Spiele: {self.lifetime.games_played}
  Spielzeit: {hours}h {minutes}m
  Missionen: {self.lifetime.total_missions_completed}
  Verbrechen: {self.lifetime.total_crimes_committed}
  Tagesrekord: {self.lifetime.furthest_day_reached}
  Höchstes Level: {self.lifetime.highest_level}
  Meiste Cash: ${self.lifetime.highest_cash}
  Höchste Reputation: {self.lifetime.highest_reputation}"""

    def get_top_districts(self) -> list[tuple[str, int]]:
        sorted_districts = sorted(
            self.district_stats.items(),
            key=lambda x: x[1].times_visited,
            reverse=True
        )
        return [(name, stats.times_visited) for name, stats in sorted_districts[:5]]

    def get_top_weapons(self) -> list[tuple[str, int]]:
        sorted_weapons = sorted(
            self.weapon_stats.items(),
            key=lambda x: x[1].times_used,
            reverse=True
        )
        return [(name, stats.times_used) for name, stats in sorted_weapons[:5]]

    def to_dict(self) -> dict:
        return {
            "current_session": self.current_session.to_dict(),
            "lifetime": self.lifetime.to_dict(),
            "district_stats": {name: stats.to_dict() for name, stats in self.district_stats.items()},
            "weapon_stats": {name: stats.to_dict() for name, stats in self.weapon_stats.items()},
            "mission_stats": {name: stats.to_dict() for name, stats in self.mission_stats.items()},
            "game_history": self.game_history,
        }

    def load_from_dict(self, data: dict) -> None:
        if "lifetime" in data:
            for key, value in data["lifetime"].items():
                if hasattr(self.lifetime, key):
                    setattr(self.lifetime, key, value)
        if "district_stats" in data:
            self.district_stats = {
                name: DistrictStats(**stats_data)
                for name, stats_data in data["district_stats"].items()
            }
        if "weapon_stats" in data:
            self.weapon_stats = {
                name: WeaponStats(**stats_data)
                for name, stats_data in data["weapon_stats"].items()
            }
        if "mission_stats" in data:
            self.mission_stats = {
                name: MissionStats(**stats_data)
                for name, stats_data in data["mission_stats"].items()
            }
        if "game_history" in data:
            self.game_history = data["game_history"]