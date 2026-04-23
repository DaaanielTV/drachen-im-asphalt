from dataclasses import dataclass, field
from typing import Optional
import random


@dataclass
class WeaponStats:
    damage: int
    accuracy: float
    fire_rate: float
    range_bonus: int
    stealth_modifier: float


@dataclass
class Weapon:
    name: str
    cost: int
    damage_increase: int
    illegal_status: bool
    weapon_type: str = "melee"
    stats: Optional[WeaponStats] = None
    description: str = ""
    ammo_type: str = "none"
    max_ammo: int = 0
    current_ammo: int = 0

    def __post_init__(self):
        if self.stats is None:
            self.stats = WeaponStats(
                damage=self.damage_increase,
                accuracy=0.5,
                fire_rate=1.0,
                range_bonus=0,
                stealth_modifier=1.0
            )

    def can_fire(self) -> bool:
        if self.ammo_type == "none":
            return True
        return self.current_ammo > 0

    def fire(self) -> bool:
        if self.can_fire():
            if self.ammo_type != "none":
                self.current_ammo -= 1
            return True
        return False

    def reload(self, amount: int) -> None:
        if self.ammo_type != "none":
            self.current_ammo = min(self.max_ammo, self.current_ammo + amount)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "cost": self.cost,
            "damage_increase": self.damage_increase,
            "illegal_status": self.illegal_status,
            "weapon_type": self.weapon_type,
            "description": self.description,
            "ammo_type": self.ammo_type,
            "max_ammo": self.max_ammo,
            "current_ammo": self.current_ammo,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Weapon":
        return cls(**data)


class WeaponCatalog:
    MELEE_WEAPONS = [
        {
            "name": "Faust",
            "cost": 0,
            "damage_increase": 2,
            "illegal_status": False,
            "weapon_type": "melee",
            "description": "Deine nackten Hände. Besser als nichts.",
            "stats": WeaponStats(damage=2, accuracy=0.6, fire_rate=2.0, range_bonus=0, stealth_modifier=1.5)
        },
        {
            "name": "Messer",
            "cost": 50,
            "damage_increase": 5,
            "illegal_status": True,
            "weapon_type": "melee",
            "description": "Ein scharfes Taschenmesser. Schnell und leise.",
            "stats": WeaponStats(damage=5, accuracy=0.7, fire_rate=2.5, range_bonus=0, stealth_modifier=2.0)
        },
        {
            "name": "Baseballschläger",
            "cost": 80,
            "damage_increase": 8,
            "illegal_status": False,
            "weapon_type": "melee",
            "description": "Solide Waffe mit ordentlich Wucht.",
            "stats": WeaponStats(damage=8, accuracy=0.5, fire_rate=1.5, range_bonus=1, stealth_modifier=1.2)
        },
        {
            "name": "Ketten",
            "cost": 120,
            "damage_increase": 10,
            "illegal_status": False,
            "weapon_type": "melee",
            "description": "Eine schwere Kette. Ziemlich einschüchternd.",
            "stats": WeaponStats(damage=10, accuracy=0.4, fire_rate=1.2, range_bonus=1, stealth_modifier=0.8)
        },
    ]

    HANDGUNS = [
        {
            "name": "Pistole",
            "cost": 200,
            "damage_increase": 15,
            "illegal_status": True,
            "weapon_type": "handgun",
            "description": "Eine zuverlässige 9mm Pistole.",
            "ammo_type": "9mm",
            "max_ammo": 12,
            "current_ammo": 12,
            "stats": WeaponStats(damage=15, accuracy=0.7, fire_rate=1.0, range_bonus=3, stealth_modifier=0.5)
        },
        {
            "name": "Revolver",
            "cost": 350,
            "damage_increase": 25,
            "illegal_status": True,
            "weapon_type": "handgun",
            "description": "Ein mächtiger Revolver mit enormer Durchschlagskraft.",
            "ammo_type": ".45",
            "max_ammo": 6,
            "current_ammo": 6,
            "stats": WeaponStats(damage=25, accuracy=0.6, fire_rate=0.6, range_bonus=4, stealth_modifier=0.3)
        },
        {
            "name": "Schalldämpfer-Pistole",
            "cost": 500,
            "damage_increase": 12,
            "illegal_status": True,
            "weapon_type": "handgun",
            "description": "Leise und tödlich. Für diskrete Einsätze.",
            "ammo_type": "9mm",
            "max_ammo": 12,
            "current_ammo": 12,
            "stats": WeaponStats(damage=12, accuracy=0.75, fire_rate=1.0, range_bonus=2, stealth_modifier=1.5)
        },
    ]

    RIFLES = [
        {
            "name": "Schrotflinte",
            "cost": 600,
            "damage_increase": 35,
            "illegal_status": True,
            "weapon_type": "shotgun",
            "description": "Pump-Action Schrotflinte. Verheerend auf kurze Distanz.",
            "ammo_type": "shotgun_shell",
            "max_ammo": 8,
            "current_ammo": 8,
            "stats": WeaponStats(damage=35, accuracy=0.4, fire_rate=0.5, range_bonus=2, stealth_modifier=0.2)
        },
        {
            "name": "Maschinenpistole",
            "cost": 800,
            "damage_increase": 20,
            "illegal_status": True,
            "weapon_type": "smg",
            "description": "Schnellfeuer für unterdrückende Gewalt.",
            "ammo_type": "9mm",
            "max_ammo": 30,
            "current_ammo": 30,
            "stats": WeaponStats(damage=20, accuracy=0.5, fire_rate=3.0, range_bonus=3, stealth_modifier=0.1)
        },
        {
            "name": " Sturmgewehr",
            "cost": 1200,
            "damage_increase": 30,
            "illegal_status": True,
            "weapon_type": "rifle",
            "description": "Militärisches Sturmgewehr. Hohe Feuerkraft.",
            "ammo_type": "556",
            "max_ammo": 30,
            "current_ammo": 30,
            "stats": WeaponStats(damage=30, accuracy=0.7, fire_rate=2.0, range_bonus=5, stealth_modifier=0.05)
        },
        {
            "name": "Scharfschützengewehr",
            "cost": 1500,
            "damage_increase": 50,
            "illegal_status": True,
            "weapon_type": "sniper",
            "description": "Für präzise Langstrecken-Schüsse.",
            "ammo_type": "762",
            "max_ammo": 5,
            "current_ammo": 5,
            "stats": WeaponStats(damage=50, accuracy=0.9, fire_rate=0.3, range_bonus=10, stealth_modifier=0.05)
        },
    ]

    EXPLOSIVES = [
        {
            "name": "Molotow-Cocktail",
            "cost": 100,
            "damage_increase": 20,
            "illegal_status": True,
            "weapon_type": "explosive",
            "description": "Selbstgemachter Brandsatz. Feuerschaden.",
            "stats": WeaponStats(damage=20, accuracy=0.3, fire_rate=0.2, range_bonus=2, stealth_modifier=0.1)
        },
        {
            "name": "Granate",
            "cost": 250,
            "damage_increase": 40,
            "illegal_status": True,
            "weapon_type": "explosive",
            "description": "Konzentrierte Explosivkraft.",
            "stats": WeaponStats(damage=40, accuracy=0.5, fire_rate=0.1, range_bonus=3, stealth_modifier=0.1)
        },
        {
            "name": "C4-Explosiv",
            "cost": 500,
            "damage_increase": 60,
            "illegal_status": True,
            "weapon_type": "explosive",
            "description": "Plastiksprengstoff. Professionelle Sprengung.",
            "stats": WeaponStats(damage=60, accuracy=0.8, fire_rate=0.1, range_bonus=5, stealth_modifier=0.2)
        },
    ]

    SPECIAL = [
        {
            "name": "Schlagstock",
            "cost": 100,
            "damage_increase": 6,
            "illegal_status": False,
            "weapon_type": "melee",
            "description": "Teleskop-Schlagstock. Zusammensteckbar.",
            "stats": WeaponStats(damage=6, accuracy=0.6, fire_rate=2.0, range_bonus=2, stealth_modifier=1.5)
        },
        {
            "name": "Elektroschocker",
            "cost": 150,
            "damage_increase": 4,
            "illegal_status": True,
            "weapon_type": "special",
            "description": "Lähmt Gegner kurzzeitig. Nicht tödlich.",
            "stats": WeaponStats(damage=4, accuracy=0.8, fire_rate=1.0, range_bonus=1, stealth_modifier=1.8)
        },
        {
            "name": "Rauchgranate",
            "cost": 80,
            "damage_increase": 0,
            "illegal_status": True,
            "weapon_type": "tactical",
            "description": "Erzeugt Rauch. Gut für Fluchtversuche.",
            "stats": WeaponStats(damage=0, accuracy=0.7, fire_rate=0.3, range_bonus=3, stealth_modifier=2.0)
        },
    ]

    @classmethod
    def get_all_weapons(cls) -> list[dict]:
        all_weapons = []
        all_weapons.extend(cls.MELEE_WEAPONS)
        all_weapons.extend(cls.HANDGUNS)
        all_weapons.extend(cls.RIFLES)
        all_weapons.extend(cls.EXPLOSIVES)
        all_weapons.extend(cls.SPECIAL)
        return all_weapons

    @classmethod
    def get_weapons_by_type(cls, weapon_type: str) -> list[dict]:
        type_map = {
            "melee": cls.MELEE_WEAPONS,
            "handgun": cls.HANDGUNS,
            "rifle": cls.RIFLES,
            "shotgun": [w for w in cls.RIFLES if w["weapon_type"] == "shotgun"],
            "smg": [w for w in cls.RIFLES if w["weapon_type"] == "smg"],
            "sniper": [w for w in cls.RIFLES if w["weapon_type"] == "sniper"],
            "explosive": cls.EXPLOSIVES,
            "special": cls.SPECIAL,
        }
        return type_map.get(weapon_type, [])

    @classmethod
    def create_weapon(cls, weapon_data: dict) -> Weapon:
        stats_data = weapon_data.pop("stats", None)
        weapon = Weapon(**weapon_data)
        if stats_data:
            weapon.stats = WeaponStats(**stats_data)
        return weapon


class AmmoPrices:
    PRICES = {
        "9mm": 10,
        ".45": 15,
        "shotgun_shell": 8,
        "556": 20,
        "762": 25,
    }


class WeaponDealer:
    def __init__(self):
        self.catalog = WeaponCatalog()

    def get_available_weapons(self, cash: int, level: int = 1) -> list[Weapon]:
        weapons = []
        for w_data in self.catalog.get_all_weapons():
            required_level = self._get_required_level(w_data["weapon_type"])
            if level >= required_level and w_data["cost"] <= cash * 2:
                weapons.append(self.catalog.create_weapon(w_data))
        return weapons

    def _get_required_level(self, weapon_type: str) -> int:
        level_req = {
            "melee": 1,
            "handgun": 2,
            "shotgun": 3,
            "smg": 4,
            "rifle": 5,
            "sniper": 6,
            "explosive": 4,
            "special": 3,
            "tactical": 2,
        }
        return level_req.get(weapon_type, 1)

    def get_buy_price(self, weapon: Weapon, reputation: int = 0) -> int:
        base_price = weapon.cost
        discount = reputation * 0.001
        return int(base_price * (1 - discount))

    def get_sell_price(self, weapon: Weapon, reputation: int = 0) -> int:
        base_price = weapon.cost // 3
        discount = reputation * 0.001
        return int(base_price * (1 - discount))

    def buy_weapon(self, weapon_name: str, protagonist) -> bool:
        for w_data in self.catalog.get_all_weapons():
            if w_data["name"] == weapon_name:
                weapon = self.catalog.create_weapon(w_data)
                price = self.get_buy_price(weapon, protagonist.reputation)
                if protagonist.cash >= price:
                    protagonist.cash -= price
                    protagonist.inventory.append(weapon)
                    return True
        return False

    def sell_weapon(self, weapon_index: int, protagonist) -> bool:
        if 0 <= weapon_index < len(protagonist.inventory):
            weapon = protagonist.inventory[weapon_index]
            price = self.get_sell_price(weapon, protagonist.reputation)
            protagonist.cash += price
            protagonist.inventory.pop(weapon_index)
            return True
        return False

    def repair_weapon(self, weapon_index: int, protagonist) -> bool:
        if 0 <= weapon_index < len(protagonist.inventory):
            weapon = protagonist.inventory[weapon_index]
            if weapon.ammo_type != "none":
                repair_cost = weapon.max_ammo * AmmoPrices.PRICES.get(weapon.ammo_type, 10)
                if protagonist.cash >= repair_cost:
                    protagonist.cash -= repair_cost
                    weapon.current_ammo = weapon.max_ammo
                    return True
        return False