from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class FactionType(Enum):
    CRIMINAL = "criminal"
    LAW_ENFORCEMENT = "law_enforcement"
    CIVILIAN = "civilian"
    CORPORATE = "corporate"
    GANGS = "gangs"


@dataclass
class Faction:
    name: str
    faction_type: FactionType
    description: str
    reputation: int = 0
    influence: int = 0
    hostility: int = 0
    allied_factions: list[str] = field(default_factory=list)
    enemy_factions: list[str] = field(default_factory=list)
    available_services: list[str] = field(default_factory=list)
    special_requirements: list[str] = field(default_factory=list)

    def is_hostile(self) -> bool:
        return self.hostility >= 50

    def is_allied(self) -> bool:
        return self.reputation >= 50

    def can_access_services(self, reputation: int, level: int = 1) -> bool:
        for req in self.special_requirements:
            if req.startswith("rep:"):
                min_rep = int(req.split(":")[1])
                if reputation < min_rep:
                    return False
            elif req.startswith("level:"):
                min_level = int(req.split(":")[1])
                if level < min_level:
                    return False
        return True

    def get_service_cost(self, service: str, base_price: int) -> int:
        if not self.is_allied():
            modifier = 1.0 + (self.hostility * 0.01)
        else:
            modifier = 0.8
        return int(base_price * modifier)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "faction_type": self.faction_type.value,
            "description": self.description,
            "reputation": self.reputation,
            "influence": self.influence,
            "hostility": self.hostility,
            "allied_factions": self.allied_factions,
            "enemy_factions": self.enemy_factions,
            "available_services": self.available_services,
            "special_requirements": self.special_requirements,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Faction":
        return cls(
            name=data["name"],
            faction_type=FactionType(data.get("faction_type", "criminal")),
            description=data.get("description", ""),
            reputation=data.get("reputation", 0),
            influence=data.get("influence", 0),
            hostility=data.get("hostility", 0),
            allied_factions=data.get("allied_factions", []),
            enemy_factions=data.get("enemy_factions", []),
            available_services=data.get("available_services", []),
            special_requirements=data.get("special_requirements", []),
        )


class FactionManager:
    def __init__(self):
        self.factions: dict[str, Faction] = {}
        self.protagonist_relations: dict[str, int] = {}
        self._initialize_factions()

    def _initialize_factions(self):
        self.factions = {
            "vice_city_mafia": Faction(
                name="Vice City Mafia",
                faction_type=FactionType.CRIMINAL,
                description="Die mächtige organisierte Kriminalität von Vice City. Respekt wird erwartet.",
                reputation=0,
                available_services=["protection", "business_deals", "weapon_supply"],
                special_requirements=["rep:20", "level:3"],
            ),
            "biker_gang": Faction(
                name="The Vice City Biker Gang",
                faction_type=FactionType.CRIMINAL,
                description="Motorrad-Gangs, die die Straßen kontrollieren. Loyalität ist alles.",
                reputation=0,
                allied_factions=["vice_city_mafia"],
                enemy_factions=["vice_city_cartel"],
                available_services=["territory_access", "smuggling_routes", "combat_support"],
                special_requirements=["rep:15", "level:2"],
            ),
            "vice_city_cartel": Faction(
                name="Vice City Kartell",
                faction_type=FactionType.CRIMINAL,
                description="Drogenimperium mit internationalen Verbindungen.",
                reputation=0,
                enemy_factions=["biker_gang", "police_department"],
                available_services=["drug_network", "corruption", "hit_contracts"],
                special_requirements=["rep:25", "level:4"],
            ),
            "police_department": Faction(
                name="Vice City Polizei",
                faction_type=FactionType.LAW_ENFORCEMENT,
                description="Die Strafverfolgungsbehörden. Korrupt oder ehrlich?",
                reputation=0,
                hostility=30,
                enemy_factions=["vice_city_cartel", "vice_city_mafia"],
                available_services=["crime_reporting", "evidence_removal", "safe_house"],
                special_requirements=["level:5"],
            ),
            "federal_agency": Faction(
                name="Föderale Behörde",
                faction_type=FactionType.LAW_ENFORCEMENT,
                description="FBI und DEA - die großen Jäger. Umsonst arbeiten sie nicht.",
                reputation=0,
                hostility=50,
                enemy_factions=["vice_city_cartel", "vice_city_mafia"],
                available_services=["witness_protection", "intel_sharing", "case_drops"],
                special_requirements=["rep:40", "level:6"],
            ),
            "corrupt_politicians": Faction(
                name="Korrupte Politiker",
                faction_type=FactionType.CORPORATE,
                description="Die dunkle Seite der Politik. Für den richtigen Preis.",
                reputation=0,
                available_services=["license_approvals", "zoning_changes", "media_control"],
                special_requirements=["rep:30", "level:5"],
            ),
            "business_association": Faction(
                name="Geschäftsverband",
                faction_type=FactionType.CIVILIAN,
                description="Die legitime Geschäftswelt. Misstrauisch gegenüber Kriminellen.",
                reputation=0,
                hostility=20,
                available_services=["business_license", "property_access", "investment_opportunities"],
                special_requirements=["rep:10"],
            ),
            "street_gangs": Faction(
                name="Straßengangs",
                faction_type=FactionType.GANGS,
                description="Viele kleine Gangs, die um Territorium kämpfen.",
                reputation=0,
                available_services=["street_intel", "lookout_network", "distraction_operations"],
                special_requirements=["rep:5"],
            ),
        }

        for faction_name in self.factions:
            self.protagonist_relations[faction_name] = 0

    def get_faction(self, name: str) -> Optional[Faction]:
        return self.factions.get(name)

    def get_all_factions(self) -> list[Faction]:
        return list(self.factions.values())

    def get_faction_by_type(self, faction_type: FactionType) -> list[Faction]:
        return [f for f in self.factions.values() if f.faction_type == faction_type]

    def modify_reputation(self, faction_name: str, amount: int) -> int:
        faction = self.factions.get(faction_name)
        if not faction:
            return 0

        faction.reputation = max(-100, min(100, faction.reputation + amount))
        self.protagonist_relations[faction_name] = faction.reputation

        if faction.reputation >= 50:
            faction.allied_factions.append(faction_name)
        elif faction.reputation <= -50:
            faction.hostility = min(100, faction.hostility + abs(amount))

        return faction.reputation

    def modify_hostility(self, faction_name: str, amount: int) -> int:
        faction = self.factions.get(faction_name)
        if not faction:
            return 0

        faction.hostility = max(0, min(100, faction.hostility + amount))
        return faction.hostility

    def get_protagonist_relation(self, faction_name: str) -> int:
        return self.protagonist_relations.get(faction_name, 0)

    def get_faction_status(self, faction_name: str) -> str:
        faction = self.factions.get(faction_name)
        if not faction:
            return "Unbekannt"

        if faction.reputation >= 75:
            return "Verbündeter"
        elif faction.reputation >= 25:
            return "Freundlich"
        elif faction.reputation >= -25:
            return "Neutral"
        elif faction.reputation >= -75:
            return "Misstrauisch"
        else:
            return "Feind"

    def can_use_service(self, faction_name: str, service: str, protagonist) -> bool:
        faction = self.factions.get(faction_name)
        if not faction:
            return False

        if service not in faction.available_services:
            return False

        if faction.is_hostile():
            return False

        if not faction.can_access_services(protagonist.reputation, protagonist.level):
            return False

        return True

    def get_allied_factions(self) -> list[Faction]:
        return [f for f in self.factions.values() if f.is_allied()]

    def get_hostile_factions(self) -> list[Faction]:
        return [f for f in self.factions.values() if f.is_hostile()]

    def perform_faction_action(self, faction_name: str, action: str, protagonist) -> bool:
        faction = self.factions.get(faction_name)
        if not faction or not self.can_use_service(faction_name, action, protagonist):
            return False

        if action == "protection":
            protagonist.wanted_level = max(0, protagonist.wanted_level - 1)
            return True
        elif action == "combat_support":
            protagonist.stamina = min(protagonist.level * 25, protagonist.stamina + 10)
            return True
        elif action == "intel_sharing":
            print("\n[INFO] Du erhältst wertvolle Informationen über einen Gegner.")
            return True
        elif action == "safe_house":
            protagonist.stamina = protagonist.level * 25
            protagonist.stress_level = max(0, protagonist.stress_level - 20)
            return True

        return False

    def trigger_faction_event(self, faction_name: str, event_type: str, protagonist) -> None:
        faction = self.factions.get(faction_name)
        if not faction:
            return

        if event_type == "betrayal":
            faction.reputation = max(-100, faction.reputation - 30)
            faction.hostility = min(100, faction.hostility + 40)
            print(f"\n[EREIGNIS] {faction.name} hat deinen Verrat bemerkt!")
        elif event_type == "ally_benefit":
            faction.reputation = min(100, faction.reputation + 10)
            print(f"\n[EREIGNIS] {faction.name} schätzt deine Hilfe!")
        elif event_type == "witness":
            faction.reputation = min(100, faction.reputation + 5)
            print(f"\n[EREIGNIS] {faction.name} hat deine Taten bemerkt.")

    def to_dict(self) -> dict:
        return {
            "factions": {name: faction.to_dict() for name, faction in self.factions.items()},
            "protagonist_relations": self.protagonist_relations,
        }

    def load_from_dict(self, data: dict) -> None:
        if "factions" in data:
            self.factions = {
                name: Faction.from_dict(faction_data)
                for name, faction_data in data["factions"].items()
            }
        if "protagonist_relations" in data:
            self.protagonist_relations = data["protagonist_relations"]

    def get_faction_summary(self) -> str:
        summary = "\n[FRAKTIONEN] Übersicht:\n"
        for faction in self.factions.values():
            status = self.get_faction_status(faction.name)
            summary += f"  {faction.name}: {status} (Rep: {faction.reputation}, Feindseligkeit: {faction.hostility})\n"
        return summary