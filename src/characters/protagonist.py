import json
import time
import random

from src.ui.text_display import TextDisplayManager
from src.story.story_manager import StoryManager
from src.missions.mission_manager import MissionManager
from src.missions.mission import Mission, MissionPhase
from src.missions.mission_giver import MissionGiver
from src.districts.district_manager import DistrictManager
from src.effects.drug_effect import DrugEffect
from src.effects.dragon_hallucination import DragonHallucination
from src.items.weapon import Weapon
from src.characters.dragon import ViceCityDragon


class Location:
    def __init__(self, name, description, danger_level, opportunities):
        self.name = name
        self.description = description
        self.danger_level = danger_level
        self.opportunities = opportunities
    
    def describe(self):
        print(f"\n[ORT] {self.name}")
        print(f"{self.description}")
        print(f"Gefahrenlevel: {'*' * self.danger_level}")


class Protagonist:
    def __init__(self, name, character_type):
        self.name = name
        self.character_type = character_type
        self.cash = 500
        self.level = 1
        self.inventory = []
        self.stamina = 30
        self.days = 0
        self.wanted_level = 0
        self.reputation = 0
        self.drug_effects = []
        self.dragon_encounters = 0
        self.chapter = 1
        self.partner_trust = 100
        self.ankle_monitor = character_type == "lucia"
        
        self.text_display = TextDisplayManager()
        self.story_manager = StoryManager(self.text_display)
        self.story_flags = {
            "first_crime_committed": False,
            "first_dragon_seen": False,
            "partner_betrayed": False,
            "redemption_offered": False,
            "first_mission_completed": False
        }
        self.mission_manager = MissionManager()
        self.district_manager = DistrictManager(self)
        
        if character_type == "jason":
            self.combat_skill = 15
            self.stealth = 10
        else:
            self.combat_skill = 10
            self.stealth = 15
    
    def display_attributes(self):
        print(f"\n[SPIELER] {self.name.upper()} - {self.character_type.upper()}")
        print(f"[CASH] Cash: ${self.cash}")
        print(f"[LEVEL] Level: {self.level}")
        print(f"[AUSDAUER] Ausdauer: {self.stamina}")
        print(f"[WAFFEN] Inventar: {[item.name for item in self.inventory]}")
        print(f"[WANTED] Wanted Level: {self.wanted_level}")
        print(f"[REPUTATION] Reputation: {self.reputation}")
        print(f"[TAGE] Tage in Vice City: {self.days}")
        print(f"[DRACHEN] Drachen-Begegnungen: {self.dragon_encounters}")
        print(f"[PARTNER] Partner-Vertrauen: {self.partner_trust}%")
        if self.ankle_monitor:
            print("[FUSSFESSEL] Fußfessel aktiv (Einschränkungen bei Aktivitäten)")
    
    def switch_character(self):
        pass
    
    def rest(self, location="sicherer Unterschlupf"):
        print(f"\n[RUHEN] Du ruhst dich in {location} aus...")
        self.days += 1
        self.stamina = self.level * 25
        self.wanted_level = max(0, self.wanted_level - 1)
        
        self.drug_effects = [effect for effect in self.drug_effects if effect.remaining > 0]
        
        if self.dragon_encounters > 0 and random.random() < 0.3:
            dragon = DragonHallucination()
            dragon.trigger_encounter("high_stress", self)
            
        print(f"Ausdauer wiederhergestellt: {self.stamina}")
        if self.wanted_level > 0:
            print(f"Wanted Level gesunken: {self.wanted_level}")
    
    def explore_vice_city(self):
        self.district_manager.update_season()
        
        districts = list(self.district_manager.districts.values())
        
        print("\nWähle einen Stadtteil in Vice City:")
        for i, district in enumerate(districts):
            feature_indicator = "[ACTIVE]" if district.special_feature in district.discovered_features else "[LOCKED]"
            print(f"{i+1}. {district.name} ({'*' * district.danger_level}) {feature_indicator}")
        
        try:
            choice = int(input(f"Wähle einen Stadtteil (1-{len(districts)}): ")) - 1
            if 0 <= choice < len(districts):
                district = districts[choice]
                self.district_manager.check_feature_unlock(district.name)
                self.explore_district(district)
            else:
                print("Ungültige Wahl!")
        except ValueError:
            print("Ungültige Eingabe!")
    
    def explore_district(self, district):
        district.describe()
        
        if district.special_feature in district.discovered_features:
            self.handle_district_feature(district)
            return
        
        if self.ankle_monitor and random.random() < 0.3:
            print("\n[FUSSFESSEL] Deine Fußfessel schlägt Alarm! Die Polizei ist auf dem Weg!")
            self.wanted_level = min(5, self.wanted_level + 2)
            self.stamina = max(1, self.stamina - 5)
            return
        
        encounter_chance = 0.3 + (district.danger_level * 0.1)
        
        if random.random() < encounter_chance:
            self.criminal_encounter(district)
        else:
            print("\n[STADT] Die Straße ist ruhig. Du findest nichts Nützliches hier.")
            self.stamina = max(1, self.stamina - 2)
    
    def handle_district_feature(self, district):
        if district.special_feature == "tourism_season":
            self.handle_tourism_season(district)
        elif district.special_feature == "motel_network":
            self.handle_motel_network(district)
        elif district.special_feature == "surveillance":
            self.handle_surveillance(district)
        elif district.special_feature == "container_management":
            self.handle_container_management(district)
        elif district.special_feature == "corporate_crime":
            self.handle_corporate_crime(district)
        elif district.special_feature == "territory_control":
            self.handle_territory_control(district)
        elif district.special_feature == "social_climbing":
            self.handle_social_climbing(district)
        elif district.special_feature == "swamp_base":
            self.handle_swamp_base(district)
        elif district.special_feature == "island_smuggling":
            self.handle_island_smuggling(district)
        else:
            print(f"\n[LOCKED] Feature für {district.name} noch nicht implementiert.")
            self.explore_district_regular(district)
    
    def explore_district_regular(self, district):
        if self.ankle_monitor and random.random() < 0.3:
            print("\n[FUSSFESSEL] Deine Fußfessel schlägt Alarm! Die Polizei ist auf dem Weg!")
            self.wanted_level = min(5, self.wanted_level + 2)
            self.stamina = max(1, self.stamina - 5)
            return
        
        encounter_chance = 0.3 + (district.danger_level * 0.1)
        
        if random.random() < encounter_chance:
            self.criminal_encounter(district)
        else:
            print("\n[STADT] Die Straße ist ruhig. Du findest nichts Nützliches hier.")
            self.stamina = max(1, self.stamina - 2)
    
    def criminal_encounter(self, district):
        encounters = {
            "Ocean Beach": [
                {"type": "police", "description": "Ein Polizist bemerkt dich bei einem Taschendiebstahl!"},
                {"type": "tourist", "description": "Eine Gruppe Touristen sieht wie eine leichte Beute aus."},
                {"type": "dealer", "description": "Ein Drogendealer bietet dir eine Probe an."}
            ],
            "Vice Point": [
                {"type": "security", "description": "Ein Wachmann entdeckt dich beim Einbruchversuch!"},
                {"type": "rich_person", "description": "Eine reiche Person allein auf der Straße."},
                {"type": "car", "description": "Ein teures Auto steht ungesichert herum."}
            ],
            "Washington Beach": [
                {"type": "motel_security", "description": "Ein Motel-Wachmann patrouilliert im Flur!"},
                {"type": "beach_vendor", "description": "Ein Strandverkäufer sieht dich beim Schnorren!"},
                {"type": "tourist_family", "description": "Eine Touristenfamilie wirkt wie eine leichte Beute."}
            ],
            "Viceport": [
                {"type": "dock_security", "description": "Dock-Arbeiter entdecken dich beim Schmuggeln!"},
                {"type": "customs", "description": "Zollbeamte führen eine Kontrolle durch!"},
                {"type": "container_guard", "description": "Ein Container-Wachmann macht dich fest!"}
            ],
            "Downtown": [
                {"type": "swat", "description": "SWAT-Team erscheint bei deinem Überfallversuch!"},
                {"type": "bank_teller", "description": "Eine Bankangestellte scheint erpressbar."},
                {"type": "businessman", "description": "Ein Geschäftsmann mit einer teuren Uhr."}
            ],
            "Little Haiti": [
                {"type": "gang", "description": "Eine rivalisierende Gang stellt dich zur Rede!"},
                {"type": "cartel", "description": "Kartell-Mitglieder beobachten dich misstrauisch."},
                {"type": "informant", "description": "Ein Informant hat wertvolle Informationen."}
            ],
            "Starfish Island": [
                {"type": "private_security", "description": "Ein privater Sicherheitsdienst patrouilliert auf dem Anwesen!"},
                {"type": "wealthy_resident", "description": "Ein reicher Bewohner fährt in einem teuren Auto vor."},
                {"type": "elite_criminal", "description": "Ein Elite-Krimineller beobachtet dich von seiner Villa aus."}
            ],
            "Everglades": [
                {"type": "alligators", "description": "Alligatoren blockieren deinen Weg!"},
                {"type": "drug_lab", "description": "Ein illegales Drogenlabor ist in der Nähe."},
                {"type": "smugglers", "description": "Schmuggler sind dabei, ihre Ware zu verstecken."}
            ],
            "Vice Keys": [
                {"type": "coast_guard", "description": "Die Küstenwache patrouilliert in der Nähe."},
                {"type": "black_market", "description": "Ein Schwarzmarkt-Händler bietet rare Waren an."},
                {"type": "smuggler_boat", "description": "Ein Schmugglerboot legt an der Küste an."}
            ]
        }
        encounter = random.choice(encounters[district.name])
        print(f"\n[WAFFEN] {encounter['description']}")
        
        encounter_handlers = {
            "police": self.police_encounter,
            "security": self.security_encounter,
            "motel_security": self.motel_security_encounter,
            "swat": self.swat_encounter,
            "dock_security": self.dock_security_encounter,
            "customs": self.customs_encounter,
            "container_guard": self.container_guard_encounter,
            "private_security": self.private_security_encounter,
            "coast_guard": self.coast_guard_encounter,
            "gang": lambda: self.gang_encounter("gang"),
            "cartel": lambda: self.gang_encounter("cartel"),
            "dealer": self.drug_encounter,
            "tourist": lambda: self.opportunity_encounter("tourist", district),
            "rich_person": lambda: self.opportunity_encounter("rich_person", district),
            "car": lambda: self.opportunity_encounter("car", district),
            "beach_vendor": lambda: self.opportunity_encounter("beach_vendor", district),
            "tourist_family": lambda: self.opportunity_encounter("tourist_family", district),
            "bank_teller": lambda: self.opportunity_encounter("bank_teller", district),
            "businessman": lambda: self.opportunity_encounter("businessman", district),
            "informant": lambda: self.opportunity_encounter("informant", district),
            "drug_lab": lambda: self.opportunity_encounter("drug_lab", district),
            "smugglers": lambda: self.opportunity_encounter("smugglers", district),
            "black_market": lambda: self.opportunity_encounter("black_market", district),
            "smuggler_boat": lambda: self.opportunity_encounter("smuggler_boat", district),
            "alligators": self.alligator_encounter,
            "wealthy_resident": lambda: self.opportunity_encounter("wealthy_resident", district),
            "elite_criminal": lambda: self.opportunity_encounter("elite_criminal", district),
        }
        
        handler = encounter_handlers.get(encounter["type"])
        if handler:
            handler()

    def _get_police_stats(self, police_type):
        return {
            "police": {"stamina": 30, "damage": 8, "wanted_increase": 1},
            "security": {"stamina": 25, "damage": 6, "wanted_increase": 1},
            "swat": {"stamina": 50, "damage": 15, "wanted_increase": 3},
            "coast_guard": {"stamina": 35, "damage": 10, "wanted_increase": 2},
            "motel_security": {"stamina": 20, "damage": 5, "wanted_increase": 1},
            "dock_security": {"stamina": 30, "damage": 7, "wanted_increase": 1},
            "customs": {"stamina": 40, "damage": 12, "wanted_increase": 2},
            "container_guard": {"stamina": 28, "damage": 6, "wanted_increase": 1},
            "private_security": {"stamina": 45, "damage": 11, "wanted_increase": 2}
        }.get(police_type, {"stamina": 30, "damage": 8, "wanted_increase": 1})
    
    def _get_bribe_cost(self, police_type):
        return {
            "police": 200,
            "security": 150,
            "swat": 500,
            "coast_guard": 300,
            "motel_security": 100,
            "dock_security": 175,
            "customs": 250,
            "container_guard": 125,
            "private_security": 400
        }.get(police_type, 200)
    
    def _handle_police_choice(self, police_type, action):
        if action == "kämpfen":
            self.combat_police(police_type)
        elif action == "fliehen":
            self.flee_police(police_type)
        elif action == "bestechen":
            self.bribe_police(police_type)
        else:
            print("Du zögerst zu lange!")
            self.combat_police(police_type)
    
    def police_encounter(self):
        print("\n[POLICE] POLIZEI-KONFRONTATION")
        action = input("Möchtest du kämpfen, fliehen oder bestechen? (kämpfen/fliehen/bestechen) ")
        self._handle_police_choice("police", action)
    
    def security_encounter(self):
        print("\n[SECURITY] SICHERHEITS-KONFRONTATION")
        action = input("Möchtest du kämpfen, fliehen oder bestechen? (kämpfen/fliehen/bestechen) ")
        self._handle_police_choice("security", action)
    
    def motel_security_encounter(self):
        print("\n[MOTEL] MOTEL-SICHERHEITS-KONFRONTATION")
        action = input("Möchtest du kämpfen, fliehen oder bestechen? (kämpfen/fliehen/bestechen) ")
        self._handle_police_choice("motel_security", action)
    
    def swat_encounter(self):
        print("\n[SWAT] SWAT-KONFRONTATION")
        action = input("Möchtest du kämpfen, fliehen oder bestechen? (kämpfen/fliehen/bestechen) ")
        self._handle_police_choice("swat", action)
    
    def dock_security_encounter(self):
        print("\n[DOCK] DOCK-SICHERHEITS-KONFRONTATION")
        action = input("Möchtest du kämpfen, fliehen oder bestechen? (kämpfen/fliehen/bestechen) ")
        self._handle_police_choice("dock_security", action)
    
    def customs_encounter(self):
        print("\n[CUSTOMS] ZOLL-KONFRONTATION")
        action = input("Möchtest du kämpfen, fliehen oder bestechen? (kämpfen/fliehen/bestechen) ")
        self._handle_police_choice("customs", action)
    
    def container_guard_encounter(self):
        print("\n[CONTAINER] CONTAINER-WÄCHTER-KONFRONTATION")
        action = input("Möchtest du kämpfen, fliehen oder bestechen? (kämpfen/fliehen/bestechen) ")
        self._handle_police_choice("container_guard", action)
    
    def private_security_encounter(self):
        print("\n[PRIVATE] PRIVATE-SICHERHEITS-KONFRONTATION")
        action = input("Möchtest du kämpfen, fliehen oder bestechen? (kämpfen/fliehen/bestechen) ")
        self._handle_police_choice("private_security", action)
    
    def coast_guard_encounter(self):
        print("\n[COAST] KÜSTENWACHE-KONFRONTATION")
        action = input("Möchtest du kämpfen, fliehen oder bestechen? (kämpfen/fliehen/bestechen) ")
        self._handle_police_choice("coast_guard", action)
    
    def combat_police(self, police_type):
        stats = self._get_police_stats(police_type)
        combat_chance = 0.3 + (self.combat_skill * 0.02) + (len(self.inventory) * 0.05)
        
        if random.random() < combat_chance:
            print(f"Du besiegst die {police_type}-Einheit!")
            cash_found = random.randint(100, 500)
            self.cash += cash_found
            self.wanted_level = min(5, self.wanted_level + stats["wanted_increase"])
            self.reputation += 5
            print(f"Du findest ${cash_found} bei den Besiegten!")
            print(f"Wanted Level: {self.wanted_level}")
        else:
            print(f"Du wirst von der {police_type}-Einheit besiegt!")
            self.cash = max(0, self.cash // 2)
            self.wanted_level = min(5, self.wanted_level + stats["wanted_increase"] + 1)
            self.stamina = max(1, self.stamina - 15)
            self.days += 1
            print("Du verlierst die Hälfte deines Geldes und landest im Krankenhaus!")
            
            if random.random() < 0.4:
                dragon = DragonHallucination()
                dragon.trigger_encounter("high_stress", self)
                self.dragon_encounters += 1
    
    def flee_police(self, police_type):
        flee_chance = 0.5 + (self.stealth * 0.03) - (self.wanted_level * 0.1)
        
        if random.random() < flee_chance:
            print("Du kannst erfolgreich entkommen!")
            self.stamina = max(1, self.stamina - 10)
        else:
            print("Deine Flucht schlägt fehl!")
            self.combat_police(police_type)
    
    def bribe_police(self, police_type):
        cost = self._get_bribe_cost(police_type)
        
        if self.cash >= cost:
            self.cash -= cost
            print(f"Du bestechst die {police_type}-Einheit mit ${cost}!")
            self.wanted_level = max(0, self.wanted_level - 1)
        else:
            print(f"Du hast nicht genug Geld für die Bestechung (${cost} benötigt)!")
            self.combat_police(police_type)
    
    def gang_encounter(self, gang_type):
        print(f"\n[WAFFEN] GANG-KONFRONTATION: {gang_type.upper()}")
        action = input("Möchtest du kämpfen, verhandeln oder dich anschließen? (kämpfen/verhandeln/anschließen) ")
        
        if action == "kämpfen":
            self.combat_gang(gang_type)
        elif action == "verhandeln":
            self.negotiate_gang(gang_type)
        elif action == "anschließen":
            self.join_gang(gang_type)
        else:
            print("Die Gang interpretiert dein Zögern als Schwäche!")
            self.combat_gang(gang_type)
    
    def combat_gang(self, gang_type):
        combat_chance = 0.4 + (self.combat_skill * 0.02) + (len(self.inventory) * 0.08)
        
        if random.random() < combat_chance:
            print(f"Du besiegst die {gang_type}-Mitglieder!")
            loot = random.randint(300, 800) if gang_type == "cartel" else random.randint(150, 400)
            self.cash += loot
            self.reputation += 10
            print(f"Du erbeutest ${loot} und Waffen!")
            self.story_manager.check_chapter_progression(self)
        else:
            print(f"Du wirst von der {gang_type} besiegt!")
            self.cash = max(0, self.cash // 3)
            self.stamina = max(1, self.stamina - 20)
            self.partner_trust = max(0, self.partner_trust - 15)
            print("Du verlierst Geld und das Vertrauen deines Partners!")
            
            if self.partner_trust < 30 and not self.story_flags["partner_betrayed"]:
                self.story_flags["partner_betrayed"] = True
                self.story_manager.trigger_story_event("partner_trust_low", self)
            
            if random.random() < 0.6:
                dragon = DragonHallucination()
                dragon.trigger_encounter("betrayal", self)
                self.dragon_encounters += 1
    
    def negotiate_gang(self, gang_type):
        negotiate_chance = 0.3 + (self.reputation * 0.01) + (self.level * 0.05)
        
        if random.random() < negotiate_chance:
            payment = random.randint(100, 300)
            print(f"Die Verhandlung erfolgreich! Du zahlst ${payment} für sicheren Durchgang.")
            self.cash = max(0, self.cash - payment)
            self.reputation += 3
        else:
            print("Die Verhandlung scheitert!")
            self.combat_gang(gang_type)
    
    def join_gang(self, gang_type):
        if self.reputation >= 20:
            print(f"Du schließt dich der {gang_type} an!")
            self.cash += random.randint(200, 500)
            self.reputation += 15
            self.wanted_level = min(5, self.wanted_level + 1)
            print("Du erhältst Geld und Einfluss, aber auch mehr Aufmerksamkeit der Polizei!")
            self.story_manager.check_chapter_progression(self)
        else:
            print("Deine Reputation ist nicht hoch genug, um einer Gang beizutreten!")
            self.combat_gang(gang_type)
    
    def drug_encounter(self):
        print("\n[DROGEN] DROGEN-ANGEBOT")
        action = input("Möchtest du Drogen kaufen oder ablehnen? (kaufen/ablehnen) ")
        
        if action == "kaufen":
            if self.cash >= 100:
                self.cash -= 100
                drug_types = [
                    {"name": "Weed", "intensity": 0.3, "duration": 3},
                    {"name": "Kokain", "intensity": 0.7, "duration": 5},
                    {"name": "Meth", "intensity": 0.9, "duration": 7}
                ]
                drug = random.choice(drug_types)
                effect = DrugEffect(drug["name"], drug["intensity"], drug["duration"])
                self.drug_effects.append(effect)
                print(f"Du kaufst {drug['name']} für $100!")
                
                if drug["intensity"] > 0.6:
                    effect.trigger_dragon_hallucination(self)
                    self.dragon_encounters += 1
                    
                    if not self.story_flags["first_dragon_seen"]:
                        self.story_flags["first_dragon_seen"] = True
                        self.story_manager.trigger_story_event("first_dragon", self)
            else:
                print("Du hast nicht genug Geld für Drogen!")
        else:
            print("Du lehnst das Angebot ab.")
    
    def alligator_encounter(self):
        print("\n[ALLIGATOR] ALLIGATOR-KONFRONTATION")
        action = input("Möchtest du kämpfen oder fliehen? (kämpfen/fliehen) ")
        
        if action == "kämpfen":
            combat_chance = 0.3 + (self.combat_skill * 0.02)
            
            if random.random() < combat_chance:
                print("Du besiegst den Alligator!")
                self.cash += random.randint(50, 150)
                self.reputation += 3
                print(f"Du findest ${random.randint(50, 150)} an der Alligator-Haut!")
            else:
                print("Der Alligator ist zu stark!")
                self.stamina = max(1, self.stamina - 10)
                self.cash = max(0, self.cash // 2)
        elif action == "fliehen":
            flee_chance = 0.6 + (self.stealth * 0.03)
            
            if random.random() < flee_chance:
                print("Du kannst vor dem Alligator entkommen!")
                self.stamina = max(1, self.stamina - 5)
            else:
                print("Der Alligator holt dich ein!")
                self.stamina = max(1, self.stamina - 15)
                self.cash = max(0, self.cash // 2)
        else:
            print("Du zögerst zu lange!")
            self.stamina = max(1, self.stamina - 15)
            self.cash = max(0, self.cash // 2)
    
    def opportunity_encounter(self, opportunity_type, district):
        opportunities = {
            "tourist": {"cash": 50, "stamina_cost": 2, "description": "Du bestiehlst einen Touristen"},
            "businessman": {"cash": 150, "stamina_cost": 4, "description": "Du bestiehlst einen Geschäftsmann"},
            "informant": {"cash": 100, "stamina_cost": 1, "description": "Du kaufst Informationen von einem Informanten"},
            "drug_lab": {"cash": 400, "stamina_cost": 12, "description": "Du überfällst ein Drogenlabor"},
            "smugglers": {"cash": 600, "stamina_cost": 15, "description": "Du beraubst Schmuggler"},
            "black_market": {"cash": 250, "stamina_cost": 6, "description": "Du machst ein Geschäft auf dem Schwarzmarkt"},
            "smuggler_boat": {"cash": 800, "stamina_cost": 18, "description": "Du überfällst ein Schmugglerboot"},
            "beach_vendor": {"cash": 75, "stamina_cost": 3, "description": "Du presst einem Strandverkäufer Geld ab"},
            "tourist_family": {"cash": 120, "stamina_cost": 4, "description": "Du betrügst eine Touristenfamilie"},
            "wealthy_resident": {"cash": 350, "stamina_cost": 7, "description": "Du überfällst einen reichen Bewohner"},
            "elite_criminal": {"cash": 450, "stamina_cost": 11, "description": "Du machst ein Geschäft mit einem Elite-Kriminellen"}
        }
        
        opp = opportunities.get(opportunity_type, opportunities["tourist"])
        
        print(f"\n[CASH] GELEGENHEIT: {opp['description']}")
        action = input("Möchtest du diese Gelegenheit nutzen? (ja/nein) ")
        
        if action == "ja":
            if self.stamina >= opp["stamina_cost"]:
                success_chance = 0.6 + (self.stealth * 0.02) - (district.danger_level * 0.05)
                
                if random.random() < success_chance:
                    print(f"Erfolg! Du erhältst ${opp['cash']}!")
                    self.cash += opp["cash"]
                    self.reputation += 2
                    self.stamina -= opp["stamina_cost"]
                    
                    if not self.story_flags["first_crime_committed"]:
                        self.story_flags["first_crime_committed"] = True
                        self.story_manager.trigger_story_event("first_crime", self)
                    
                    self.story_manager.check_chapter_progression(self)
                else:
                    print("Die Aktion schlägt fehl!")
                    self.wanted_level = min(5, self.wanted_level + 1)
                    self.stamina = max(1, self.stamina - opp["stamina_cost"] - 5)
            else:
                print("Du hast nicht genug Ausdauer für diese Aktion!")
        else:
            print("Du lässt die Gelegenheit verstreichen.")
    
    def handle_tourism_season(self, district):
        season = self.district_manager.seasonal_events[self.district_manager.current_season]
        print(f"\n[SEASON] AKTUELLE SAISON: {season['name']}")
        print(f"Touristen-Aufkommen: {season['tourist_multiplier']}x")
        print(f"Polizei-Präsenz: {season['police_multiplier']}x")
        print(f"Belohnungs-Bonus: {season['rewards_bonus']}x")
        
        print("\n[TOURISM] TOURISMUS-OPTIONEN:")
        print("1. Touristen ausrauben (Saison-Bonus)")
        print("2. Strand-Party organisieren")
        print("3. Hotel-Rezeption infiltrieren")
        print("4. Reguläre Erkundung")
        
        try:
            choice = int(input("Wähle eine Option (1-4): "))
            options = {
                1: self.tourist_robbery_season,
                2: self.organize_beach_party,
                3: self.infiltrate_hotel_reception,
                4: self.explore_district_regular
            }
            if choice in options:
                options[choice](district)
            else:
                print("Ungültige Wahl!")
                self.explore_district_regular(district)
        except ValueError:
            print("Ungültige Eingabe!")
            self.explore_district_regular(district)
    
    def tourist_robbery_season(self, district):
        season = self.district_manager.seasonal_events[self.district_manager.current_season]
        
        tourist_types = {
            "high_season": ["reiche Touristen", "Spring Break Partygäste", "Geschäftsleute"],
            "low_season": ["Rucksacktouristen", "Backpacker", "Einheimische"],
            "normal_season": ["Familien", "Paare", "Einzelreisende"]
        }
        
        tourist_type = random.choice(tourist_types[self.district_manager.current_season])
        base_cash = random.randint(50, 200)
        bonus_cash = int(base_cash * (season["rewards_bonus"] - 1.0))
        total_cash = base_cash + bonus_cash
        
        print(f"\n[ROBBERY] Du siehst eine Gruppe von {tourist_type}...")
        
        police_chance = 0.3 * season["police_multiplier"]
        
        if random.random() < police_chance:
            print("\n[POLICE] Ein Polizist hat dich bemerkt!")
            self.police_encounter()
        else:
            print(f"\n[SUCCESS] Erfolgreicher Diebstahl bei {tourist_type}!")
            print(f"Basis: ${base_cash} + Saison-Bonus: ${bonus_cash} = ${total_cash}")
            self.cash += total_cash
            district.reputation += 2
            self.stamina -= 3
    
    def organize_beach_party(self, district):
        print("\n[PARTY] Du organisierst eine Strand-Party...")
        
        if self.cash < 100:
            print("Du brauchst mindestens $100 für die Organisation!")
            return
        
        self.cash -= 100
        self.stamina -= 5
        
        success_chance = 0.4 + (self.reputation * 0.01) + (self.stealth * 0.02)
        
        if random.random() < success_chance:
            profit = random.randint(200, 600)
            print(f"\n[SUCCESS] Die Party ist ein Erfolg! Du verdienst ${profit}!")
            self.cash += profit
            district.reputation += 3
            self.reputation += 2
        else:
            print("\n[FAILURE] Die Party wird von der Polizei geräumt!")
            self.wanted_level = min(5, self.wanted_level + 1)
            self.stamina = max(1, self.stamina - 10)
    
    def infiltrate_hotel_reception(self, district):
        print("\n[INFILTRATE] Du schleichst dich zur Hotel-Rezeption...")
        
        stealth_check = 0.3 + (self.stealth * 0.03)
        
        if random.random() < stealth_check:
            information_value = random.randint(100, 300)
            print(f"\n[SUCCESS] Du stiehlst wertvolle Informationen über reiche Gäste! Wert: ${information_value}")
            self.cash += information_value
            district.reputation += 1
            self.stamina -= 4
        else:
            print("\n[FAILURE] Der Hotel-Manager entdeckt dich!")
            self.wanted_level = min(5, self.wanted_level + 1)
            self.stamina = max(1, self.stamina - 8)
    
    def handle_motel_network(self, district):
        print(f"\n[MOTEL] MOTEL-NETZWERK in {district.name}")
        print("Das Motel-Netzwerk bietet verschiedene Möglichkeiten:")
        print("1. Motel-Gäste ausrauben")
        print("2. Motel-Rezeption infiltrieren")
        print("3. Motel-Zimmer als Versteck mieten")
        print("4. Reguläre Erkundung")
        
        try:
            choice = int(input("Wähle eine Option (1-4): "))
            options = {
                1: self.motel_guest_robbery,
                2: self.motel_reception_infiltrate,
                3: self.rent_motel_room,
                4: self.explore_district_regular
            }
            if choice in options:
                options[choice](district)
            else:
                print("Ungültige Wahl!")
                self.explore_district_regular(district)
        except ValueError:
            print("Ungültige Eingabe!")
            self.explore_district_regular(district)
    
    def motel_guest_robbery(self, district):
        print("\n[MOTEL] Du raubst Motel-Gäste aus...")
        stealth_check = 0.4 + (self.stealth * 0.03)
        
        if random.random() < stealth_check:
            loot = random.randint(100, 300)
            print(f"\n[SUCCESS] Erfolgreicher Raub! Beute: ${loot}")
            self.cash += loot
            district.reputation += 2
            self.stamina -= 4
        else:
            print("\n[FAILURE] Der Motel-Wachmann hat dich erwischt!")
            self.motel_security_encounter()
    
    def motel_reception_infiltrate(self, district):
        print("\n[MOTEL] Du infiltrierst die Motel-Rezeption...")
        stealth_check = 0.35 + (self.stealth * 0.03)
        
        if random.random() < stealth_check:
            info_value = random.randint(150, 400)
            print(f"\n[SUCCESS] Informationen gestohlen! Wert: ${info_value}")
            self.cash += info_value
            district.reputation += 1
            self.stamina -= 5
        else:
            print("\n[FAILURE] Die Rezeption hat dich bemerkt!")
            self.wanted_level = min(5, self.wanted_level + 1)
            self.stamina = max(1, self.stamina - 8)
    
    def rent_motel_room(self, district):
        if self.cash >= 50:
            self.cash -= 50
            print("\n[SUCCESS] Du hast ein Motel-Zimmer gemietet. Sicherer Rückzugsort.")
            self.stamina = min(self.level * 25, self.stamina + 10)
        else:
            print("Du hast nicht genug Geld ($50 benötigt)!")
    
    def handle_surveillance(self, district):
        print(f"\n[SURVEILLANCE] ÜBERWACHUNGS-SYSTEM in {district.name}")
        print("Die Überwachungskameras können ein Vorteil oder Hindernis sein:")
        print("1. Überwachung umgehen (Einbruch)")
        print("2. Überwachungsdaten stehlen")
        print("3. Reiche Bewohner beobachten")
        print("4. Reguläre Erkundung")
        
        try:
            choice = int(input("Wähle eine Option (1-4): "))
            options = {
                1: self.bypass_surveillance,
                2: self.steal_surveillance_data,
                3: self.observe_residents,
                4: self.explore_district_regular
            }
            if choice in options:
                options[choice](district)
            else:
                print("Ungültige Wahl!")
                self.explore_district_regular(district)
        except ValueError:
            print("Ungültige Eingabe!")
            self.explore_district_regular(district)
    
    def bypass_surveillance(self, district):
        print("\n[SURVEILLANCE] Du umgehst die Überwachung...")
        stealth_check = 0.3 + (self.stealth * 0.04)
        
        if random.random() < stealth_check:
            loot = random.randint(200, 500)
            print(f"\n[SUCCESS] Einbruch erfolgreich! Beute: ${loot}")
            self.cash += loot
            district.reputation += 2
            self.wanted_level = min(5, self.wanted_level + 1)
            self.stamina -= 8
        else:
            print("\n[FAILURE] Die Überwachung hat dich aufgenommen!")
            self.security_encounter()
    
    def steal_surveillance_data(self, district):
        print("\n[SURVEILLANCE] Du stiehlst Überwachungsdaten...")
        tech_check = 0.35 + (self.stealth * 0.03)
        
        if random.random() < tech_check:
            ransom = random.randint(300, 700)
            print(f"\n[SUCCESS] Daten gestohlen! Lösegeld: ${ransom}")
            self.cash += ransom
            district.reputation += 1
            self.stamina -= 5
        else:
            print("\n[FAILURE] Die Sicherheitsfirma hat dich entdeckt!")
            self.security_encounter()
    
    def observe_residents(self, district):
        print("\n[SURVEILLANCE] Du beobachtest reiche Bewohner...")
        if self.stealth >= 15:
            info_value = random.randint(200, 500)
            print(f"\n[SUCCESS] Wertvolle Informationen gesammelt! Wert: ${info_value}")
            self.cash += info_value
            district.reputation += 1
            self.stamina -= 3
        else:
            print("Deine Beobachtungsfähigkeiten sind nicht gut genug!")
            self.stamina = max(1, self.stamina - 2)
    
    def handle_container_management(self, district):
        print(f"\n[CONTAINER] CONTAINER-MANAGEMENT in {district.name}")
        print("Die Container-Terminals bieten viele Möglichkeiten:")
        print("1. Container plündern")
        print("2. Schmuggel-Container finden")
        print("3. Dock-Arbeiter bestechen")
        print("4. Reguläre Erkundung")
        
        try:
            choice = int(input("Wähle eine Option (1-4): "))
            options = {
                1: self.loot_container,
                2: self.find_smuggle_container,
                3: self.bribe_dock_workers,
                4: self.explore_district_regular
            }
            if choice in options:
                options[choice](district)
            else:
                print("Ungültige Wahl!")
                self.explore_district_regular(district)
        except ValueError:
            print("Ungültige Eingabe!")
            self.explore_district_regular(district)
    
    def loot_container(self, district):
        print("\n[CONTAINER] Du plünderst einen Container...")
        stealth_check = 0.35 + (self.stealth * 0.03)
        
        if random.random() < stealth_check:
            loot = random.randint(400, 1000)
            print(f"\n[SUCCESS] Container geplündert! Beute: ${loot}")
            self.cash += loot
            district.reputation += 3
            self.wanted_level = min(5, self.wanted_level + 1)
            self.stamina -= 10
        else:
            print("\n[FAILURE] Container-Wächter haben dich erwischt!")
            self.container_guard_encounter()
    
    def find_smuggle_container(self, district):
        print("\n[CONTAINER] Du suchst nach Schmuggel-Containern...")
        search_chance = 0.3 + (self.stealth * 0.02)
        
        if random.random() < search_chance:
            smuggle_value = random.randint(600, 1500)
            print(f"\n[SUCCESS] Schmuggel-Container gefunden! Wert: ${smuggle_value}")
            self.cash += smuggle_value
            district.reputation += 4
            self.wanted_level = min(5, self.wanted_level + 2)
            self.stamina -= 12
        else:
            print("\n[FAILURE] Die Suche war erfolglos und hat Aufmerksamkeit erregt!")
            self.dock_security_encounter()
    
    def bribe_dock_workers(self, district):
        if self.cash >= 200:
            self.cash -= 200
            print("\n[SUCCESS] Dock-Arbeiter bestochen! Freier Zugang zu Containern.")
            district.reputation += 1
            loot = random.randint(300, 800)
            self.cash += loot
            print(f"Du findest ${loot} in einem Container.")
            self.stamina -= 5
        else:
            print("Du hast nicht genug Geld für Bestechung ($200 benötigt)!")
    
    def handle_corporate_crime(self, district):
        print(f"\n[CORPORATE] UNTERNEHMENSKRIMINALITÄT in {district.name}")
        print("Die Geschäftswelt hat ihre dunklen Seiten:")
        print("1. Firma erpressen")
        print("2. Banküberfall planen")
        print("3. Geschäftsdaten stehlen")
        print("4. Reguläre Erkundung")
        
        try:
            choice = int(input("Wähle eine Option (1-4): "))
            options = {
                1: self.extort_company,
                2: self.plan_bank_heist,
                3: self.steal_business_data,
                4: self.explore_district_regular
            }
            if choice in options:
                options[choice](district)
            else:
                print("Ungültige Wahl!")
                self.explore_district_regular(district)
        except ValueError:
            print("Ungültige Eingabe!")
            self.explore_district_regular(district)
    
    def extort_company(self, district):
        print("\n[CORPORATE] Du erpresst eine Firma...")
        if self.reputation >= 30:
            extortion = random.randint(500, 1200)
            print(f"\n[SUCCESS] Erpressung erfolgreich! Geld: ${extortion}")
            self.cash += extortion
            district.reputation += 3
            self.wanted_level = min(5, self.wanted_level + 1)
            self.stamina -= 8
        else:
            print("Deine Reputation ist nicht hoch genug für Erpressung!")
    
    def plan_bank_heist(self, district):
        print("\n[CORPORATE] Du planst einen Banküberfall...")
        if self.level >= 5 and self.reputation >= 50:
            heist_chance = 0.3 + (self.combat_skill * 0.02) + (self.stealth * 0.02)
            
            if random.random() < heist_chance:
                heist_loot = random.randint(2000, 5000)
                print(f"\n[SUCCESS] Banküberfall erfolgreich! Beute: ${heist_loot}")
                self.cash += heist_loot
                district.reputation += 5
                self.wanted_level = min(5, self.wanted_level + 3)
                self.stamina -= 20
            else:
                print("\n[FAILURE] Der Überfall schlägt fehl!")
                self.swat_encounter()
        else:
            print("Du brauchst Level 5 und 50 Reputation für diesen Überfall!")
    
    def handle_territory_control(self, district):
        print(f"\n[TERRITORY] GEBIETS-KONTROLLE in {district.name}")
        print("Gebiets-Kontrolle erfordert Strategie:")
        print("1. Rivale Gang angreifen")
        print("2. Gebiet übernehmen")
        print("3. Schutzgelder eintreiben")
        print("4. Reguläre Erkundung")
        
        try:
            choice = int(input("Wähle eine Option (1-4): "))
            options = {
                1: self.attack_rival_gang,
                2: self.take_territory,
                3: self.collect_protection_money,
                4: self.explore_district_regular
            }
            if choice in options:
                options[choice](district)
            else:
                print("Ungültige Wahl!")
                self.explore_district_regular(district)
        except ValueError:
            print("Ungültige Eingabe!")
            self.explore_district_regular(district)
    
    def handle_social_climbing(self, district):
        print(f"\n[SOCIAL] GESELLSCHAFTLICHER AUFSTIEG in {district.name}")
        print("In der High Society geht es um Einfluss:")
        print("1. Luxus-Party infiltrieren")
        print("2. Reiche Kontakte knüpfen")
        print("3. Villa ausrauben")
        print("4. Reguläre Erkundung")
        
        try:
            choice = int(input("Wähle eine Option (1-4): "))
            options = {
                1: self.infiltrate_luxury_party,
                2: self.make_rich_contacts,
                3: self.rob_mansion,
                4: self.explore_district_regular
            }
            if choice in options:
                options[choice](district)
            else:
                print("Ungültige Wahl!")
                self.explore_district_regular(district)
        except ValueError:
            print("Ungültige Eingabe!")
            self.explore_district_regular(district)
    
    def handle_swamp_base(self, district):
        print(f"\n[SWAMP] SUMPF-BASIS in {district.name}")
        print("Der Sumpf bietet ideale Verstecke:")
        print("1. Sumpf-Versteck einrichten")
        print("2. Drogenlabor finden")
        print("3. Schmuggler-Routen nutzen")
        print("4. Reguläre Erkundung")
        
        try:
            choice = int(input("Wähle eine Option (1-4): "))
            options = {
                1: self.setup_swamp_hideout,
                2: self.find_drug_lab_swamp,
                3: self.use_smuggler_routes,
                4: self.explore_district_regular
            }
            if choice in options:
                options[choice](district)
            else:
                print("Ungültige Wahl!")
                self.explore_district_regular(district)
        except ValueError:
            print("Ungültige Eingabe!")
            self.explore_district_regular(district)
    
    def handle_island_smuggling(self, district):
        print(f"\n[ISLAND] INSEL-SCHMUGGEL in {district.name}")
        print("Die Inseln sind perfekt für Schmuggel:")
        print("1. Schmuggel-Boot kapern")
        print("2. Schwarzmarkt besuchen")
        print("3. Menschenhandel unterbinden")
        print("4. Reguläre Erkundung")
        
        try:
            choice = int(input("Wähle eine Option (1-4): "))
            options = {
                1: self.hijack_smuggle_boat,
                2: self.visit_island_black_market,
                3: self.stop_human_trafficking,
                4: self.explore_district_regular
            }
            if choice in options:
                options[choice](district)
            else:
                print("Ungültige Wahl!")
                self.explore_district_regular(district)
        except ValueError:
            print("Ungültige Eingabe!")
            self.explore_district_regular(district)
    
    def attack_rival_gang(self, district):
        print("\n[TERRITORY] Du greifst eine rivalisierende Gang an...")
        combat_chance = 0.4 + (self.combat_skill * 0.03)
        
        if random.random() < combat_chance:
            territory_gain = random.randint(200, 500)
            print(f"\n[SUCCESS] Gebietskampf gewonnen! Beute: ${territory_gain}")
            self.cash += territory_gain
            district.reputation += 4
            district.control_level = min(100, district.control_level + 10)
            self.stamina -= 12
        else:
            print("\n[FAILURE] Du verlierst den Gebietskampf!")
            self.gang_encounter("gang")
    
    def take_territory(self, district):
        print("\n[TERRITORY] Du übernimmst die Kontrolle über ein Gebiet...")
        if district.control_level >= 50:
            print("Du kontrollierst dieses Gebiet bereits!")
        else:
            control_chance = 0.3 + (self.reputation * 0.01)
            
            if random.random() < control_chance:
                print("\n[SUCCESS] Gebiet übernommen! Dein Einfluss wächst.")
                district.control_level = min(100, district.control_level + 20)
                district.reputation += 3
                self.stamina -= 8
            else:
                print("\n[FAILURE] Die Verteidigung ist zu stark!")
                self.gang_encounter("gang")
    
    def collect_protection_money(self, district):
        print("\n[TERRITORY] Du eintreibst Schutzgelder...")
        if district.control_level >= 30:
            protection_money = random.randint(150, 400) * (district.control_level // 10)
            print(f"\n[SUCCESS] Schutzgelder eintreiben! Geld: ${protection_money}")
            self.cash += protection_money
            district.reputation += 1
            self.stamina -= 3
        else:
            print("Du hast nicht genug Kontrolle in diesem Gebiet!")
    
    def infiltrate_luxury_party(self, district):
        print("\n[SOCIAL] Du infiltrierst eine Luxus-Party...")
        stealth_check = 0.4 + (self.stealth * 0.04)
        
        if random.random() < stealth_check:
            party_loot = random.randint(500, 1500)
            print(f"\n[SUCCESS] Party-Infiltration erfolgreich! Beute: ${party_loot}")
            self.cash += party_loot
            district.reputation += 3
            self.stamina -= 6
        else:
            print("\n[FAILURE] Du wirst von der Security erwischt!")
            self.private_security_encounter()
    
    def make_rich_contacts(self, district):
        print("\n[SOCIAL] Du knüpfst Kontakte zur High Society...")
        if self.reputation >= 40:
            contact_value = random.randint(300, 800)
            print(f"\n[SUCCESS] Wertvolle Kontakte geknüpft! Vorteil: ${contact_value}")
            self.cash += contact_value
            district.reputation += 2
            self.stamina -= 2
        else:
            print("Deine Reputation ist nicht hoch genug für die High Society!")
    
    def rob_mansion(self, district):
        print("\n[SOCIAL] Du planst einen Einbruch in eine Villa...")
        heist_chance = 0.3 + (self.stealth * 0.05)
        
        if random.random() < heist_chance:
            mansion_loot = random.randint(800, 2000)
            print(f"\n[SUCCESS] Villeneinbruch erfolgreich! Beute: ${mansion_loot}")
            self.cash += mansion_loot
            district.reputation += 4
            self.wanted_level = min(5, self.wanted_level + 1)
            self.stamina -= 12
        else:
            print("\n[FAILURE] Einbruch schlägt fehl! Private Security ist unterwegs!")
            self.private_security_encounter()
    
    def setup_swamp_hideout(self, district):
        print("\n[SWAMP] Du richtest ein Sumpf-Versteck ein...")
        if self.cash >= 300:
            self.cash -= 300
            print("\n[SUCCESS] Sumpf-Versteck eingerichtet! Sicherer Rückzugsort.")
            self.stamina = min(self.level * 25, self.stamina + 15)
            district.reputation += 2
        else:
            print("Du hast nicht genug Geld für ein Versteck ($300 benötigt)!")
    
    def find_drug_lab_swamp(self, district):
        print("\n[SWAMP] Du suchst nach Drogenlaboren im Sumpf...")
        search_chance = 0.3 + (self.stealth * 0.03)
        
        if random.random() < search_chance:
            lab_loot = random.randint(600, 1500)
            print(f"\n[SUCCESS] Drogenlabor gefunden! Beute: ${lab_loot}")
            self.cash += lab_loot
            district.reputation += 3
            self.wanted_level = min(5, self.wanted_level + 1)
            self.stamina -= 10
        else:
            print("\n[FAILURE] Du wirst von Lab-Wachtern entdeckt!")
            self.gang_encounter("cartel")
    
    def use_smuggler_routes(self, district):
        print("\n[SWAMP] Du nutzt Schmuggler-Routen...")
        route_chance = 0.5 + (self.stealth * 0.02)
        
        if random.random() < route_chance:
            route_profit = random.randint(200, 600)
            print(f"\n[SUCCESS] Schmuggel-Route genutzt! Gewinn: ${route_profit}")
            self.cash += route_profit
            district.reputation += 2
            self.stamina -= 5
        else:
            print("\n[FAILURE] Schmuggler entdecken dich!")
            self.gang_encounter("cartel")
    
    def hijack_smuggle_boat(self, district):
        print("\n[ISLAND] Du kapern ein Schmuggel-Boot...")
        hijack_chance = 0.3 + (self.combat_skill * 0.03)
        
        if random.random() < hijack_chance:
            boat_loot = random.randint(800, 2000)
            print(f"\n[SUCCESS] Schmuggel-Boot gekapert! Beute: ${boat_loot}")
            self.cash += boat_loot
            district.reputation += 4
            self.wanted_level = min(5, self.wanted_level + 2)
            self.stamina -= 15
        else:
            print("\n[FAILURE] Kaperung schlägt fehl! Küstenwache ist im Anmarsch!")
            self.coast_guard_encounter()
    
    def visit_island_black_market(self, district):
        print("\n[ISLAND] Du besuchst den exklusiven Insel-Schwarzmarkt...")
        if self.reputation >= 50:
            market_deal = random.randint(400, 1200)
            print(f"\n[SUCCESS] Schwarzmarkt-Deal abgeschlossen! Gewinn: ${market_deal}")
            self.cash += market_deal
            district.reputation += 2
            self.stamina -= 3
        else:
            print("Deine Reputation ist nicht hoch genug für diesen Schwarzmarkt!")
    
    def stop_human_trafficking(self, district):
        print("\n[ISLAND] Du unterbindest Menschenhandel...")
        combat_chance = 0.4 + (self.combat_skill * 0.04)
        
        if random.random() < combat_chance:
            reward_money = random.randint(1000, 2500)
            print(f"\n[SUCCESS] Menschenhandel unterbunden! Belohnung: ${reward_money}")
            self.cash += reward_money
            district.reputation += 5
            self.partner_trust = min(100, self.partner_trust + 10)
            self.stamina -= 12
        else:
            print("\n[FAILURE] Die Menschenhändler sind zu stark!")
            self.gang_encounter("cartel")
    
    def steal_business_data(self, district):
        print("\n[CORPORATE] Du stiehlst Geschäftsdaten...")
        tech_check = 0.4 + (self.stealth * 0.04)
        
        if random.random() < tech_check:
            data_ransom = random.randint(300, 800)
            print(f"\n[SUCCESS] Daten gestohlen! Lösegeld: ${data_ransom}")
            self.cash += data_ransom
            district.reputation += 2
            self.stamina -= 5
        else:
            print("\n[FAILURE] Unternehmenssicherheit hat dich erwischt!")
            self.security_encounter()
    
    def visit_black_market(self):
        weapons = [
            Weapon("Messer", 100, 5, 2),
            Weapon("Pistole", 500, 10, 3),
            Weapon("Schrotflinte", 1500, 15, 4),
            Weapon("Sturmgewehr", 3000, 25, 5),
            Weapon("Scharfschützengewehr", 5000, 35, 5)
        ]
        
        print("\n[WAFFEN] SCHWARZMARKT - Illegale Waffen")
        print("Hier sind die verfügbaren Waffen:")
        for i, weapon in enumerate(weapons):
            owned = " (Bereits besitzt)" if weapon.name in [owned_item.name for owned_item in self.inventory] else ""
            print(f"{i + 1}. {weapon.name} - Kosten: ${weapon.cost} - Schaden: +{weapon.damage_increase} - Illegalität: {'⚠️' * weapon.illegal_status}{owned}")
        
        try:
            choice = int(input("Welche Waffe möchtest du kaufen? (Gib die Nummer ein) "))
            if 1 <= choice <= len(weapons):
                weapon = weapons[choice - 1]
                if weapon.name in [owned_item.name for owned_item in self.inventory]:
                    print(f"Du besitzt bereits eine {weapon.name}!")
                elif self.cash >= weapon.cost:
                    self.cash -= weapon.cost
                    self.inventory.append(weapon)
                    print(f"Du hast eine {weapon.name} gekauft!")
                    self.wanted_level = min(5, self.wanted_level + (weapon.illegal_status // 2))
                    print(f"Wanted Level erhöht: {self.wanted_level}")
                else:
                    print(f"Du hast nicht genug Geld für diese Waffe (${weapon.cost} benötigt)!")
            else:
                print("Ungültige Wahl!")
        except ValueError:
            print("Ungültige Eingabe!")
    
    def confront_dragon(self, dragon):
        print(f"\n[DRACHE] KONFRONTATION MIT DEM {dragon.name.upper()}")
        print("Dies ist der Moment der Wahrheit - die Konsequenzen deines Lebens holen dich ein.")
        print(f"Drachen-Stärke: {dragon.stamina} | Deine Ausdauer: {self.stamina}")
        
        while dragon.stamina > 0 and self.stamina > 0:
            print(f"\n[STATUS] Status - Drache: {dragon.stamina} | Du: {self.stamina} | Cash: ${self.cash}")
            action = input("Möchtest du konfrontieren, fliehen oder deine Drogen nutzen? (konfrontieren/fliehen/drogen) ")
            
            if action == "konfrontieren":
                self.confront_dragon_directly(dragon)
            elif action == "fliehen":
                if self.flee_from_dragon():
                    break
            elif action == "drogen":
                self.use_drugs_vs_dragon(dragon)
            else:
                print("Ungültige Aktion! Der Drache nutzt deine Zögerlichkeit aus.")
                dragon.attack_protagonist(self)
        
        if dragon.stamina <= 0:
            self.dragon_victory(dragon)
        elif self.stamina <= 0:
            self.dragon_defeat(dragon)
    
    def confront_dragon_directly(self, dragon):
        weapon_damage = sum(item.damage_increase for item in self.inventory)
        mental_strength = max(0, 100 - (self.dragon_encounters * 5))
        
        confront_chance = 0.3 + (self.level * 0.05) + (weapon_damage * 0.01) + (mental_strength * 0.002)
        
        if random.random() < confront_chance:
            damage = random.randint(20, 40) + weapon_damage + (self.level * 3)
            dragon.stamina -= damage
            print(f'Du stellst dich deinen Dämonen! Du verursachst {damage} "psychischen" Schaden!')
            print(f"Drachen-Stärke: {max(0, dragon.stamina)}")
            
            if dragon.stamina > 0:
                dragon.attack_protagonist(self)
        else:
            print("Deine Konfrontation scheitert! Die Konsequenzen überwältigen dich.")
            dragon.attack_protagonist(self)
    
    def flee_from_dragon(self):
        flee_chance = 0.4 + (self.stealth * 0.03) - (self.dragon_encounters * 0.05)
        
        if random.random() < flee_chance:
            print("Du kannst vor deinen Konsequenzen fliehen... vorerst.")
            self.stamina = max(1, self.stamina - 20)
            self.cash = max(0, self.cash - 200)
            self.dragon_encounters += 1
            return True
        else:
            print("Du kannst deinen Konsequenzen nicht entkommen!")
            return False
    
    def use_drugs_vs_dragon(self, dragon):
        if self.drug_effects:
            effect = self.drug_effects[0]
            print(f"Du nimmst {effect.name} um dem Drache zu entkommen...")
            
            if effect.intensity > 0.7:
                print("Die Drogen sind zu stark! Du bekommst eine Überdosis Halluzinationen!")
                self.dragon_encounters += 2
                self.stamina = max(1, self.stamina - 25)
                dragon.attack_protagonist(self)
            else:
                print("Die Drogen geben dir temporären Mut... aber der Drache wird stärker.")
                dragon.stamina += 10
                self.stamina = max(1, self.stamina - 10)
        else:
            print("Du hast keine Drogen!")
            dragon.attack_protagonist(self)
    
    def dragon_victory(self, dragon):
        dragon.defeated = True
        print("\n*** SIEG UEBER DIE KONSEKUENZEN! ***")
        print("Du hast deine Daemonen bezwungen und einen Weg aus dem kriminellen Leben gefunden!")
        
        reward = random.randint(10000, 25000)
        self.cash += reward
        print(f"Du findest einen Weg zu einem ehrlichen Leben und erhaelst ${reward} aus legitimen Quellen!")
        print("Die Vice City Dragons Saga ist beendet. Du bist frei!")
        
        self.dragon_defeated = True
    
    def dragon_defeat(self, dragon):
        print("\n*** DEINE KONSEKUENZEN HOLEN DICH EIN ***")
        print("Der Drache der Konsequenzen hat dich verschlungen.")
        print("Du verlierst alles und landest fuer immer im Gefaengnis... oder schlimmer.")
        
        self.cash = 0
        self.wanted_level = 5
        self.partner_trust = 0
        self.days += 7
        self.stamina = 10
        
        print("Alles ist verloren. Das kriminelle Leben hat dich bezahlt.")
    
    def visit_mission_board(self):
        print("\n[MISSION] MISSION-BRETT")
        print("Verfügbare Missionen und Kontakte:")
        
        self.mission_manager.check_mission_unlocks(self)
        
        available_missions = self.mission_manager.get_available_missions(self)
        
        if not available_missions:
            print("Keine Missionen verfügbar. Erhöhe deine Reputation oder Level.")
            return
        
        print("\n[MISSION] VERFÜGBARE MISSIONEN:")
        for i, mission in enumerate(available_missions):
            print(f"{i+1}. {mission.name} (Kapitel {mission.chapter}, {'*' * mission.difficulty})")
            print(f"   Belohnung: ${mission.rewards.get('cash', 0)}, +{mission.rewards.get('reputation', 0)} Reputation")
        
        print(f"{len(available_missions)+1}. Zurück zum Hauptmenü")
        
        try:
            choice = int(input("Wähle eine Mission: ")) - 1
            if 0 <= choice < len(available_missions):
                mission = available_missions[choice]
                self.start_mission(mission)
            elif choice == len(available_missions):
                return
            else:
                print("Ungültige Wahl!")
        except ValueError:
            print("Ungültige Eingabe!")
    
    def start_mission(self, mission):
        if self.mission_manager.start_mission(mission, self):
            print(f"\n🎉 Mission '{mission.name}' erfolgreich abgeschlossen!")
        else:
            print(f"\n💥 Mission '{mission.name}' fehlgeschlagen oder abgebrochen.")
    
    def initialize_missions(self):
        rico = MissionGiver(
            "Rico",
            "Ocean Beach",
            "professional",
            "Ein professioneller Autodieb und Hehler, der immer einen Deal im Angebot hat."
        )
        
        maria = MissionGiver(
            "Maria",
            "Little Haiti",
            "desperate",
            "Eine verzweifelte Drogenhändlerin, die sich aus dem Geschäft zurückziehen will."
        )
        
        self.mission_manager.register_mission_giver(rico)
        self.mission_manager.register_mission_giver(maria)
        
        self.create_first_taste_mission()
        self.create_beach_party_mission()
        
        first_mission = self.mission_manager.all_missions.get("First Taste of Vice City")
        if first_mission:
            first_mission.available = True
    
    def create_first_taste_mission(self):
        mission = Mission(
            "First Taste of Vice City",
            1,
            2,
            {"cash": 500, "reputation": 5, "partner_trust": 5},
            self.text_display
        )
        
        phase1 = MissionPhase(
            "Das Treffen",
            "dialogue",
            "Du triffst Rico in einem schäbigen Café in Ocean Beach. Er hat einen einfachen Job für dich."
        )
        phase1.dialogue = [
            {"speaker": "Rico", "text": "Willkommen in Vice City, Neuling. Ich höre, du brauchst schnelles Geld."},
            {"speaker": "Rico", "text": "Ich habe einen kleinen Job für dich - nichts Großes, nur ein einfacher Autodiebstahl."},
            {"speaker": "Rico", "text": "Ein teures Auto steht in Vice Point. Die Besitzer sind auf Urlaub."},
            {"speaker": "Rico", "text": "Bring es zu meiner Garage in Ocean Beach und du bekommst $500. Einfach, oder?"}
        ]
        phase1.choices = [
            {
                "text": "Klingt gut. Ich mache es.",
                "response": "Rico: Perfekt. Ich wusste, ich kann auf dich zählen.",
                "rewards": {"partner_trust": 2}
            },
            {
                "text": "Was ist der Haken?",
                "response": "Rico: Kein Haken. Nur ein einfacher Job für einen einfachen Start.",
                "consequences": {"partner_trust": -1}
            }
        ]
        
        phase2 = MissionPhase(
            "Fahrt nach Vice Point",
            "travel",
            "Du fährst mit einem gestohlenen Wagen nach Vice Point. Rico gibt dir während der Fahrt Tipps."
        )
        phase2.travel_dialogue = [
            {"speaker": "Rico", "text": "Vice Point ist reich. Die Leute dort achten nicht auf ihre Sachen."},
            {"speaker": "Rico", "text": "Sei leise, sei schnell. Keine Aufmerksamkeit, kein Problem."},
            {"speaker": "Rico", "text": "Wenn etwas schiefgeht - fahr einfach ab. Es ist nur ein Auto."}
        ]
        phase2.stamina_cost = 3
        phase2.encounter_chance = 0.15
        
        phase3 = MissionPhase(
            "Autodiebstahl",
            "action",
            "Du findest das Zielauto in einer Einfahrt. Es hat eine Alarmanlage, aber sie sieht alt aus."
        )
        phase3.stealth_check = True
        phase3.base_success_chance = 0.6
        phase3.success_message = "Du knackst die Tür und startest den Motor leise. Das Auto ist dein!"
        phase3.failure_message = "Die Alarmanlage geht los! Die Nachbarn werden aufmerksam!"
        phase3.success_rewards = {"reputation": 2}
        phase3.failure_consequences = {"wanted_level": 1, "stamina": 5}
        
        phase4 = MissionPhase(
            "Flucht",
            "escape",
            "Die Polizei ist auf dem Weg! Du musst schnell zur Garage in Ocean Beach kommen."
        )
        phase4.wanted_increase = 2
        phase4.escape_success_message = "Du erreichst Ricos Garage und verlierst die Verfolger!"
        phase4.escape_failure_message = "Die Polizei stellt dich! Du musst das Auto verlassen und zu Fuß fliehen."
        
        mission.phases = [phase1, phase2, phase3, phase4]
        self.mission_manager.register_mission(mission)
    
    def create_beach_party_mission(self):
        mission = Mission(
            "Beach Party Cleanup",
            1,
            3,
            {"cash": 800, "reputation": 8, "partner_trust": 3},
            self.text_display
        )
        
        phase1 = MissionPhase(
            "Marias Problem",
            "dialogue",
            "Du triffst Maria in Little Haiti. Sie sieht gestresst aus und braucht Hilfe."
        )
        phase1.dialogue = [
            {"speaker": "Maria", "text": "Danke, dass du gekommen bist. Ich habe ein Problem..."},
            {"speaker": "Maria", "text": "Die Vipers Gang hat meine Drogen bei einer Beach Party gestohlen."},
            {"speaker": "Maria", "text": "Ich brauche jemanden, der sie zurückholt. Jemand, der nicht bekannt ist."},
            {"speaker": "Maria", "text": "Die Party ist heute Nacht in Ocean Beach. Sei vorsichtig - die Vipers sind gefährlich."}
        ]
        
        phase2 = MissionPhase(
            "Party-Infiltration",
            "action",
            "Du schleichst dich auf die Beach Party. Du musst die Drogen finden, ohne entdeckt zu werden."
        )
        phase2.stealth_check = True
        phase2.base_success_chance = 0.5
        phase2.success_message = "Du findest die Drogen in einem Rucksack hinter einem Beach Bar."
        phase2.failure_message = "Ein Viper Gangmitglied entdeckt dich! Die Alarmglocken läuten!"
        phase2.failure_consequences = {"wanted_level": 1, "stamina": 8}
        
        phase3 = MissionPhase(
            "Die Konfrontation",
            "action",
            "Die Vipers bemerken den Diebstahl! Du musst kämpfen, um zu entkommen."
        )
        phase3.combat_check = True
        phase3.base_success_chance = 0.4
        phase3.success_message = "Du besiegst die Vipers und kannst mit den Drogen entkommen!"
        phase3.failure_message = "Du wirst überwältigt und musst die Drogen zurücklassen!"
        phase3.success_rewards = {"reputation": 3}
        phase3.failure_consequences = {"stamina": 12, "partner_trust": 5}
        
        phase4 = MissionPhase(
            "Polizeiflucht",
            "escape",
            "Die Polizei ist wegen des Kampfes auf der Party alarmiert worden!"
        )
        phase4.wanted_increase = 2
        phase4.escape_success_message = "Du verlierst die Polizei in den engen Gassen von Ocean Beach!"
        phase4.escape_failure_message = "Die Polizei stellt dich! Du landest kurzzeitig in Gewahrsam."
        
        mission.phases = [phase1, phase2, phase3, phase4]
        mission.available = False
        self.mission_manager.register_mission(mission)
    
    def criminal_training(self):
        print("\n🏋️ KRIMINELLES TRAINING")
        print("Verbessere deine Fähigkeiten für einen Preis:")
        print(f"1. Kampfskill verbessern (+5) - Kosten: $500")
        print(f"2. Stealth verbessern (+5) - Kosten: $400")
        print(f"3. Level erhöhen (+1) - Kosten: $1000")
        
        try:
            choice = int(input("Wähle eine Trainingsoption (1-3): "))
            if choice == 1:
                if self.cash >= 500:
                    self.cash -= 500
                    self.combat_skill += 5
                    print("Deine Kampffähigkeiten haben sich verbessert!")
                    self.story_manager.check_chapter_progression(self)
                else:
                    print("Nicht genug Geld!")
            elif choice == 2:
                if self.cash >= 400:
                    self.cash -= 400
                    self.stealth += 5
                    print("Deine Stealth-Fähigkeiten haben sich verbessert!")
                    self.story_manager.check_chapter_progression(self)
                else:
                    print("Nicht genug Geld!")
            elif choice == 3:
                if self.cash >= 1000:
                    self.cash -= 1000
                    self.level += 1
                    self.stamina = self.level * 25
                    print(f"Du bist jetzt Level {self.level}!")
                    self.story_manager.check_chapter_progression(self)
                else:
                    print("Nicht genug Geld!")
            else:
                print("Ungültige Wahl!")
        except ValueError:
            print("Ungültige Eingabe!")
    
    def save_game(self, filename="data/saves/savegame.json"):
        save_data = {
            "name": self.name,
            "character_type": self.character_type,
            "cash": self.cash,
            "level": self.level,
            "inventory": [item.__dict__ for item in self.inventory],
            "stamina": self.stamina,
            "days": self.days,
            "wanted_level": self.wanted_level,
            "reputation": self.reputation,
            "drug_effects": [effect.__dict__ for effect in self.drug_effects],
            "dragon_encounters": self.dragon_encounters,
            "chapter": self.chapter,
            "partner_trust": self.partner_trust,
            "ankle_monitor": self.ankle_monitor,
            "combat_skill": self.combat_skill,
            "stealth": self.stealth,
            "dragon_defeated": getattr(self, 'dragon_defeated', False),
            "story_flags": self.story_flags,
            "clear_screen_enabled": self.text_display.clear_screen_enabled
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            print(f"Spiel gespeichert als {filename}!")
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
    
    def load_game(self, filename="data/saves/savegame.json"):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            self.name = save_data["name"]
            self.character_type = save_data["character_type"]
            self.cash = save_data["cash"]
            self.level = save_data["level"]
            self.inventory = [Weapon(**item) for item in save_data["inventory"]]
            self.stamina = save_data["stamina"]
            self.days = save_data["days"]
            self.wanted_level = save_data["wanted_level"]
            self.reputation = save_data["reputation"]
            self.drug_effects = [DrugEffect(**effect) for effect in save_data["drug_effects"]]
            self.dragon_encounters = save_data["dragon_encounters"]
            self.chapter = save_data["chapter"]
            self.partner_trust = save_data["partner_trust"]
            self.ankle_monitor = save_data["ankle_monitor"]
            self.combat_skill = save_data["combat_skill"]
            self.stealth = save_data["stealth"]
            self.dragon_defeated = save_data.get("dragon_defeated", False)
            self.story_flags = save_data.get("story_flags", {
                "first_crime_committed": False,
                "first_dragon_seen": False,
                "partner_betrayed": False,
                "redemption_offered": False
            })
            self.text_display.clear_screen_enabled = save_data.get("clear_screen_enabled", False)
            
            return True
        except FileNotFoundError:
            print("Kein Speicherstand gefunden!")
            return False
        except Exception as e:
            print(f"Fehler beim Laden: {e}")
            return False
    
    def save_dragon(self, dragon, filename="data/dragon.json"):
        dragon_data = {
            "stamina": dragon.stamina,
            "defeated": dragon.defeated,
            "manifestation": dragon.manifestation
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(dragon_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Fehler beim Speichern des Drachen: {e}")
    
    def load_dragon(self, filename="data/dragon.json"):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                dragon_data = json.load(f)
            
            dragon = ViceCityDragon()
            dragon.stamina = dragon_data["stamina"]
            dragon.defeated = dragon_data["defeated"]
            dragon.manifestation = dragon_data.get("manifestation", "metaphorisch")
            
            return dragon
        except FileNotFoundError:
            return ViceCityDragon()
        except Exception as e:
            print(f"Fehler beim Laden des Drachen: {e}")
            return ViceCityDragon()
