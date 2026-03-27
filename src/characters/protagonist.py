import time
import random

from src.ui.text_display import TextDisplayManager
from src.story.story_manager import StoryManager
from src.story.journal import Journal
from src.missions.mission_manager import MissionManager
from src.missions.mission import Mission, MissionPhase
from src.missions.mission_giver import MissionGiver
from src.districts.district_manager import DistrictManager
from src.game.mission_logic import MissionBoardService
from src.game.persistence import GamePersistence
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
        self.stress_level = 20
        self.hallucination_intensity = 0.0
        self.delayed_consequences = []
        self.chapter = 1
        self.partner_trust = 100
        self.ankle_monitor = character_type == "lucia"
        self.dragon_defeated = False
        
        self.ng_plus_unlocked = False
        self.new_game_plus_active = False
        self.new_game_plus_cycle = 0
        self.mission_modifier = "standard"
        self.district_condition = "normal"
        self.endgame_report = {}
        self.branch_choices = []
        self.run_completed = False
        self.run_history = {
            "runs_completed": 0,
            "victories": 0,
            "defeats": 0,
            "highest_wanted": 0,
            "highest_reputation": 0,
            "lowest_partner_trust": 100
        }
        
        self.text_display = TextDisplayManager()
        self.story_manager = StoryManager(self.text_display)
        self.story_flags = {
            "first_crime_committed": False,
            "first_dragon_seen": False,
            "partner_betrayed": False,
            "partner_loyalty_path": False,
            "redemption_offered": False,
            "first_mission_completed": False,
            "decision_flags": {},
            "shown_consequence_events": []
        }
        self.consequence_manager = ConsequenceManager(self.story_flags["decision_flags"])
        self.mission_manager = MissionManager()
        self.mission_board = MissionBoardService(self.mission_manager)
        self.persistence = GamePersistence()
        self.district_manager = DistrictManager(self)
        self.current_district_context = None
        
        if character_type == "jason":
            self.combat_skill = 15
            self.stealth = 10
        else:
            self.combat_skill = 10
            self.stealth = 15
        self.escape_route_bonus = 0.0

    def _character_action_bonus(self, action_type):
        bonuses = {
            "jason": {
                "ambush": 0.12,
                "direct_assault": 0.10,
                "silent_takedown": -0.03,
                "distraction": 0.01,
                "escape_route_planning": 0.03,
            },
            "lucia": {
                "ambush": 0.05,
                "direct_assault": -0.05,
                "silent_takedown": 0.14,
                "distraction": 0.13,
                "escape_route_planning": 0.12,
            },
        }
        return bonuses.get(self.character_type, {}).get(action_type, 0.0)
    
    def display_attributes(self):
        self.update_run_tracking()
        print(f"\n[SPIELER] {self.name.upper()} - {self.character_type.upper()}")
        print(f"[CASH] Cash: ${self.cash}")
        print(f"[LEVEL] Level: {self.level}")
        print(f"[AUSDAUER] Ausdauer: {self.stamina}")
        print(f"[WAFFEN] Inventar: {[item.name for item in self.inventory]}")
        print(f"[WANTED] Wanted Level: {self.wanted_level}")
        print(f"[REPUTATION] Reputation: {self.reputation}")
        print(f"[TAGE] Tage in Vice City: {self.days}")
        print(f"[DRACHEN] Drachen-Begegnungen: {self.dragon_encounters}")
        print(f"[PSYCHE] Stress: {self.stress_level} | Halluzinations-Intensität: {self.hallucination_intensity:.2f}")
        print(f"[PARTNER] Partner-Vertrauen: {self.partner_trust}%")
        print(f"[MODUS] NG+ aktiv: {'Ja' if self.new_game_plus_active else 'Nein'} (Zyklus {self.new_game_plus_cycle})")
        print(f"[MODIFIER] Missionen: {self.mission_modifier} | Distrikte: {self.district_condition}")
        if self.ankle_monitor:
            print("[FUSSFESSEL] Fußfessel aktiv (Einschränkungen bei Aktivitäten)")
        print("\n[REPUTATION] Distrikt-Reputation:")
        for district in self.district_manager.districts.values():
            print(f"- {district.name}: {district.reputation}")

    def get_district_reputation(self, district_name=None):
        target_district = district_name or self.current_district_context
        if target_district and target_district in self.district_manager.districts:
            return self.district_manager.districts[target_district].reputation
        return 0

    def get_average_district_reputation(self):
        districts = list(self.district_manager.districts.values())
        if not districts:
            return 0
        return int(sum(district.reputation for district in districts) / len(districts))

    def adjust_district_reputation(self, amount, district_name=None):
        target_district = district_name or self.current_district_context
        if target_district and target_district in self.district_manager.districts:
            district = self.district_manager.districts[target_district]
            district.reputation = max(-100, min(100, district.reputation + amount))
    
    def switch_character(self):
        pass

    def get_drug_pressure(self):
        if not self.drug_effects:
            return 0.0
        pressure = 0.0
        for effect in self.drug_effects:
            if effect.duration <= 0:
                continue
            pressure += effect.intensity * (effect.remaining / effect.duration)
        return min(1.5, pressure)

    def update_psychological_state(self, context="general"):
        base_stress = (self.wanted_level * 6) + (5 if self.partner_trust < 35 else 0)
        self.stress_level = min(100, max(0, self.stress_level + base_stress // 4))

        active_effects = []
        for effect in self.drug_effects:
            hallucinated = effect.apply_effect(self)
            if hallucinated:
                self.dragon_encounters += 1
            if effect.remaining > 0:
                active_effects.append(effect)
        self.drug_effects = active_effects

        pressure = self.get_drug_pressure()
        self.hallucination_intensity = min(1.0, (self.stress_level / 100) * 0.65 + (pressure * 0.55))

        if context == "rest":
            self.stress_level = max(0, self.stress_level - 20)
        elif context == "combat":
            self.stress_level = min(100, self.stress_level + 8)

        if self.hallucination_intensity > 0.55 and random.random() < self.hallucination_intensity * 0.2:
            dragon = DragonHallucination()
            trigger = random.choice(["high_stress", "drug_use"])
            dragon.trigger_encounter(trigger, self, self.hallucination_intensity)

    def apply_delayed_consequences(self):
        if not self.delayed_consequences:
            return
        pending = self.delayed_consequences[:]
        self.delayed_consequences = []
        print("\n[SPÄTFOLGEN] Verdrängte Konsequenzen holen dich ein...")
        for consequence in pending:
            if consequence == "wanted_spike":
                self.wanted_level = min(5, self.wanted_level + 1)
                print("Sirenen in der Ferne: Wanted Level steigt um 1.")
            elif consequence == "cash_loss":
                lost = random.randint(80, 220)
                self.cash = max(0, self.cash - lost)
                print(f"Du bemerkst einen fehlenden Geldstapel: -${lost}.")
            elif consequence == "trust_drop":
                self.partner_trust = max(0, self.partner_trust - 8)
                print("Dein Partner erinnert sich an dein wirres Verhalten: Vertrauen sinkt.")

    def distort_text(self, text):
        dragon = DragonHallucination()
        return dragon.distort_text(text, self.hallucination_intensity)

    def maybe_unreliable_dialogue(self, speaker, text):
        chance = self.hallucination_intensity * 0.45
        if random.random() < chance:
            fragments = [
                " ...oder war das nur ein Flüstern?",
                " [Deine Erinnerung springt.]",
                " (Die Stimme klingt plötzlich wie ein Drachenknurren.)"
            ]
            return self.distort_text(text + random.choice(fragments))
        return text

    def build_perceived_choices(self, choices):
        perceived = [{"kind": "real", "choice": c} for c in choices]
        random.shuffle(perceived)
        if self.hallucination_intensity > 0.45 and random.random() < self.hallucination_intensity * 0.6:
            false_choice = {
                "text": self.distort_text("Dem Drachen folgen"),
                "response": "Du folgst einer Illusion in eine Sackgasse.",
                "consequences": {"stamina": 6}
            }
            perceived.append({"kind": "false", "choice": false_choice})
            random.shuffle(perceived)
        return perceived
    
    def update_run_tracking(self):
        self.run_history["highest_wanted"] = max(self.run_history["highest_wanted"], self.wanted_level)
        self.run_history["highest_reputation"] = max(self.run_history["highest_reputation"], self.reputation)
        self.run_history["lowest_partner_trust"] = min(self.run_history["lowest_partner_trust"], self.partner_trust)
    
    def record_branch_choice(self, mission_name, phase_name, choice_text):
        self.branch_choices.append({
            "mission": mission_name,
            "phase": phase_name,
            "choice": choice_text
        })
    
    def get_mission_success_modifier(self):
        modifiers = {
            "standard": 0.0,
            "clean_getaway": -0.05,
            "heat_wave": -0.12,
            "all_or_nothing": -0.18
        }
        return modifiers.get(self.mission_modifier, 0.0)
    
    def get_escape_modifier(self):
        modifiers = {
            "standard": 0.0,
            "clean_getaway": 0.08,
            "heat_wave": -0.1,
            "all_or_nothing": -0.15
        }
        return modifiers.get(self.mission_modifier, 0.0)
    
    def get_reward_multiplier(self):
        multipliers = {
            "standard": 1.0,
            "clean_getaway": 1.2,
            "heat_wave": 1.35,
            "all_or_nothing": 1.6
        }
        return multipliers.get(self.mission_modifier, 1.0)
    
    def get_district_pressure_multiplier(self):
        conditions = {
            "normal": 1.0,
            "crackdown": 1.25,
            "blackout": 1.45,
            "martial_law": 1.65
        }
        return conditions.get(self.district_condition, 1.0)
    
    def rest(self, location="sicherer Unterschlupf"):
        print(f"\n[RUHEN] Du ruhst dich in {location} aus...")
        self.days += 1
        self.stamina = self.level * 25
        self.wanted_level = max(0, self.wanted_level - 1)
        self.update_psychological_state(context="rest")
        self.apply_delayed_consequences()
        
        if self.dragon_encounters > 0 and random.random() < (0.2 + self.hallucination_intensity * 0.3):
            dragon = DragonHallucination()
            dragon.trigger_encounter("high_stress", self, self.hallucination_intensity)
            
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
        self.current_district_context = district.name
        district.describe()
        
        if district.special_feature in district.discovered_features:
            self.handle_district_feature(district)
            return
        self.explore_district_regular(district)
    
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
        self.current_district_context = district.name
        if self.ankle_monitor and random.random() < 0.3:
            print("\n[FUSSFESSEL] Deine Fußfessel schlägt Alarm! Die Polizei ist auf dem Weg!")
            self.wanted_level = min(5, self.wanted_level + 2)
            self.stamina = max(1, self.stamina - 5)
            return

        if self.trigger_world_event(district):
            return

        encounter_chance = 0.3 + (district.danger_level * 0.1)
        
        if random.random() < encounter_chance:
            self.criminal_encounter(district)
        else:
            print("\n[STADT] Die Straße ist ruhig. Du findest nichts Nützliches hier.")
            self.stamina = max(1, self.stamina - 2)

    def _get_player_progress_score(self):
        completed_missions = len(self.story_flags.get("completed_missions", []))
        return self.level + (self.chapter * 0.8) + (self.reputation / 25) + (completed_missions * 0.5)

    def trigger_world_event(self, district):
        progress_score = self._get_player_progress_score()
        season = self.district_manager.current_season

        event_chance = 0.2 + (district.danger_level * 0.03) + (self.wanted_level * 0.04)
        if season == "high_season":
            event_chance += 0.08
        elif season == "low_season":
            event_chance -= 0.04
        if progress_score >= 10:
            event_chance += 0.06

        if random.random() >= min(0.85, event_chance):
            return False

        event_pool = [
            {"type": "informant", "weight": 2.2},
            {"type": "market", "weight": 2.0},
            {"type": "unexpected", "weight": 1.8},
            {"type": "ambush", "weight": 1.4 + (district.danger_level * 0.15)}
        ]

        if self.wanted_level >= 2:
            event_pool.append({"type": "checkpoint", "weight": 1.5 + (self.wanted_level * 0.6)})
        if district.name in {"Ocean Beach", "Washington Beach", "Vice Point", "Downtown"}:
            event_pool.append({"type": "street_race", "weight": 1.7 + (0.2 if season == "high_season" else 0)})
        if district.name in {"Viceport", "Little Haiti", "Everglades", "Vice Keys"}:
            event_pool.append({"type": "ambush", "weight": 0.8})
        if season == "high_season":
            event_pool.append({"type": "market", "weight": 0.9})
            event_pool.append({"type": "street_race", "weight": 0.6})
        if season == "low_season":
            event_pool.append({"type": "informant", "weight": 0.8})
            event_pool.append({"type": "checkpoint", "weight": 0.5})

        event_type = random.choices(
            [event["type"] for event in event_pool],
            weights=[event["weight"] for event in event_pool],
            k=1
        )[0]

        print(f"\n[WORLD EVENT] Dynamisches Ereignis in {district.name}!")
        handlers = {
            "street_race": self.street_race_event,
            "checkpoint": self.police_checkpoint_event,
            "informant": self.informant_event,
            "ambush": self.ambush_event,
            "market": self.market_opportunity_event,
            "unexpected": self.unexpected_encounter_event
        }
        handlers[event_type](district, progress_score)
        return True

    def street_race_event(self, district, progress_score):
        print("[RACE] Illegales Straßenrennen entdeckt.")
        action = input("Willst du teilnehmen oder sabotieren? (teilnehmen/sabotieren) ")
        skill_factor = 0.45 + (self.stealth * 0.015) + min(0.15, progress_score * 0.01)
        success = random.random() < skill_factor

        if success:
            prize = random.randint(180, 520) + (district.danger_level * 20)
            print(f"Du dominierst das Rennen und kassierst ${prize}!")
            self.cash += prize
            self.reputation += 3
            self.stamina = max(1, self.stamina - 6)
        else:
            print("Das Rennen eskaliert. Sirenen nähern sich!")
            self.wanted_level = min(5, self.wanted_level + 1)
            self.stamina = max(1, self.stamina - 10)

    def police_checkpoint_event(self, district, progress_score):
        print("[CHECKPOINT] Polizeikontrolle blockiert mehrere Ausgänge.")
        evade_chance = 0.35 + (self.stealth * 0.02) + min(0.12, progress_score * 0.01) - (self.wanted_level * 0.08)
        if random.random() < evade_chance:
            print("Du umgehst den Checkpoint über Seitenstraßen.")
            self.reputation += 1
            self.stamina = max(1, self.stamina - 4)
            return

        print("Die Polizei erkennt dich und greift durch!")
        self.wanted_level = min(5, self.wanted_level + 1)
        if district.danger_level >= 7:
            self.customs_encounter()
        else:
            self.police_encounter()

    def informant_event(self, district, progress_score):
        print("[INFORMANT] Ein Informant bietet Insider-Infos über lokale Ziele.")
        buy_in = 80 if progress_score < 8 else 140
        action = input(f"Infos kaufen für ${buy_in}? (ja/nein) ")
        if action != "ja":
            print("Du lehnst den Deal ab und ziehst weiter.")
            return
        if self.cash < buy_in:
            print("Nicht genug Cash für den Deal.")
            return

        self.cash -= buy_in
        payout = random.randint(160, 420) + int(progress_score * 10)
        print(f"Die Information zahlt sich aus. Profit: ${payout}!")
        self.cash += payout
        district.reputation += 2
        self.reputation += 2

    def ambush_event(self, district, progress_score):
        print("[AMBUSH] Eine rivalisierende Crew legt dir einen Hinterhalt.")
        ambush_power = 0.45 + (district.danger_level * 0.04) + (self.wanted_level * 0.05)
        defense_power = 0.35 + (self.combat_skill * 0.02) + min(0.15, progress_score * 0.01)
        if random.random() < max(0.1, defense_power - ambush_power + 0.5):
            loot = random.randint(120, 380)
            print(f"Du durchbrichst den Hinterhalt und sicherst ${loot}.")
            self.cash += loot
            self.reputation += 4
            self.stamina = max(1, self.stamina - 7)
        else:
            print("Der Hinterhalt trifft hart. Du verlierst Ressourcen.")
            self.cash = max(0, self.cash - random.randint(80, 220))
            self.stamina = max(1, self.stamina - 12)
            self.wanted_level = min(5, self.wanted_level + 1)

    def market_opportunity_event(self, district, progress_score):
        season = self.district_manager.current_season
        print("[MARKT] Ein temporäres Schwarzmarktfenster öffnet sich.")
        seasonal_bonus = 1.25 if season == "high_season" else 0.8 if season == "low_season" else 1.0
        base_profit = random.randint(90, 320)
        adjusted_profit = int((base_profit + (district.danger_level * 12)) * seasonal_bonus)
        risk = 0.2 + (self.wanted_level * 0.07)
        action = input("Chance nutzen? (ja/nein) ")
        if action != "ja":
            print("Du wartest auf eine bessere Gelegenheit.")
            return

        if random.random() < risk:
            print("Der Deal wird von verdeckten Ermittlern gestört!")
            self.wanted_level = min(5, self.wanted_level + 1)
            self.stamina = max(1, self.stamina - 8)
        else:
            print(f"Sauberer Deal. Gewinn: ${adjusted_profit}.")
            self.cash += adjusted_profit
            self.reputation += 2
            district.reputation += 1
            self.stamina = max(1, self.stamina - 5)

    def unexpected_encounter_event(self, district, progress_score):
        surprises = [
            "Ein VIP verliert eine Tasche neben dir.",
            "Ein alter Kontakt schickt dir eine spontane Jobchance.",
            "Ein Straßenkünstler deckt einen Geldtransport auf.",
            "Ein beschädigter Lieferwagen steht verlassen am Rand."
        ]
        print(f"[ENCOUNTER] {random.choice(surprises)}")
        good_outcome_chance = 0.5 + min(0.2, progress_score * 0.01) - (self.wanted_level * 0.04)
        if random.random() < good_outcome_chance:
            reward = random.randint(100, 260)
            print(f"Du nutzt den Moment perfekt und machst ${reward}.")
            self.cash += reward
            self.reputation += 1
        else:
            print("Die Situation kippt unerwartet gegen dich.")
            self.stamina = max(1, self.stamina - 6)
            if district.danger_level > 6:
                self.wanted_level = min(5, self.wanted_level + 1)
    
    def criminal_encounter(self, district):
        self.update_psychological_state(context="street")
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
        print(f"\n[WAFFEN] {self.distort_text(encounter['description'])}")
        
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
        base_stats = {
            "police": {"stamina": 30, "damage": 8, "wanted_increase": 1},
            "security": {"stamina": 25, "damage": 6, "wanted_increase": 1},
            "swat": {"stamina": 50, "damage": 15, "wanted_increase": 3},
            "coast_guard": {"stamina": 35, "damage": 10, "wanted_increase": 2},
            "motel_security": {"stamina": 20, "damage": 5, "wanted_increase": 1},
            "dock_security": {"stamina": 30, "damage": 7, "wanted_increase": 1},
            "customs": {"stamina": 40, "damage": 12, "wanted_increase": 2},
            "container_guard": {"stamina": 28, "damage": 6, "wanted_increase": 1},
            "private_security": {"stamina": 45, "damage": 11, "wanted_increase": 2}
        }
        stats = base_stats.get(police_type, {"stamina": 30, "damage": 8, "wanted_increase": 1}).copy()
        district_rep = self.get_district_reputation()
        pressure_modifier = max(-0.2, min(0.2, -district_rep / 200))
        stats["stamina"] = max(10, int(stats["stamina"] * (1 + pressure_modifier)))
        stats["damage"] = max(2, int(stats["damage"] * (1 + pressure_modifier)))
        if district_rep <= -40:
            stats["wanted_increase"] += 1
        elif district_rep >= 40:
            stats["wanted_increase"] = max(0, stats["wanted_increase"] - 1)
        return stats
    
    def _get_bribe_cost(self, police_type):
        base_cost = {
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
        district_rep = self.get_district_reputation()
        modifier = max(0.7, min(1.4, 1 - (district_rep / 250)))
        return int(base_cost * modifier)
    
    def _handle_police_choice(self, police_type, action):
        if action == "kämpfen":
            self.record_decision("police_heat_high", f"police_encounter:{police_type}")
            self.combat_police(police_type)
        elif action == "fliehen":
            self.record_decision("silent_operator", f"police_encounter:{police_type}")
            self.flee_police(police_type)
        elif action == "bestechen":
            self.record_decision("corrupt_contacts", f"police_encounter:{police_type}")
            self.bribe_police(police_type)
        elif action == "ambush":
            self.ambush_police(police_type)
        elif action == "ablenken":
            self.distraction_escape(police_type)
        elif action == "silent":
            self.silent_takedown(police_type)
        elif action == "route":
            self.plan_escape_route(police_type)
        else:
            print("Du zögerst zu lange!")
            self.combat_police(police_type)

    def _police_action_prompt(self):
        return input(
            "Aktion: kämpfen, fliehen, bestechen, ambush, ablenken, silent oder route? "
        ).strip().lower()
    
    def police_encounter(self):
        print("\n[POLICE] POLIZEI-KONFRONTATION")
        action = self._police_action_prompt()
        self._handle_police_choice("police", action)
    
    def security_encounter(self):
        print("\n[SECURITY] SICHERHEITS-KONFRONTATION")
        action = self._police_action_prompt()
        self._handle_police_choice("security", action)
    
    def motel_security_encounter(self):
        print("\n[MOTEL] MOTEL-SICHERHEITS-KONFRONTATION")
        action = self._police_action_prompt()
        self._handle_police_choice("motel_security", action)
    
    def swat_encounter(self):
        print("\n[SWAT] SWAT-KONFRONTATION")
        action = self._police_action_prompt()
        self._handle_police_choice("swat", action)
    
    def dock_security_encounter(self):
        print("\n[DOCK] DOCK-SICHERHEITS-KONFRONTATION")
        action = self._police_action_prompt()
        self._handle_police_choice("dock_security", action)
    
    def customs_encounter(self):
        print("\n[CUSTOMS] ZOLL-KONFRONTATION")
        action = self._police_action_prompt()
        self._handle_police_choice("customs", action)
    
    def container_guard_encounter(self):
        print("\n[CONTAINER] CONTAINER-WÄCHTER-KONFRONTATION")
        action = self._police_action_prompt()
        self._handle_police_choice("container_guard", action)
    
    def private_security_encounter(self):
        print("\n[PRIVATE] PRIVATE-SICHERHEITS-KONFRONTATION")
        action = self._police_action_prompt()
        self._handle_police_choice("private_security", action)
    
    def coast_guard_encounter(self):
        print("\n[COAST] KÜSTENWACHE-KONFRONTATION")
        action = self._police_action_prompt()
        self._handle_police_choice("coast_guard", action)
    
    def combat_police(self, police_type):
        stats = self._get_police_stats(police_type)
        district_rep = self.get_district_reputation()
        combat_chance = 0.3 + (self.combat_skill * 0.02) + (len(self.inventory) * 0.05) + (district_rep * 0.002)
        
        if random.random() < combat_chance:
            print(f"Du besiegst die {police_type}-Einheit!")
            cash_found = random.randint(100, 500)
            self.cash += cash_found
            self.wanted_level = min(5, self.wanted_level + stats["wanted_increase"])
            self.reputation += 5
            self.adjust_district_reputation(2)
            print(f"Du findest ${cash_found} bei den Besiegten!")
            print(f"Wanted Level: {self.wanted_level}")
        else:
            print(f"Du wirst von der {police_type}-Einheit besiegt!")
            self.cash = max(0, self.cash // 2)
            self.wanted_level = min(5, self.wanted_level + stats["wanted_increase"] + 1)
            self.stamina = max(1, self.stamina - 15)
            self.days += 1
            self.adjust_district_reputation(-3)
            print("Du verlierst die Hälfte deines Geldes und landest im Krankenhaus!")
            
            if random.random() < 0.4:
                dragon = DragonHallucination()
                dragon.trigger_encounter("high_stress", self, self.hallucination_intensity)
    
    def flee_police(self, police_type):
        district_rep = self.get_district_reputation()
        flee_chance = 0.5 + (self.stealth * 0.03) - (self.wanted_level * 0.1) + (district_rep * 0.002)
        
        if random.random() < flee_chance:
            print("Du kannst erfolgreich entkommen!")
            self.stamina = max(1, self.stamina - 10)
        else:
            print("Deine Flucht schlägt fehl!")
            self.combat_police(police_type)

    def plan_escape_route(self, police_type):
        print("Du analysierst Nebenstraßen, Kamerawinkel und mögliche Deckung.")
        route_roll = 0.45 + (self.stealth * 0.02) + self._character_action_bonus("escape_route_planning")
        if random.random() < route_roll:
            self.escape_route_bonus = min(0.25, self.escape_route_bonus + 0.16)
            self.stamina = max(1, self.stamina - 2)
            print("Fluchtroute vorbereitet! Deine nächste Flucht ist deutlich besser.")
            self.flee_police(police_type)
        else:
            print("Die Route ist schlecht gewählt - ihr habt dich fast eingekesselt.")
            self.wanted_level = min(5, self.wanted_level + 1)
            self.flee_police(police_type)

    def ambush_police(self, police_type):
        print("Du setzt auf einen riskanten Hinterhalt.")
        ambush_chance = 0.35 + (self.combat_skill * 0.02) + self._character_action_bonus("ambush")
        if random.random() < ambush_chance:
            loot = random.randint(150, 350)
            self.cash += loot
            self.reputation += 6
            self.wanted_level = min(5, self.wanted_level + 2)
            print(f"Hinterhalt erfolgreich! Du sicherst ${loot}, aber die Stadt redet darüber.")
        else:
            print("Der Hinterhalt scheitert, Verstärkung trifft ein!")
            self.wanted_level = min(5, self.wanted_level + 2)
            self.combat_police(police_type)

    def distraction_escape(self, police_type):
        print("Du erzeugst eine Ablenkung, um ungesehen abzutauchen.")
        distraction_chance = 0.4 + (self.stealth * 0.03) + self._character_action_bonus("distraction")
        if random.random() < distraction_chance:
            self.stamina = max(1, self.stamina - 4)
            self.wanted_level = max(0, self.wanted_level - 1)
            print("Ablenkung gelungen! Die Verfolger verlieren deine Spur.")
        else:
            print("Die Ablenkung klappt nicht.")
            self.flee_police(police_type)

    def silent_takedown(self, police_type):
        print("Du versuchst einen lautlosen Takedown auf den Anführer.")
        takedown_chance = 0.32 + (self.stealth * 0.03) + self._character_action_bonus("silent_takedown")
        if random.random() < takedown_chance:
            self.reputation += 4
            self.stamina = max(1, self.stamina - 5)
            print("Silent Takedown erfolgreich! Das Team ist kurz desorientiert.")
            self.distraction_escape(police_type)
        else:
            print("Takedown fehlgeschlagen! Nahkampf bricht aus.")
            self.combat_police(police_type)
    
    def bribe_police(self, police_type):
        cost = self._get_bribe_cost(police_type)
        
        if self.cash >= cost:
            self.cash -= cost
            district_rep = self.get_district_reputation()
            bribe_success_chance = 0.65 + (district_rep * 0.005)
            if random.random() < bribe_success_chance:
                print(f"Du bestechst die {police_type}-Einheit mit ${cost}!")
                wanted_drop = 2 if district_rep >= 30 else 1
                self.wanted_level = max(0, self.wanted_level - wanted_drop)
                self.adjust_district_reputation(1)
            else:
                print(f"Die Bestechung in Höhe von ${cost} wird abgelehnt!")
                self.wanted_level = min(5, self.wanted_level + 1)
                self.adjust_district_reputation(-2)
                self.combat_police(police_type)
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
            print("Du verlierst Geld und das Vertrauen deines Partners!")            
            self.adjust_partner_trust(-15, "Niederlage gegen Gang")
            
            if random.random() < 0.6:
                dragon = DragonHallucination()
                dragon.trigger_encounter("betrayal", self, self.hallucination_intensity)
    
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
        self.update_psychological_state(context="drug_offer")
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
                self.stress_level = min(100, self.stress_level + int(drug["intensity"] * 12))
                
                if drug["intensity"] > 0.6:
                    effect.trigger_dragon_hallucination(self)
                    
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
        self.update_psychological_state(context="opportunity")
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
                print("Ansatz: 1) Ablenkung 2) Silent Takedown 3) Ambush")
                tactic_choice = input("Wähle Taktik (1-3): ").strip()
                tactic_map = {
                    "1": ("distraction", 0.08, 0.35),
                    "2": ("silent_takedown", 0.1, 0.45),
                    "3": ("ambush", 0.07, 0.55),
                }
                tactic, tactic_bonus, tactic_risk = tactic_map.get(tactic_choice, ("distraction", 0.05, 0.3))

                success_chance = (
                    0.6
                    + (self.stealth * 0.02)
                    - (district.danger_level * 0.05)
                    + tactic_bonus
                    + self._character_action_bonus(tactic)
                )
                success_chance = max(0.08, min(0.95, success_chance))

                roll = random.random()
                critical_success = min(0.98, success_chance + tactic_risk * 0.35)
                critical_failure = max(0.02, success_chance - tactic_risk * 0.5)

                if roll > critical_success:
                    jackpot = int(opp["cash"] * 1.8)
                    print(f"Kritischer Erfolg! Dein riskanter Plan bringt ${jackpot}!")
                    self.cash += jackpot
                    self.reputation += 5
                    self.stamina -= opp["stamina_cost"]
                elif roll < critical_failure:
                    print("Kritischer Fehler! Die Aktion eskaliert komplett.")
                    self.wanted_level = min(5, self.wanted_level + 2)
                    self.stamina = max(1, self.stamina - opp["stamina_cost"] - 10)
                    self.cash = max(0, self.cash - random.randint(50, 200))
                elif roll < success_chance:
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
                    if self.hallucination_intensity > 0.6 and random.random() < 0.5:
                        self.delayed_consequences.append("wanted_spike")
                        print("Du bist sicher, dass dich niemand gesehen hat... vorerst.")
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
            self.adjust_partner_trust(10, "Partner respektiert deine Hilfe")
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
        self.update_psychological_state(context="market")
        weapons = [
            Weapon("Messer", 100, 5, 2),
            Weapon("Pistole", 500, 10, 3),
            Weapon("Schrotflinte", 1500, 15, 4),
            Weapon("Sturmgewehr", 3000, 25, 5),
            Weapon("Scharfschützengewehr", 5000, 35, 5)
        ]
        market_rep = self.get_district_reputation("Vice Keys")
        if market_rep == 0:
            market_rep = self.get_average_district_reputation()
        price_modifier = max(0.7, min(1.35, 1 - (market_rep / 250)))
        
        print("\n[WAFFEN] SCHWARZMARKT - Illegale Waffen")
        print(f"Händler-Stimmung (Reputation): {market_rep} | Preisfaktor: {price_modifier:.2f}x")
        print("Hier sind die verfügbaren Waffen:")
        for i, weapon in enumerate(weapons):
            owned = " (Bereits besitzt)" if weapon.name in [owned_item.name for owned_item in self.inventory] else ""
            adjusted_cost = int(weapon.cost * price_modifier)
            print(f"{i + 1}. {weapon.name} - Kosten: ${adjusted_cost} - Schaden: +{weapon.damage_increase} - Illegalität: {'⚠️' * weapon.illegal_status}{owned}")
        
        try:
            choice = int(input("Welche Waffe möchtest du kaufen? (Gib die Nummer ein) "))
            if 1 <= choice <= len(weapons):
                weapon = weapons[choice - 1]
                adjusted_cost = int(weapon.cost * price_modifier)
                if weapon.name in [owned_item.name for owned_item in self.inventory]:
                    print(f"Du besitzt bereits eine {weapon.name}!")
                elif self.cash >= adjusted_cost:
                    self.cash -= adjusted_cost
                    self.inventory.append(weapon)
                    self.adjust_district_reputation(1, "Vice Keys")
                    print(f"Du hast eine {weapon.name} für ${adjusted_cost} gekauft!")
                    self.wanted_level = min(5, self.wanted_level + (weapon.illegal_status // 2))
                    print(f"Wanted Level erhöht: {self.wanted_level}")
                else:
                    print(f"Du hast nicht genug Geld für diese Waffe (${adjusted_cost} benötigt)!")
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
        if self.partner_trust >= 75:
            print("Dein Partner bleibt an deiner Seite. Ihr verlasst Vice City gemeinsam - Loyalitäts-Ende.")
        elif self.partner_trust <= 25:
            print("Du überlebst, aber allein. Dein Partner ist verschwunden - Einsames-Ende.")
        else:
            print("Ihr geht getrennte Wege, aber ohne offenen Verrat - Bittersüßes Ende.")
        print("Die Vice City Dragons Saga ist beendet. Du bist frei!")
        
        self.dragon_defeated = True
        self.finalize_run("victory")
    
    def dragon_defeat(self, dragon):
        print("\n*** DEINE KONSEKUENZEN HOLEN DICH EIN ***")
        print("Der Drache der Konsequenzen hat dich verschlungen.")
        print("Du verlierst alles und landest fuer immer im Gefaengnis... oder schlimmer.")
        
        self.cash = 0
        self.wanted_level = 5
        self.partner_trust = 0
        self.days += 7
        self.stamina = 10
        if self.story_flags.get("partner_betrayed"):
            print("Dein Partner verrät dich an die Polizei. Das ist das Verrats-Ende.")
        else:
            print("Dein Partner kann dich nicht mehr retten. Ihr scheitert gemeinsam.")
        print("Alles ist verloren. Das kriminelle Leben hat dich bezahlt.")
        self.finalize_run("defeat")
    
    def determine_branch_ending(self, outcome):
        betrayed = any("Haken" in choice["choice"] for choice in self.branch_choices)
        
        if outcome == "defeat":
            return (
                "ENDUNG: DRACHENKERKER",
                "Du wirst zur Legende als Warnung: Macht ohne Grenzen endet in Ketten."
            )
        
        if self.partner_trust >= 75 and self.reputation >= 45 and self.wanted_level <= 2:
            return (
                "ENDUNG: PAKT DER LOYALITÄT",
                "Mit Vertrauen und Reputation baust du ein legales Imperium aus den Resten der Unterwelt."
            )
        
        if self.wanted_level >= 4 and self.reputation >= 60:
            return (
                "ENDUNG: SCHATTENKOENIG*IN",
                "Du herrschst aus dem Verborgenen. Vice City flüstert deinen Namen mit Angst."
            )
        
        if self.partner_trust <= 30 or betrayed:
            return (
                "ENDUNG: EINSAME KRONE",
                "Dein Aufstieg war erfolgreich, aber jede Brücke ist verbrannt. Niemand traut dir mehr."
            )
        
        return (
            "ENDUNG: SCHMALER GRAT",
            "Du überlebst und findest einen fragilen Frieden zwischen Schuld und Zukunft."
        )
    
    def _compile_endgame_report(self, outcome):
        title, description = self.determine_branch_ending(outcome)
        completed_missions = self.story_flags.get("completed_missions", [])
        self.run_history["highest_wanted"] = max(self.run_history["highest_wanted"], self.wanted_level)
        self.run_history["highest_reputation"] = max(self.run_history["highest_reputation"], self.reputation)
        self.run_history["lowest_partner_trust"] = min(self.run_history["lowest_partner_trust"], self.partner_trust)
        
        return {
            "outcome": outcome,
            "ending_title": title,
            "ending_description": description,
            "character": self.character_type,
            "name": self.name,
            "chapter": self.chapter,
            "level": self.level,
            "cash": self.cash,
            "wanted_level": self.wanted_level,
            "reputation": self.reputation,
            "partner_trust": self.partner_trust,
            "days": self.days,
            "dragon_encounters": self.dragon_encounters,
            "completed_missions": completed_missions,
            "branch_choices": self.branch_choices[-6:],
            "mission_modifier": self.mission_modifier,
            "district_condition": self.district_condition,
            "ng_plus_cycle": self.new_game_plus_cycle
        }
    
    def finalize_run(self, outcome):
        if self.run_completed:
            return
        self.update_run_tracking()
        self.run_completed = True
        self.ng_plus_unlocked = True
        self.run_history["runs_completed"] += 1
        if outcome == "victory":
            self.run_history["victories"] += 1
        else:
            self.run_history["defeats"] += 1
        self.endgame_report = self._compile_endgame_report(outcome)
    
    def show_endgame_summary(self):
        if not self.endgame_report:
            print("Noch keine Run-Zusammenfassung verfügbar.")
            return
        
        report = self.endgame_report
        print("\n=== RUN-ZUSAMMENFASSUNG ===")
        print(f"{report['ending_title']}")
        print(report["ending_description"])
        print(f"Charakter: {report['name']} ({report['character']}) | Kapitel: {report['chapter']} | Level: {report['level']}")
        print(f"Cash: ${report['cash']} | Wanted: {report['wanted_level']} | Reputation: {report['reputation']} | Vertrauen: {report['partner_trust']}%")
        print(f"Tage in Vice City: {report['days']} | Drachenbegegnungen: {report['dragon_encounters']}")
        print(f"Modifier: Mission={report['mission_modifier']} | Distrikt={report['district_condition']} | NG+ Zyklus={report['ng_plus_cycle']}")
        print(
            f"Run-Historie: Runs={self.run_history['runs_completed']} | Siege={self.run_history['victories']} | "
            f"Niederlagen={self.run_history['defeats']} | Peak Wanted={self.run_history['highest_wanted']} | "
            f"Peak Reputation={self.run_history['highest_reputation']}"
        )
        
        missions = report["completed_missions"] or ["Keine"]
        print(f"Abgeschlossene Missionen: {', '.join(missions)}")
        if report["branch_choices"]:
            print("Wichtige Entscheidungen:")
            for entry in report["branch_choices"]:
                print(f"- {entry['mission']} / {entry['phase']}: {entry['choice']}")
    
    def configure_replay_modifiers(self):
        print("\n[REPLAY] Missions-Modifier wählen:")
        print("1. standard (keine Änderungen)")
        print("2. clean_getaway (leichtere Flucht, bessere Rewards)")
        print("3. heat_wave (schwerer, aber mehr Rewards)")
        print("4. all_or_nothing (sehr schwer, maximale Rewards)")
        mission_choice = input("Wahl (1-4): ").strip()
        self.mission_modifier = {
            "1": "standard",
            "2": "clean_getaway",
            "3": "heat_wave",
            "4": "all_or_nothing"
        }.get(mission_choice, "standard")
        
        print("\n[REPLAY] Distrikt-Bedingungen wählen:")
        print("1. normal")
        print("2. crackdown")
        print("3. blackout")
        print("4. martial_law")
        district_choice = input("Wahl (1-4): ").strip()
        self.district_condition = {
            "1": "normal",
            "2": "crackdown",
            "3": "blackout",
            "4": "martial_law"
        }.get(district_choice, "normal")
    
    def start_new_game_plus(self):
        if not self.ng_plus_unlocked:
            print("New Game+ ist noch nicht freigeschaltet.")
            return False
        
        self.configure_replay_modifiers()
        self.new_game_plus_cycle += 1
        self.new_game_plus_active = True
        self.run_completed = False
        self.dragon_defeated = False
        self.endgame_report = {}
        self.branch_choices = []
        
        self.cash = 1000 + (self.new_game_plus_cycle * 250)
        self.level = 1 + self.new_game_plus_cycle
        self.stamina = self.level * 25
        self.days = 0
        self.wanted_level = 0
        self.reputation = 0
        self.partner_trust = 100
        self.dragon_encounters = 0
        self.chapter = 1
        self.inventory = self.inventory[:1]
        self.drug_effects = []
        self.story_flags["completed_missions"] = []
        self.story_flags["available_missions"] = []
        self.story_flags["first_mission_completed"] = False
        self.initialize_missions()
        
        print(f"\n[NG+] Zyklus {self.new_game_plus_cycle} gestartet! Viel Glück in Vice City.")
        return True
    
    def visit_mission_board(self):
        self.update_psychological_state(context="mission")
        self.apply_delayed_consequences()
        print("\n[MISSION] MISSION-BRETT")
        print("Verfügbare Missionen und Kontakte:")
        print(f"Aktuelles Partner-Vertrauen: {self.partner_trust}%")
        
        self.mission_manager.check_mission_unlocks(self)
        
        available_missions = self.mission_manager.get_available_missions(self)
        locked_by_trust = []
        for mission in self.mission_manager.all_missions.values():
            if mission.completed or mission.available:
                continue
            trust_locked = (
                mission.min_partner_trust is not None and self.partner_trust < mission.min_partner_trust
            ) or (
                mission.max_partner_trust is not None and self.partner_trust > mission.max_partner_trust
            )
            if trust_locked:
                locked_by_trust.append(mission)
        
        if not available_missions:
            print("Keine Missionen verfügbar. Erhöhe deine Reputation oder Level.")
            self.update_journal_state()
            return
        
        print("\n[MISSION] VERFÜGBARE MISSIONEN:")
        for i, mission in enumerate(available_missions):
            effective_difficulty = mission.get_effective_difficulty(self)
            print(f"{i+1}. {mission.name} (Kapitel {mission.chapter}, {'*' * effective_difficulty})")
            print(f"   Belohnung: ${mission.rewards.get('cash', 0)}, +{mission.rewards.get('reputation', 0)} Reputation")
        
        if locked_by_trust:
            print("\n[MISSION] Vertrauensabhängige Pfade (derzeit gesperrt):")
            for mission in locked_by_trust:
                print(f"- {mission.name}: {mission.locked_reason}")
        
        print(f"{len(available_missions)+1}. Zurück zum Hauptmenü")
        
        try:
            choice = int(input("Wähle eine Mission: ")) - 1
            mission = self.mission_board.select_mission(available_missions, choice)
            if mission:
                self.start_mission(mission)
            elif choice == len(available_missions):
                return
            else:
                print("Ungültige Wahl!")
        except ValueError:
            print("Ungültige Eingabe!")
    
    def start_mission(self, mission):
        if self.hallucination_intensity > 0.5 and random.random() < self.hallucination_intensity * 0.4:
            self.delayed_consequences.append(random.choice(["cash_loss", "trust_drop"]))
            print("Ein inneres Flüstern lenkt dich ab. Etwas fühlt sich falsch an.")
        if self.mission_manager.start_mission(mission, self):
            print(f"\n🎉 Mission '{mission.name}' erfolgreich abgeschlossen!")
        else:
            print(f"\n💥 Mission '{mission.name}' fehlgeschlagen oder abgebrochen.")
        self.update_journal_state()
    
    def initialize_missions(self):
        self.mission_manager = MissionManager()
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

        self.update_journal_state()
    
    def create_first_taste_mission(self):
        mission = Mission(
            "First Taste of Vice City",
            1,
            2,
            {"cash": 500, "reputation": 5, "partner_trust": 5},
            self.text_display,
            district_name="Ocean Beach"
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
                "rewards": {"partner_trust": 2},
                "decision_flag": "loyal_to_rico"
            },
            {
                "text": "Was ist der Haken?",
                "response": "Rico: Kein Haken. Nur ein einfacher Job für einen einfachen Start.",
                "consequences": {"partner_trust": -1},
                "decision_flag": "skeptical_of_rico"
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
        phase3.action_options = [
            {"name": "Ablenkung", "type": "distraction", "description": "Du löst einen Alarm am Nachbarhaus aus.", "bonus": 0.08, "risk": 0.35},
            {"name": "Silent Takedown", "type": "silent_takedown", "description": "Du schaltest den einzigen Zeugen lautlos aus.", "bonus": 0.12, "risk": 0.45},
            {"name": "Direkter Zugriff", "type": "direct_assault", "description": "Du gehst schnell und aggressiv vor.", "bonus": 0.05, "risk": 0.55}
        ]
        
        phase4 = MissionPhase(
            "Flucht",
            "escape",
            "Die Polizei ist auf dem Weg! Du musst schnell zur Garage in Ocean Beach kommen."
        )
        phase4.wanted_increase = 2
        phase4.escape_success_message = "Du erreichst Ricos Garage und verlierst die Verfolger!"
        phase4.escape_failure_message = "Die Polizei stellt dich! Du musst das Auto verlassen und zu Fuß fliehen."
        phase4.allow_escape_route_planning = True
        
        mission.phases = [phase1, phase2, phase3, phase4]
        self.mission_manager.register_mission(mission)
    
    def create_beach_party_mission(self):
        mission = Mission(
            "Beach Party Cleanup",
            1,
            3,
            {"cash": 800, "reputation": 8, "partner_trust": 3},
            self.text_display,
            district_name="Little Haiti"
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
        phase1.choices = [
            {
                "text": "Ich hole alles zurück und bringe dich sicher raus.",
                "response": "Maria: Danke. Genau deshalb vertraue ich dir.",
                "rewards": {"partner_trust": 6}
            },
            {
                "text": "Ich erledige den Job, aber dein Risiko ist nicht mein Problem.",
                "response": "Maria: Kalt. Aber ich habe keine Wahl.",
                "consequences": {"partner_trust": 5}
            }
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
        phase2.action_options = [
            {"name": "Ambush", "type": "ambush", "description": "Du lockst zwei Wachen in eine Sackgasse.", "bonus": 0.09, "risk": 0.40},
            {"name": "Ablenkung", "type": "distraction", "description": "Du erzeugst ein Party-Chaos als Deckung.", "bonus": 0.12, "risk": 0.45},
            {"name": "Silent Takedown", "type": "silent_takedown", "description": "Du neutralisierst einzelne Vipers lautlos.", "bonus": 0.11, "risk": 0.42}
        ]
        
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
        phase3.action_options = [
            {"name": "Ambush", "type": "ambush", "description": "Du attackierst aus der Deckung im richtigen Moment.", "bonus": 0.08, "risk": 0.45},
            {"name": "Direkter Angriff", "type": "direct_assault", "description": "Du zwingst die Vipers mit Gewalt zurück.", "bonus": 0.1, "risk": 0.5}
        ]
        
        phase4 = MissionPhase(
            "Polizeiflucht",
            "escape",
            "Die Polizei ist wegen des Kampfes auf der Party alarmiert worden!"
        )
        phase4.wanted_increase = 2
        phase4.escape_success_message = "Du verlierst die Polizei in den engen Gassen von Ocean Beach!"
        phase4.escape_failure_message = "Die Polizei stellt dich! Du landest kurzzeitig in Gewahrsam."
        phase4.allow_escape_route_planning = True
        
        mission.phases = [phase1, phase2, phase3, phase4]
        mission.blocked_flags = ["police_heat_high"]
        mission.available = False
        self.mission_manager.register_mission(mission)
        
        self.create_partner_loyalty_mission()
        self.create_broken_pact_mission()

    def create_partner_loyalty_mission(self):
        mission = Mission(
            "Ride or Die: Harbor Strike",
            2,
            4,
            {"cash": 1500, "reputation": 12, "partner_trust": 8},
            self.text_display
        )
        mission.min_partner_trust = 70
        mission.locked_reason = "Benötigt Partner-Vertrauen von mindestens 70."

        phase1 = MissionPhase(
            "Gemeinsamer Plan",
            "dialogue",
            "Dein Partner teilt Insider-Infos: Ein Schmugglerkonvoi fährt heute durch Viceport."
        )
        phase1.dialogue = [
            {"speaker": "Partner", "text": "Ich habe alles vorbereitet. Heute ziehen wir den Coup gemeinsam durch."},
            {"speaker": "Partner", "text": "Wenn du bei mir bleibst, kommen wir beide lebend raus."}
        ]
        phase1.choices = [
            {
                "text": "Wir ziehen das als Team durch.",
                "response": "Partner: Genau deshalb vertraue ich dir mein Leben an.",
                "rewards": {"partner_trust": 4}
            },
            {
                "text": "Ich nutze dich als Ablenkung und kassiere allein.",
                "response": "Partner: Was...? Du lässt mich einfach zurück?!",
                "consequences": {"partner_trust": 20, "wanted_level": 1},
                "partner_betrayal": True
            }
        ]

        phase2 = MissionPhase(
            "Konvoi-Hack",
            "action",
            "Du und dein Partner knacken die Konvoi-Sicherung in einem engen Zeitfenster."
        )
        phase2.stealth_check = True
        phase2.base_success_chance = 0.55
        phase2.success_message = "Synchroner Zugriff! Die Konvoi-Daten sind in eurer Hand."
        phase2.failure_message = "Die Sicherheitsdrohne erkennt euch. Das Team gerät in Panik."
        phase2.success_rewards = {"reputation": 4}
        phase2.failure_consequences = {"stamina": 10, "partner_trust": 8}

        phase3 = MissionPhase(
            "Exfiltration",
            "escape",
            "Schwer bewaffnete Einheiten riegeln das Viertel ab. Nur perfekte Abstimmung rettet euch."
        )
        phase3.wanted_increase = 2
        phase3.escape_success_message = "Ihr nutzt die Tunnelroute deines Partners und entkommt sauber."
        phase3.escape_failure_message = "Ihr verliert euch im Chaos und müsst alles fallen lassen."

        mission.phases = [phase1, phase2, phase3]
        mission.available = False
        self.mission_manager.register_mission(mission)

    def create_broken_pact_mission(self):
        mission = Mission(
            "Broken Pact",
            2,
            3,
            {"cash": 700, "reputation": 5},
            self.text_display
        )
        mission.max_partner_trust = 35
        mission.locked_reason = "Nur bei niedrigem Partner-Vertrauen verfügbar (35 oder weniger)."

        phase1 = MissionPhase(
            "Eskalation im Safehouse",
            "dialogue",
            "Ein Streit im Safehouse eskaliert: Dein Partner konfrontiert dich mit deinen Entscheidungen."
        )
        phase1.dialogue = [
            {"speaker": "Partner", "text": "Ich kann dir nicht mehr vertrauen. Zu viele Lügen, zu viele Leichen."},
            {"speaker": "Partner", "text": "Letzte Chance: Wahrheit oder Krieg."}
        ]
        phase1.choices = [
            {
                "text": "Ich entschuldige mich und gebe deinen Anteil.",
                "response": "Partner: ...Vielleicht gibt es noch Hoffnung.",
                "consequences": {"cash": 400},
                "rewards": {"partner_trust": 12}
            },
            {
                "text": "Ich drohe dir und nehme alles.",
                "response": "Partner: Dann endet es hier.",
                "consequences": {"partner_trust": 15},
                "partner_betrayal": True
            }
        ]

        phase2 = MissionPhase(
            "Nacht der Vergeltung",
            "action",
            "Die Situation kippt. Informanten, Sirenen und Verrat machen jeden Schritt gefährlich."
        )
        phase2.combat_check = True
        phase2.base_success_chance = 0.45
        phase2.success_message = "Du kommst durch, aber die Beziehung ist schwer beschädigt."
        phase2.failure_message = "Du tappst in den Hinterhalt deines Ex-Partners."
        phase2.failure_consequences = {"stamina": 15, "wanted_level": 2, "partner_trust": 10}

        mission.phases = [phase1, phase2]
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
    

    def update_journal_state(self):
        self.journal.sync_missions(self.mission_manager)
        self.journal.set_chapter(self.chapter)
        self.journal.set_relationship("Partner-Vertrauen", self.partner_trust)

    def open_journal(self):
        self.update_journal_state()
        self.journal.display(self.story_manager)

    def save_game(self, filename="data/saves/savegame.json"):
        self.update_journal_state()
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
            "stress_level": self.stress_level,
            "hallucination_intensity": self.hallucination_intensity,
            "delayed_consequences": self.delayed_consequences,
            "chapter": self.chapter,
            "partner_trust": self.partner_trust,
            "ankle_monitor": self.ankle_monitor,
            "combat_skill": self.combat_skill,
            "stealth": self.stealth,
            "dragon_defeated": getattr(self, 'dragon_defeated', False),
            "story_flags": self.story_flags,
            "clear_screen_enabled": self.text_display.clear_screen_enabled,
            "district_reputations": {
                name: district.reputation for name, district in self.district_manager.districts.items()
            }
        }
        
        try:
            self.persistence.save_protagonist(self, filename)
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
            self.stress_level = save_data.get("stress_level", 20)
            self.hallucination_intensity = save_data.get("hallucination_intensity", 0.0)
            self.delayed_consequences = save_data.get("delayed_consequences", [])
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
                "redemption_offered": False,
                "first_mission_completed": False,
                "decision_flags": {},
                "shown_consequence_events": []
            })
            self.journal = Journal.from_dict(save_data.get("journal", {}))
            self.text_display.clear_screen_enabled = save_data.get("clear_screen_enabled", False)
            district_reputations = save_data.get("district_reputations", {})
            for district_name, district in self.district_manager.districts.items():
                district.reputation = district_reputations.get(district_name, 0)
            
            return True
        except FileNotFoundError:
            print("Kein Speicherstand gefunden!")
            return False
        except Exception as e:
            print(f"Fehler beim Laden: {e}")
            return False
    
    def save_dragon(self, dragon, filename="data/dragon.json"):
        try:
            self.persistence.save_dragon(dragon, filename)
        except Exception as e:
            print(f"Fehler beim Speichern des Drachen: {e}")
    
    def load_dragon(self, filename="data/dragon.json"):
        try:
            return self.persistence.load_dragon(filename)
        except FileNotFoundError:
            return ViceCityDragon()
        except Exception as e:
            print(f"Fehler beim Laden des Drachen: {e}")
            return ViceCityDragon()
