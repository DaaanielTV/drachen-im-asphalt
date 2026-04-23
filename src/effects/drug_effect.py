import random
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class DrugEffect:
    name: str
    intensity: float
    duration: int
    remaining: int = 0
    drug_type: str = "stimulant"
    effects: Optional[dict] = None

    def __post_init__(self):
        if self.remaining == 0:
            self.remaining = self.duration
        if self.effects is None:
            self.effects = {}

    def apply_effect(self, protagonist):
        if self.remaining > 0:
            if hasattr(protagonist, "stress_level"):
                stress_shift = int((self.intensity * 6) - 1)
                protagonist.stress_level = min(100, max(0, protagonist.stress_level + stress_shift))

            if self.intensity > 0.6 and random.random() < self.intensity:
                return self.trigger_dragon_hallucination(protagonist)
            self.remaining -= 1
        return False

    def trigger_dragon_hallucination(self, protagonist):
        hallucinations = [
            "Ein feuerspeiender Drache taucht am Horizont von Vice City auf...",
            "Drachenschatten tanzen auf den nassen Straßen von Ocean Beach...",
            "Du hörst das Brüllen eines Drachen im Wind der Everglades...",
            "Die Neonlichter von Vice City formen sich zu Drachenaugen...",
            "Ein Drache fliegt über die Wolkenkratzer von Downtown Vice City..."
        ]
        print(f"\n[DRACHE] DROGEN-HALLUZINATION: {random.choice(hallucinations)}")
        print("Deine Wahrnehmung ist verzerrt. Die Konsequenzen deines Lebens jagen dich...\n")
        time.sleep(2)
        return True

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "intensity": self.intensity,
            "duration": self.duration,
            "remaining": self.remaining,
            "drug_type": self.drug_type,
            "effects": self.effects or {},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DrugEffect":
        return cls(
            name=data["name"],
            intensity=data["intensity"],
            duration=data["duration"],
            remaining=data.get("remaining", data["duration"]),
            drug_type=data.get("drug_type", "stimulant"),
            effects=data.get("effects", {}),
        )


class DrugCatalog:
    STIMULANTS = [
        {
            "name": "Koffein",
            "intensity": 0.1,
            "duration": 3,
            "drug_type": "stimulant",
            "cost": 10,
            "description": "Eine Tasse Kaffee. Steigert die Wachsamkeit.",
            "effects": {
                "stamina_bonus": 5,
                "reaction_bonus": 0.05,
                "stress_modifier": 1.0,
            }
        },
        {
            "name": "Speed",
            "intensity": 0.4,
            "duration": 5,
            "drug_type": "stimulant",
            "cost": 80,
            "description": "Amphetamin. Bringt dich auf Hochtouren.",
            "effects": {
                "stamina_bonus": 15,
                "combat_bonus": 0.15,
                "stealth_penalty": 0.1,
                "stress_modifier": 1.3,
            }
        },
        {
            "name": "Crack",
            "intensity": 0.7,
            "duration": 3,
            "drug_type": "stimulant",
            "cost": 150,
            "description": "Rauchbares Kokain. Intensive, aber kurze Wirkung.",
            "effects": {
                "stamina_bonus": 20,
                "combat_bonus": 0.25,
                "perception_distortion": True,
                "stress_modifier": 1.8,
            }
        },
    ]

    DEPRESSANTS = [
        {
            "name": "Alkohol",
            "intensity": 0.2,
            "duration": 4,
            "drug_type": "depressant",
            "cost": 20,
            "description": "Ein paar Drinks. Locker, aber langsam.",
            "effects": {
                "stress_reduction": 10,
                "combat_penalty": 0.1,
                "stealth_bonus": 0.05,
                "stress_modifier": 0.8,
            }
        },
        {
            "name": "Valium",
            "intensity": 0.3,
            "duration": 6,
            "drug_type": "depressant",
            "cost": 50,
            "description": "Beruhigungsmittel. Dämpft die Nerven.",
            "effects": {
                "stress_reduction": 20,
                "perception_penalty": 0.1,
                "stealth_bonus": 0.1,
                "stress_modifier": 0.6,
            }
        },
        {
            "name": "Heroin",
            "intensity": 0.8,
            "duration": 8,
            "drug_type": "depressant",
            "cost": 300,
            "description": "Opiat. Totaler Runner. Suchtgefahr!",
            "effects": {
                "stress_reduction": 40,
                "stamina_penalty": 10,
                "combat_penalty": 0.3,
                "hallucination_chance": 0.4,
                "stress_modifier": 0.3,
            }
        },
    ]

    HALLUCINOGENS = [
        {
            "name": "Pillen",
            "intensity": 0.5,
            "duration": 5,
            "drug_type": "hallucinogen",
            "cost": 100,
            "description": "LSD-Trips. Verzerrte Wahrnehmung.",
            "effects": {
                "perception_distortion": True,
                "hallucination_chance": 0.6,
                "stealth_penalty": 0.3,
                "stress_modifier": 1.5,
            }
        },
        {
            "name": "Magic Mushrooms",
            "intensity": 0.4,
            "duration": 4,
            "drug_type": "hallucinogen",
            "cost": 60,
            "description": "Psilocybin-Pilze. Natürliche Halluzinationen.",
            "effects": {
                "hallucination_chance": 0.5,
                "time_distortion": True,
                "stress_modifier": 1.3,
            }
        },
        {
            "name": "Angel Dust",
            "intensity": 0.9,
            "duration": 6,
            "drug_type": "hallucinogen",
            "cost": 200,
            "description": "PCP. Extrem gefährlich! Massive Halluzinationen.",
            "effects": {
                "hallucination_chance": 0.9,
                "combat_bonus": 0.2,
                "combat_penalty": 0.2,
                "perception_distortion": True,
                "stress_modifier": 2.0,
            }
        },
    ]

    MEDICAL = [
        {
            "name": "Schmerzmittel",
            "intensity": 0.2,
            "duration": 3,
            "drug_type": "medical",
            "cost": 40,
            "description": "Verschreibungspflichtige Medikamente.",
            "effects": {
                "stamina_bonus": 10,
                "stress_reduction": 5,
                "stress_modifier": 0.9,
            }
        },
        {
            "name": "Adrenalin-Spritze",
            "intensity": 0.5,
            "duration": 2,
            "drug_type": "medical",
            "cost": 120,
            "description": "Notfall-Adrenalin. Kurzzeitige Super-Konzentration.",
            "effects": {
                "stamina_bonus": 25,
                "combat_bonus": 0.3,
                "reaction_bonus": 0.2,
                "stress_modifier": 1.4,
            }
        },
    ]

    MIXED = [
        {
            "name": "Speedball",
            "intensity": 0.8,
            "duration": 5,
            "drug_type": "mixed",
            "cost": 250,
            "description": "Kokain + Heroin. Die tödliche Mischung.",
            "effects": {
                "stamina_bonus": 15,
                "combat_bonus": 0.2,
                "hallucination_chance": 0.7,
                "stress_modifier": 2.2,
            }
        },
        {
            "name": "Drachenblut",
            "intensity": 1.0,
            "duration": 10,
            "drug_type": "special",
            "cost": 500,
            "description": "Geheime Droge der Unterwelt. Maximale Wirkung mit maximalen Risiken.",
            "effects": {
                "stamina_bonus": 30,
                "combat_bonus": 0.5,
                "stealth_bonus": 0.3,
                "hallucination_chance": 1.0,
                "dragon_intensity_boost": 0.5,
                "stress_modifier": 3.0,
            }
        },
    ]

    @classmethod
    def get_all_drugs(cls) -> list[dict]:
        all_drugs = []
        all_drugs.extend(cls.STIMULANTS)
        all_drugs.extend(cls.DEPRESSANTS)
        all_drugs.extend(cls.HALLUCINOGENS)
        all_drugs.extend(cls.MEDICAL)
        all_drugs.extend(cls.MIXED)
        return all_drugs

    @classmethod
    def get_drugs_by_type(cls, drug_type: str) -> list[dict]:
        type_map = {
            "stimulant": cls.STIMULANTS,
            "depressant": cls.DEPRESSANTS,
            "hallucinogen": cls.HALLUCINOGENS,
            "medical": cls.MEDICAL,
            "mixed": cls.MIXED,
            "special": cls.MIXED,
        }
        return type_map.get(drug_type, [])

    @classmethod
    def create_drug(cls, drug_data: dict) -> DrugEffect:
        effects = drug_data.pop("effects", {})
        drug = DrugEffect(
            name=drug_data["name"],
            intensity=drug_data["intensity"],
            duration=drug_data["duration"],
            drug_type=drug_data["drug_type"],
            effects=effects,
        )
        return drug


class DrugDealer:
    def __init__(self):
        self.catalog = DrugCatalog()
        self.market_prices = {}
        self._initialize_market()

    def _initialize_market(self):
        for drug in self.catalog.get_all_drugs():
            base_price = drug["cost"]
            variation = random.uniform(0.8, 1.2)
            self.market_prices[drug["name"]] = int(base_price * variation)

    def get_available_drugs(self, cash: int, level: int = 1) -> list[dict]:
        available = []
        for drug in self.catalog.get_all_drugs():
            required_level = self._get_required_level(drug["drug_type"])
            if level >= required_level:
                current_price = self.market_prices.get(drug["name"], drug["cost"])
                available.append({
                    **drug,
                    "current_price": current_price,
                    "affordable": current_price <= cash,
                })
        return available

    def _get_required_level(self, drug_type: str) -> int:
        level_req = {
            "stimulant": 1,
            "depressant": 2,
            "hallucinogen": 3,
            "medical": 1,
            "mixed": 4,
            "special": 5,
        }
        return level_req.get(drug_type, 1)

    def buy_drug(self, drug_name: str, protagonist) -> bool:
        for drug_data in self.catalog.get_all_drugs():
            if drug_data["name"] == drug_name:
                price = self.market_prices.get(drug_name, drug_data["cost"])
                if protagonist.cash >= price:
                    protagonist.cash -= price
                    drug = self.catalog.create_drug(drug_data)
                    protagonist.drug_effects.append(drug)

                    if hasattr(protagonist, "achievement_manager"):
                        protagonist.achievement_manager.unlock("first_drug", protagonist.days)

                    return True
        return False

    def sell_drug(self, drug_index: int, protagonist) -> bool:
        if 0 <= drug_index < len(protagonist.drug_effects):
            drug = protagonist.drug_effects[drug_index]
            base_price = 0
            for d in self.catalog.get_all_drugs():
                if d["name"] == drug.name:
                    base_price = d["cost"] // 2
                    break
            protagonist.cash += base_price
            protagonist.drug_effects.pop(drug_index)
            return True
        return False

    def update_market_prices(self) -> None:
        for drug in self.catalog.get_all_drugs():
            base_price = drug["cost"]
            variation = random.uniform(0.7, 1.3)
            self.market_prices[drug["name"]] = int(base_price * variation)

    def get_market_report(self) -> dict:
        report = {}
        for drug in self.catalog.get_all_drugs():
            price = self.market_prices.get(drug["name"], drug["cost"])
            trend = "stabil"
            if price > drug["cost"] * 1.1:
                trend = "steigend"
            elif price < drug["cost"] * 0.9:
                trend = "fallend"
            report[drug["name"]] = {
                "price": price,
                "base_price": drug["cost"],
                "trend": trend,
                "type": drug["drug_type"],
            }
        return report

    def use_drug(self, drug_index: int, protagonist) -> bool:
        if 0 <= drug_index < len(protagonist.drug_effects):
            drug = protagonist.drug_effects[drug_index]
            drug.remaining = drug.duration
            drug.apply_effect(protagonist)
            return True
        return False