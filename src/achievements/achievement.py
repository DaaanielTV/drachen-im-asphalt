from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class Achievement:
    id: str
    name: str
    description: str
    category: str
    unlocked: bool = False
    unlocked_at_day: Optional[int] = None
    secret: bool = False
    check_condition: Optional[Callable] = field(default=None, repr=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "unlocked": self.unlocked,
            "unlocked_at_day": self.unlocked_at_day,
            "secret": self.secret
        }


class AchievementManager:
    def __init__(self):
        self.achievements: dict[str, Achievement] = {}
        self._initialize_achievements()

    def _initialize_achievements(self):
        self.achievements = {
            "first_crime": Achievement(
                id="first_crime",
                name="Erster Sündenfall",
                description="Begehe dein erstes Verbrechen",
                category="Karriere"
            ),
            "first_money": Achievement(
                id="first_money",
                name="EASY MONEY",
                description="Verdiene deine ersten $500",
                category="Karriere"
            ),
            "first_rest": Achievement(
                id="first_rest",
                name="Müde Krieger",
                description="Ruh dich zum ersten Mal aus",
                category="Leben"
            ),
            "first_district": Achievement(
                id="first_district",
                name="Stadtführer",
                description="Erkunde einen neuen Stadtteil",
                category="Entdeckung"
            ),
            "explore_all_districts": Achievement(
                id="explore_all_districts",
                name="Stadtkenner",
                description="Erkunde alle Stadtteile",
                category="Entdeckung"
            ),
            "first_arrest": Achievement(
                id="first_arrest",
                name="Bekannter Ganove",
                description="Erreiche Wanted Level 1",
                category="Ruf"
            ),
            "most_wanted": Achievement(
                id="most_wanted",
                name="Most Wanted",
                description="Erreiche Wanted Level 5",
                category="Ruf"
            ),
            "first_mission": Achievement(
                id="first_mission",
                name="Auftraggeber",
                description="Schließe deine erste Mission ab",
                category="Karriere"
            ),
            "five_missions": Achievement(
                id="five_missions",
                name="Erfahrener Krimineller",
                description="Schließe 5 Missionen ab",
                category="Karriere"
            ),
            "ten_missions": Achievement(
                id="ten_missions",
                name="Patron der Unterwelt",
                description="Schließe 10 Missionen ab",
                category="Karriere"
            ),
            "first_love": Achievement(
                id="first_love",
                name="Kriminelle Liebschaft",
                description="Erlebe deinen ersten Partner-Verrat",
                category="Beziehungen",
                secret=True
            ),
            "first_betrayal": Achievement(
                id="first_betrayal",
                name="Einsamer Wolf",
                description="Verliere das Vertrauen deines Partners komplett",
                category="Beziehungen"
            ),
            "first_drug": Achievement(
                id="first_drug",
                name="Dunkle Pfade",
                description="Probiere zum ersten Mal Drogen",
                category="Laster"
            ),
            "dragon_seen": Achievement(
                id="dragon_seen",
                name="Der Drache erwacht",
                description="Erlebe deine erste Drachen-Halluzination",
                category="Psychose"
            ),
            "five_dragons": Achievement(
                id="five_dragons",
                name="Paranoia",
                description="Erlebe 5 Drachen-Halluzinationen",
                category="Psychose"
            ),
            "ten_dragons": Achievement(
                id="ten_dragons",
                name="Abgrund",
                description="Erlebe 10 Drachen-Halluzinationen",
                category="Psychose"
            ),
            "rich": Achievement(
                id="rich",
                name="Vice City Millionär",
                description="Sammle $10.000 Cash",
                category="Reichtum"
            ),
            "very_rich": Achievement(
                id="very_rich",
                name="König von Vice City",
                description="Sammle $50.000 Cash",
                category="Reichtum"
            ),
            "first_level_up": Achievement(
                id="first_level_up",
                name="Aufstieg",
                description="Erreiche Level 2",
                category="Karriere"
            ),
            "level_5": Achievement(
                id="level_5",
                name="Etablierter Ganove",
                description="Erreiche Level 5",
                category="Karriere"
            ),
            "level_10": Achievement(
                id="level_10",
                name="Boss der Unterwelt",
                description="Erreiche Level 10",
                category="Karriere"
            ),
            "first_win": Achievement(
                id="first_win",
                name="Drachenbezwingung",
                description="Besiege den Drachen der Konsequenzen",
                category="Endsieg"
            ),
            "first_escape": Achievement(
                id="first_escape",
                name="Geisterhand",
                description="Entkomme einer Polizeikontrolle",
                category="Fähigkeiten"
            ),
            "silent_killer": Achievement(
                id="silent_killer",
                name="Lautloser Tod",
                description="Besiege 5 Gegner lautlos",
                category="Fähigkeiten"
            ),
            "speedrunner": Achievement(
                id="speedrunner",
                name="Blitzstart",
                description="Besiege den Drachen innerhalb von 10 Tagen",
                category="Herausforderung",
                secret=True
            ),
            "survivor": Achievement(
                id="survivor",
                name="ZähÜberlebender",
                description="Besiege den Drachen mit weniger als 10 Ausdauer",
                category="Herausforderung",
                secret=True
            ),
            "ghost": Achievement(
                id="ghost",
                name="Ghost",
                description="Besiege den Drachen ohne jemals entdeckt zu werden",
                category="Herausforderung",
                secret=True
            ),
            "perfect_week": Achievement(
                id="perfect_week",
                name="Perfekte Woche",
                description="Erreiche 7 Tage ohne jemals entdeckt zu werden",
                category="Herausforderung",
                secret=True
            ),
            "no_crime": Achievement(
                id="no_crime",
                name="Unschuld",
                description="Erreiche Kapitel 3 ohne jemals ein Verbrechen zu begehen",
                category="Herausforderung",
                secret=True
            ),
            "unstoppable": Achievement(
                id="unstoppable",
                name="Unaufhaltsam",
                description="Gewinne 10 Kämpfe in Folge",
                category="Herausforderung"
            ),
            "bad_influence": Achievement(
                id="bad_influence",
                name="Schlechter Einfluss",
                description="Verführe deinen Partner zum Verrat",
                category="Beziehungen",
                secret=True
            ),
            "redemption": Achievement(
                id="redemption",
                name="Erlösung",
                description="Schließe das Spiel mit dem Erlösungs-Pfad ab",
                category="Endsieg",
                secret=True
            ),
            "ng_plus_1": Achievement(
                id="ng_plus_1",
                name="Neuanfang",
                description="Starte New Game+ zum ersten Mal",
                category="Endsieg"
            ),
            "ng_plus_3": Achievement(
                id="ng_plus_3",
                name="Zyklus",
                description="Spiele 3 Mal durch (NG+2)",
                category="Endsieg"
            ),
        }

    def unlock(self, achievement_id: str, day: int = 0) -> bool:
        achievement = self.achievements.get(achievement_id)
        if achievement and not achievement.unlocked:
            achievement.unlocked = True
            achievement.unlocked_at_day = day
            return True
        return False

    def is_unlocked(self, achievement_id: str) -> bool:
        achievement = self.achievements.get(achievement_id)
        return achievement.unlocked if achievement else False

    def check_and_unlock(self, achievement_id: str, protagonist) -> bool:
        achievement = self.achievements.get(achievement_id)
        if not achievement or achievement.unlocked:
            return False

        should_unlock = False
        if achievement_id == "first_crime":
            should_unlock = protagonist.story_flags.get("first_crime_committed", False)
        elif achievement_id == "first_money":
            should_unlock = protagonist.cash >= 500
        elif achievement_id == "first_rest":
            should_unlock = protagonist.days >= 1
        elif achievement_id == "first_district":
            should_unlock = len(protagonist.story_flags.get("explored_districts", [])) >= 1
        elif achievement_id == "explore_all_districts":
            should_unlock = len(protagonist.story_flags.get("explored_districts", [])) >= 9
        elif achievement_id == "first_arrest":
            should_unlock = protagonist.wanted_level >= 1
        elif achievement_id == "most_wanted":
            should_unlock = protagonist.wanted_level >= 5
        elif achievement_id == "first_mission":
            should_unlock = len(protagonist.story_flags.get("completed_missions", [])) >= 1
        elif achievement_id == "five_missions":
            should_unlock = len(protagonist.story_flags.get("completed_missions", [])) >= 5
        elif achievement_id == "ten_missions":
            should_unlock = len(protagonist.story_flags.get("completed_missions", [])) >= 10
        elif achievement_id == "first_betrayal":
            should_unlock = protagonist.partner_trust <= 0
        elif achievement_id == "first_drug":
            should_unlock = len(protagonist.drug_effects) > 0
        elif achievement_id == "dragon_seen":
            should_unlock = protagonist.dragon_encounters >= 1
        elif achievement_id == "five_dragons":
            should_unlock = protagonist.dragon_encounters >= 5
        elif achievement_id == "ten_dragons":
            should_unlock = protagonist.dragon_encounters >= 10
        elif achievement_id == "rich":
            should_unlock = protagonist.cash >= 10000
        elif achievement_id == "very_rich":
            should_unlock = protagonist.cash >= 50000
        elif achievement_id == "first_level_up":
            should_unlock = protagonist.level >= 2
        elif achievement_id == "level_5":
            should_unlock = protagonist.level >= 5
        elif achievement_id == "level_10":
            should_unlock = protagonist.level >= 10
        elif achievement_id == "first_win":
            should_unlock = protagonist.dragon_defeated

        if should_unlock:
            return self.unlock(achievement_id, protagonist.days)
        return False

    def get_unlocked_count(self) -> int:
        return sum(1 for a in self.achievements.values() if a.unlocked)

    def get_total_count(self) -> int:
        return len(self.achievements)

    def get_by_category(self, category: str) -> list[Achievement]:
        return [a for a in self.achievements.values() if a.category == category]

    def get_categories(self) -> list[str]:
        return list(set(a.category for a in self.achievements.values()))

    def to_dict(self) -> dict:
        return {
            "achievements": {
                aid: ach.to_dict()
                for aid, ach in self.achievements.items()
            }
        }

    def load_from_dict(self, data: dict):
        if "achievements" not in data:
            return
        for aid, ach_data in data["achievements"].items():
            if aid in self.achievements:
                self.achievements[aid].unlocked = ach_data.get("unlocked", False)
                self.achievements[aid].unlocked_at_day = ach_data.get("unlocked_at_day")
