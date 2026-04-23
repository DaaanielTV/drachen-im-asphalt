from dataclasses import dataclass, field
from typing import Optional
import random


@dataclass
class Boss:
    name: str
    boss_type: str
    description: str
    health: int
    attack_power: int
    defense: int
    special_abilities: list[str] = field(default_factory=list)
    weakness: Optional[str] = None
    phase: int = 1
    defeated: bool = False

    def take_damage(self, damage: int) -> int:
        actual_damage = max(1, damage - self.defense)
        self.health -= actual_damage
        if self.health <= 0:
            self.health = 0
            self.defeated = True
        return actual_damage

    def is_enraged(self) -> bool:
        return self.health < self.health * 0.3

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "boss_type": self.boss_type,
            "description": self.description,
            "health": self.health,
            "attack_power": self.attack_power,
            "defense": self.defense,
            "special_abilities": self.special_abilities,
            "weakness": self.weakness,
            "phase": self.phase,
            "defeated": self.defeated,
        }


class BossFactory:
    @staticmethod
    def create_boss(boss_type: str, difficulty: int = 1) -> Boss:
        bosses = {
            "gang_leader": BossFactory._create_gang_leader,
            "corrupt_official": BossFactory._create_corrupt_official,
            "rival_criminal": BossFactory._create_rival_criminal,
            "police_commander": BossFactory._create_police_commander,
            "gangster_boss": BossFactory._create_gangster_boss,
            "cartel_head": BossFactory._create_cartel_head,
        }
        creator = bosses.get(boss_type, BossFactory._create_gang_leader)
        return creator(difficulty)

    @staticmethod
    def _create_gang_leader(difficulty: int) -> Boss:
        return Boss(
            name="Rico der Hammer",
            boss_type="gang_leader",
            description="Anführer der 'Hammer-Gang'. Brutal aber berechenbar.",
            health=50 * difficulty,
            attack_power=15 + (difficulty * 5),
            defense=5 + difficulty,
            special_abilities=["intimidierung", "aoe_attack"],
            weakness="stealth"
        )

    @staticmethod
    def _create_corrupt_official(difficulty: int) -> Boss:
        return Boss(
            name="Bürgermeister V. Corruption",
            boss_type="corrupt_official",
            description="Der korrupte Bürgermeister. Hat die Polizei in seiner Tasche.",
            health=40 * difficulty,
            attack_power=10 + (difficulty * 3),
            defense=10 + (difficulty * 2),
            special_abilities=["call_backup", "bribe"],
            weakness="evidence"
        )

    @staticmethod
    def _create_rival_criminal(difficulty: int) -> Boss:
        return Boss(
            name="Killer Pete",
            boss_type="rival_criminal",
            description="Ein skrupelloser Konkurrent aus der Unterwelt.",
            health=60 * difficulty,
            attack_power=20 + (difficulty * 5),
            defense=3 + difficulty,
            special_abilities=["poison", "summon_minions"],
            weakness="melee"
        )

    @staticmethod
    def _create_police_commander(difficulty: int) -> Boss:
        return Boss(
            name="Chefinspektor Sharp",
            boss_type="police_commander",
            description="Ein gnadenloser Polizist mit Insiderwissen.",
            health=45 * difficulty,
            attack_power=12 + (difficulty * 4),
            defense=8 + (difficulty * 2),
            special_abilities=["taser", "handcuff"],
            weakness="corruption"
        )

    @staticmethod
    def _create_gangster_boss(difficulty: int) -> Boss:
        return Boss(
            name="Don Salvatore",
            boss_type="gangster_boss",
            description="Der Patenonkel der Mafia. Respekt oder Tod.",
            health=80 * difficulty,
            attack_power=18 + (difficulty * 6),
            defense=12 + (difficulty * 3),
            special_abilities=["family_loyalty", "ambush", "revenge"],
            weakness="honor"
        )

    @staticmethod
    def _create_cartel_head(difficulty: int) -> Boss:
        return Boss(
            name="El Serpentiente",
            boss_type="cartel_head",
            description="Der Anführer des Drogenkartells. Gefährlicher als der Drache.",
            health=100 * difficulty,
            attack_power=25 + (difficulty * 8),
            defense=15 + (difficulty * 4),
            special_abilities=["drug_lord", "army", "betrayal"],
            weakness="supply_line"
        )


class BossManager:
    def __init__(self):
        self.bosses: dict[str, Boss] = {}
        self.defeated_bosses: list[str] = []
        self.current_boss: Optional[Boss] = None
        self.boss_encountered_today: dict[str, bool] = {}

    def register_boss(self, boss: Boss) -> None:
        self.bosses[boss.name] = boss

    def get_boss(self, name: str) -> Optional[Boss]:
        return self.bosses.get(name)

    def get_available_bosses(self, protagonist) -> list[Boss]:
        available = []
        for boss in self.bosses.values():
            if boss.defeated:
                continue
            if boss.boss_type in self.defeated_bosses:
                continue
            if protagonist.level >= self._get_boss_level_requirement(boss.boss_type):
                available.append(boss)
        return available

    def _get_boss_level_requirement(self, boss_type: str) -> int:
        requirements = {
            "gang_leader": 2,
            "corrupt_official": 3,
            "rival_criminal": 4,
            "police_commander": 5,
            "gangster_boss": 6,
            "cartel_head": 8,
        }
        return requirements.get(boss_type, 1)

    def challenge_boss(self, boss_name: str, protagonist) -> tuple[bool, str]:
        boss = self.bosses.get(boss_name)
        if not boss:
            return False, f"Boss '{boss_name}' nicht gefunden."

        if boss.defeated:
            return False, f"{boss.name} wurde bereits besiegt."

        if protagonist.level < self._get_boss_level_requirement(boss.boss_type):
            return False, f"Du brauchst Level {self._get_boss_level_requirement(boss.boss_type)} für diesen Boss."

        self.current_boss = boss
        return True, f"{boss.name} fordert dich heraus!"

    def fight_boss(self, protagonist, weapon_damage: int, stealth_attack: bool = False) -> tuple[bool, str]:
        if not self.current_boss:
            return False, "Kein Boss zum Kämpfen."

        boss = self.current_boss
        damage = weapon_damage

        if stealth_attack:
            damage = int(damage * 1.5)

        if boss.weakness == "stealth" and stealth_attack:
            damage = int(damage * 2)
        elif boss.weakness == "melee" and not stealth_attack:
            damage = int(damage * 1.5)

        actual_damage = boss.take_damage(damage)

        if boss.defeated:
            self.defeated_bosses.append(boss.boss_type)
            self.current_boss = None
            protagonist.reputation += boss.health // 5
            return True, f"{boss.name} wurde besiegt! +{boss.health // 5} Reputation"

        boss_damage = boss.attack_power - (protagonist.combat_skill // 5)
        protagonist.stamina = max(1, protagonist.stamina - (boss_damage // 2))

        return False, f"{boss.name} erhält {actual_damage} Schaden. Noch {boss.health} HP."

    def can_flee_from_boss(self, protagonist) -> bool:
        if not self.current_boss:
            return False
        stealth_check = random.random()
        return stealth_check < (protagonist.stealth * 0.05)


class MissionTemplates:
    CHAPTER_1_MISSIONS = [
        {
            "name": "Erste Schritte",
            "description": " Lerne die Grundlagen und verdiene dein erstes Geld.",
            "type": "tutorial",
            "rewards": {"cash": 100, "reputation": 5},
            "phases": 2,
        },
        {
            "name": "Straßenkämpfe",
            "description": "Beweise dich in ein paar Schlägereien.",
            "type": "combat",
            "rewards": {"cash": 200, "reputation": 15},
            "phases": 3,
        },
        {
            "name": "Lieferung",
            "description": "Bringe ein Paket von A nach B.",
            "type": "delivery",
            "rewards": {"cash": 150, "reputation": 10},
            "phases": 2,
        },
    ]

    CHAPTER_2_MISSIONS = [
        {
            "name": "Einbruch",
            "description": "Bereche ein Haus in Vice Point.",
            "type": "stealth",
            "rewards": {"cash": 400, "reputation": 25},
            "phases": 4,
        },
        {
            "name": "Schutzgeld",
            "description": "Sammle Schutzgeld von lokalen Geschäften.",
            "type": "intimidation",
            "rewards": {"cash": 300, "reputation": 20},
            "phases": 3,
        },
        {
            "name": "Autodiebstahl",
            "description": "Klau ein paar teure Karren.",
            "type": "vehicle",
            "rewards": {"cash": 350, "reputation": 20},
            "phases": 3,
        },
    ]

    CHAPTER_3_MISSIONS = [
        {
            "name": "Razzia",
            "description": "Überfalle ein Lagerhaus.",
            "type": "raid",
            "rewards": {"cash": 600, "reputation": 35},
            "phases": 5,
        },
        {
            "name": "Geiselnahme",
            "description": "Nimm einen Geschäftsmann als Geisel.",
            "type": "kidnapping",
            "rewards": {"cash": 800, "reputation": 40},
            "phases": 4,
        },
        {
            "name": "Drogenlieferung",
            "description": "Transportiere illegale Waren.",
            "type": "smuggling",
            "rewards": {"cash": 500, "reputation": 30},
            "phases": 4,
        },
    ]

    CHAPTER_4_MISSIONS = [
        {
            "name": "Bankraub",
            "description": "Überfalle die Hauptbank von Downtown.",
            "type": "heist",
            "rewards": {"cash": 1500, "reputation": 50},
            "phases": 6,
        },
        {
            "name": "Flucht",
            "description": "Entkomme der Polizei nach einem Verbrechen.",
            "type": "escape",
            "rewards": {"cash": 400, "reputation": 25},
            "phases": 3,
        },
        {
            "name": "Erpressung",
            "description": "Erpress einen korrupten Beamten.",
            "type": "extortion",
            "rewards": {"cash": 700, "reputation": 35},
            "phases": 4,
        },
    ]

    CHAPTER_5_MISSIONS = [
        {
            "name": "Kartell-Krieg",
            "description": "Greife das Kartell an.",
            "type": "war",
            "rewards": {"cash": 2000, "reputation": 60},
            "phases": 7,
        },
        {
            "name": "Attentat",
            "description": "Eliminiere ein Ziel.",
            "type": "assassination",
            "rewards": {"cash": 1200, "reputation": 50},
            "phases": 5,
        },
        {
            "name": "Revolution",
            "description": "Übernimm die Kontrolle über Little Haiti.",
            "type": "conquest",
            "rewards": {"cash": 1800, "reputation": 70},
            "phases": 8,
        },
    ]

    CHAPTER_6_MISSIONS = [
        {
            "name": "Endspiel",
            "description": "Konfrontiere den Drachen der Konsequenzen.",
            "type": "final",
            "rewards": {"cash": 5000, "reputation": 100},
            "phases": 10,
        },
        {
            "name": "Erlösung",
            "description": "Wähle den Weg der Erlösung.",
            "type": "redemption",
            "rewards": {"cash": 3000, "reputation": 80},
            "phases": 6,
        },
    ]

    SIDE_MISSIONS = [
        {
            "name": "Straßenrennen",
            "description": "Gewinne illegale Straßenrennen.",
            "type": "racing",
            "rewards": {"cash": 250, "reputation": 15},
            "phases": 3,
        },
        {
            "name": "Schnapsideen",
            "description": "Verkauf Billig-Schnaps an Touristen.",
            "type": "scam",
            "rewards": {"cash": 200, "reputation": 10},
            "phases": 2,
        },
        {
            "name": "Finderlohn",
            "description": "Finde verlorene Gegenstände und bring sie zurück.",
            "type": "delivery",
            "rewards": {"cash": 150, "reputation": 10},
            "phases": 2,
        },
        {
            "name": "Nachtwächter",
            "description": "Bewache ein Lager für eine Nacht.",
            "type": "guard",
            "rewards": {"cash": 300, "reputation": 15},
            "phases": 2,
        },
        {
            "name": "Unterhaltung",
            "description": "Unterhalte einen Gangsterboss.",
            "type": "dialogue",
            "rewards": {"cash": 400, "reputation": 20},
            "phases": 3,
        },
    ]

    @classmethod
    def get_chapter_missions(cls, chapter: int) -> list[dict]:
        chapter_map = {
            1: cls.CHAPTER_1_MISSIONS,
            2: cls.CHAPTER_2_MISSIONS,
            3: cls.CHAPTER_3_MISSIONS,
            4: cls.CHAPTER_4_MISSIONS,
            5: cls.CHAPTER_5_MISSIONS,
            6: cls.CHAPTER_6_MISSIONS,
        }
        return chapter_map.get(chapter, [])

    @classmethod
    def get_side_missions(cls) -> list[dict]:
        return cls.SIDE_MISSIONS

    @classmethod
    def get_all_missions(cls) -> list[dict]:
        all_missions = []
        for chapter in range(1, 7):
            all_missions.extend(cls.get_chapter_missions(chapter))
        all_missions.extend(cls.get_side_missions())
        return all_missions


class MissionGenerator:
    @staticmethod
    def generate_random_mission(level: int, district: str) -> dict:
        mission_types = ["delivery", "surveillance", "extraction", "sabotage", "protection"]
        type_choice = random.choice(mission_types)

        base_rewards = {
            "delivery": {"cash": 100 + (level * 20), "reputation": 5 + level},
            "surveillance": {"cash": 80 + (level * 15), "reputation": 8 + level},
            "extraction": {"cash": 150 + (level * 25), "reputation": 10 + level},
            "sabotage": {"cash": 120 + (level * 20), "reputation": 12 + level},
            "protection": {"cash": 100 + (level * 18), "reputation": 7 + level},
        }

        descriptions = {
            "delivery": f"Liefere etwas Geheimes nach {district}.",
            "surveillance": f"Beobachte ein Ziel in {district}.",
            "extraction": f"Geheime Person aus {district} herausholen.",
            "sabotage": f"Sabotiere einen Betrieb in {district}.",
            "protection": f"Beschütze jemanden in {district}.",
        }

        return {
            "name": f"{type_choice.capitalize()}-Auftrag",
            "description": descriptions[type_choice],
            "type": type_choice,
            "rewards": base_rewards[type_choice],
            "phases": 2 + (level // 3),
            "difficulty": level,
            "district": district,
        }

    @staticmethod
    def generate_heist_mission(level: int, target: str) -> dict:
        return {
            "name": f"Einbruch: {target}",
            "description": f"Plane und führe einen Einbruch bei {target} durch.",
            "type": "heist",
            "rewards": {"cash": 500 + (level * 50), "reputation": 20 + level},
            "phases": 5 + (level // 2),
            "difficulty": level + 2,
        }

    @staticmethod
    def generate_assassination_mission(level: int, target: str) -> dict:
        return {
            "name": f"Auftrag: {target}",
            "description": f"Eliminiere {target} diskret.",
            "type": "assassination",
            "rewards": {"cash": 800 + (level * 75), "reputation": 30 + level},
            "phases": 4 + (level // 2),
            "difficulty": level + 3,
        }