from dataclasses import dataclass, field
from typing import Optional
import random


@dataclass
class Henchman:
    name: str
    role: str
    level: int
    combat_skill: int
    stealth_skill: int
    loyalty: int = 100
    experience: int = 0
    salary_per_day: int = 0
    equipment: list[str] = field(default_factory=list)
    special_abilities: list[str] = field(default_factory=list)
    status: str = "active"
    days_employed: int = 0

    def gain_loyalty(self, amount: int) -> None:
        self.loyalty = min(100, self.loyalty + amount)

    def lose_loyalty(self, amount: int) -> None:
        self.loyalty -= amount
        if self.loyalty <= 0:
            self.status = "betrayed"
        elif self.loyalty < 30:
            self.status = "unhappy"

    def gain_experience(self, amount: int) -> None:
        self.experience += amount
        if self.experience >= 100 * self.level:
            self.level += 1
            self.combat_skill += 2
            self.stealth_skill += 1

    def can_work(self) -> bool:
        return self.status == "active" and self.salary_per_day <= 0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "role": self.role,
            "level": self.level,
            "combat_skill": self.combat_skill,
            "stealth_skill": self.stealth_skill,
            "loyalty": self.loyalty,
            "experience": self.experience,
            "salary_per_day": self.salary_per_day,
            "equipment": self.equipment,
            "special_abilities": self.special_abilities,
            "status": self.status,
            "days_employed": self.days_employed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Henchman":
        return cls(**data)


class HenchmanRecruiter:
    RECRUITABLE_HENCHMEN = [
        {
            "name": "Vinnie",
            "role": "Driver",
            "combat_skill": 8,
            "stealth_skill": 12,
            "salary_per_day": 50,
            "special_abilities": ["getaway_driver", "vehicle_expert"],
            "description": "Ein erfahrener Fluchtwagen-Fahrer."
        },
        {
            "name": "Maria",
            "role": "Medic",
            "combat_skill": 5,
            "stealth_skill": 10,
            "salary_per_day": 75,
            "special_abilities": ["field_medic", "healing"],
            "description": "Eine ehemalige Krankenschwester mit dunkler Seite."
        },
        {
            "name": "Tank",
            "role": "Enforcer",
            "combat_skill": 18,
            "stealth_skill": 3,
            "salary_per_day": 100,
            "special_abilities": ["intimidation", "heavy_weapons"],
            "description": "Ein massiver Mann für schmutzige Arbeit."
        },
        {
            "name": "Silent Sam",
            "role": "Assassin",
            "combat_skill": 15,
            "stealth_skill": 20,
            "salary_per_day": 150,
            "special_abilities": ["silent_kill", "disguise"],
            "description": "Ein Meister der lautlosen Eliminierung."
        },
        {
            "name": "Fixer Pete",
            "role": "Tech Expert",
            "combat_skill": 4,
            "stealth_skill": 15,
            "salary_per_day": 80,
            "special_abilities": ["hacking", "surveillance_counter"],
            "description": "Ein Genie für Elektronik und Technik."
        },
        {
            "name": "Big Tony",
            "role": "Gang Leader",
            "combat_skill": 12,
            "stealth_skill": 8,
            "salary_per_day": 200,
            "special_abilities": ["gang_backup", "territory_control"],
            "description": "Führt eine kleine Gang von loyalen Männern."
        },
        {
            "name": "Nina",
            "role": "Infiltrator",
            "combat_skill": 10,
            "stealth_skill": 18,
            "salary_per_day": 120,
            "special_abilities": ["social_engineering", "information_gathering"],
            "description": "Spezialistin für Observation und Infiltration."
        },
        {
            "name": "Mick the Knife",
            "role": "Getaway Expert",
            "combat_skill": 10,
            "stealth_skill": 14,
            "salary_per_day": 90,
            "special_abilities": ["vehicle_thief", "route_planning"],
            "description": "Kennt jeden Winkel von Vice City."
        },
    ]

    def __init__(self):
        self.available_henchmen: list[dict] = []
        self._initialize_recruits()

    def _initialize_recruits(self):
        self.available_henchmen = [h for h in self.RECRUITABLE_HENCHMEN]

    def get_available_recruits(self, cash: int, reputation: int) -> list[dict]:
        available = []
        for henchman in self.available_henchmen:
            hire_cost = self.get_hire_cost(henchman)
            min_rep = self.get_minimum_reputation(henchman)
            if cash >= hire_cost and reputation >= min_rep:
                available.append({**henchman, "hire_cost": hire_cost})
        return available

    def get_hire_cost(self, henchman: dict) -> int:
        base_cost = henchman["salary_per_day"] * 5
        skill_bonus = (henchman["combat_skill"] + henchman["stealth_skill"]) * 5
        return base_cost + skill_bonus

    def get_minimum_reputation(self, henchman: dict) -> int:
        role_reqs = {
            "Driver": 5,
            "Medic": 10,
            "Enforcer": 20,
            "Assassin": 30,
            "Tech Expert": 15,
            "Gang Leader": 40,
            "Infiltrator": 25,
            "Getaway Expert": 10,
        }
        return role_reqs.get(henchman["role"], 0)

    def recruit(self, henchman_data: dict, protagonist) -> tuple[bool, str, Optional[Henchman]]:
        hire_cost = self.get_hire_cost(henchman_data)

        if protagonist.cash < hire_cost:
            return False, f"Nicht genug Geld. Du brauchst ${hire_cost}.", None

        if hasattr(protagonist, "henchmen") and len(protagonist.henchmen) >= 5:
            return False, "Du hast bereits 5 Henchmen. Entlass einen zuerst.", None

        protagonist.cash -= hire_cost

        henchman = Henchman(
            name=henchman_data["name"],
            role=henchman_data["role"],
            level=1,
            combat_skill=henchman_data["combat_skill"],
            stealth_skill=henchman_data["stealth_skill"],
            salary_per_day=henchman_data["salary_per_day"],
            special_abilities=henchman_data.get("special_abilities", []),
        )

        if henchman_data["name"] in [h["name"] for h in self.available_henchmen]:
            self.available_henchmen = [h for h in self.available_henchmen if h["name"] != henchman_data["name"]]

        return True, f"{henchman.name} wurde rekrutiert!", henchman

    def dismiss(self, henchman: Henchman, protagonist) -> int:
        severance = henchman.salary_per_day * 3
        protagonist.cash -= severance
        return severance


class HenchmanManager:
    def __init__(self):
        self.henchmen: list[Henchman] = []
        self.max_henchmen: int = 5

    def add_henchman(self, henchman: Henchman) -> bool:
        if len(self.henchmen) >= self.max_henchmen:
            return False
        self.henchmen.append(henchman)
        return True

    def remove_henchman(self, henchman_name: str) -> Optional[Henchman]:
        for i, h in enumerate(self.henchmen):
            if h.name == henchman_name:
                return self.henchmen.pop(i)
        return None

    def get_henchman(self, name: str) -> Optional[Henchman]:
        for h in self.henchmen:
            if h.name == name:
                return h
        return None

    def get_all_henchmen(self) -> list[Henchman]:
        return self.henchmen

    def get_active_henchmen(self) -> list[Henchman]:
        return [h for h in self.henchmen if h.status == "active"]

    def get_available_henchmen_by_role(self, role: str) -> list[Henchman]:
        return [h for h in self.henchmen if h.role == role and h.status == "active"]

    def pay_salaries(self, protagonist) -> int:
        total_salary = sum(h.salary_per_day for h in self.henchmen)
        if protagonist.cash >= total_salary:
            protagonist.cash -= total_salary
            for h in self.henchmen:
                h.days_employed += 1
                if random.random() < 0.1:
                    h.gain_experience(10)
        else:
            for h in self.henchmen:
                h.lose_loyalty(20)
            print("\n[WARNUNG] Du konntest nicht alle Gehälter zahlen!")
        return total_salary

    def perform_action(self, henchman: Henchman, action: str, protagonist) -> bool:
        if henchman.status != "active":
            return False

        success = random.random()
        skill_bonus = (henchman.combat_skill if action == "combat" else henchman.stealth_skill) * 0.02
        loyalty_factor = henchman.loyalty * 0.005
        base_chance = 0.5 + skill_bonus + loyalty_factor

        if success < base_chance:
            if action == "combat":
                protagonist.stamina = max(0, protagonist.stamina - 3)
                henchman.gain_experience(25)
            elif action == "stealth":
                henchman.gain_experience(20)

            if henchman.loyalty < 50:
                henchman.lose_loyalty(5)
            else:
                henchman.gain_experience(10)
            return True

        henchman.lose_loyalty(15)
        return False

    def send_on_mission(self, henchman: Henchman, mission_type: str, protagonist) -> tuple[bool, str]:
        action_map = {
            "patrol": "stealth",
            "scout": "stealth",
            "guard": "combat",
            "attack": "combat",
            "gather_intel": "stealth",
        }

        action = action_map.get(mission_type, "combat")
        success = self.perform_action(henchman, action, protagonist)

        if success:
            rewards = {
                "patrol": (50, 10),
                "scout": (30, 20),
                "guard": (0, 30),
                "attack": (100, 50),
                "gather_intel": (20, 40),
            }
            cash, rep = rewards.get(mission_type, (50, 20))
            protagonist.cash += cash
            protagonist.reputation += rep
            return True, f"{henchman.name} hat die Mission erfolgreich abgeschlossen!"
        else:
            return False, f"{henchman.name} ist bei der Mission gescheitert. Er verliert etwas Loyalität."

    def handle_betrayal(self, henchman: Henchman, protagonist) -> None:
        betrayal_loss = random.randint(100, 300)
        protagonist.cash = max(0, protagonist.cash - betrayal_loss)
        protagonist.reputation = max(0, protagonist.reputation - 20)
        print(f"\n[EREIGNIS] {henchman.name} hat dich verraten und ${betrayal_loss} gestohlen!")

    def to_dict(self) -> dict:
        return {
            "henchmen": [h.to_dict() for h in self.henchmen],
            "max_henchmen": self.max_henchmen,
        }

    def load_from_dict(self, data: dict) -> None:
        if "henchmen" in data:
            self.henchmen = [Henchman.from_dict(h) for h in data["henchmen"]]
        if "max_henchmen" in data:
            self.max_henchmen = data["max_henchmen"]


class NPCContact:
    def __init__(self, name: str, role: str, location: str, relationship: int = 0):
        self.name = name
        self.role = role
        self.location = location
        self.relationship = relationship
        self.last_contact: int = 0
        self.available_services: list[str] = []

    def improve_relationship(self, amount: int) -> None:
        self.relationship = min(100, self.relationship + amount)

    def worsen_relationship(self, amount: int) -> None:
        self.relationship -= amount

    def can_provide_service(self, service: str) -> bool:
        return service in self.available_services and self.relationship >= 20

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "role": self.role,
            "location": self.location,
            "relationship": self.relationship,
            "last_contact": self.last_contact,
            "available_services": self.available_services,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NPCContact":
        return cls(**data)