import time
import random

from src.ui.text_display import TextDisplayManager
from src.effects.dragon_hallucination import DragonHallucination


class MissionPhase:
    def __init__(self, name, phase_type, description):
        self.name = name
        self.phase_type = phase_type
        self.description = description
        self.dialogue = []
        self.travel_dialogue = []
        self.choices = []
        self.base_success_chance = 0.5
        self.combat_check = False
        self.stealth_check = False
        self.stamina_cost = 5
        self.encounter_chance = 0.2
        self.success_message = "Aktion erfolgreich!"
        self.failure_message = "Aktion fehlgeschlagen!"
        self.escape_success_message = "Erfolgreich entkommen!"
        self.escape_failure_message = "Flucht gescheitert!"
        self.wanted_increase = 1
        self.success_rewards = {}
        self.failure_consequences = {}


class Mission:
    def __init__(self, name, chapter, difficulty, rewards, text_display_manager=None):
        self.name = name
        self.chapter = chapter
        self.difficulty = difficulty
        self.rewards = rewards
        self.text_display = text_display_manager or TextDisplayManager()
        self.phases = []
        self.completed = False
        self.failed_attempts = 0
        self.current_phase = 0
        self.available = False
        
    def is_available(self, protagonist):
        return (protagonist.chapter >= self.chapter and 
                not self.completed and 
                self.available)
    
    def start_mission(self, protagonist):
        self.current_phase = 0
        print(f"\n[MISSION] MISSION START: {self.name}")
        print(f"Schwierigkeit: {'⭐' * self.difficulty}")
        time.sleep(2)
        return self.execute_current_phase(protagonist)
    
    def execute_current_phase(self, protagonist):
        if self.current_phase >= len(self.phases):
            return self.complete_mission(protagonist)
        
        phase = self.phases[self.current_phase]
        print(f"\n--- PHASE {self.current_phase + 1}: {phase.name} ---")
        time.sleep(1)
        
        if phase.phase_type == "dialogue":
            return self.execute_dialogue_phase(phase, protagonist)
        elif phase.phase_type == "travel":
            return self.execute_travel_phase(phase, protagonist)
        elif phase.phase_type == "action":
            return self.execute_action_phase(phase, protagonist)
        elif phase.phase_type == "escape":
            return self.execute_escape_phase(phase, protagonist)
        
        return False
    
    def execute_dialogue_phase(self, phase, protagonist):
        self.text_display.display_mission_text(phase.description)
        for dialogue in phase.dialogue:
            self.text_display.display_dialogue(dialogue['speaker'], dialogue['text'])
        
        if phase.choices:
            return self.handle_phase_choices(phase, protagonist)
        else:
            self.current_phase += 1
            return self.execute_current_phase(protagonist)
    
    def execute_travel_phase(self, phase, protagonist):
        self.text_display.display_mission_text(phase.description)
        protagonist.stamina -= phase.stamina_cost or 5
        
        for dialogue in phase.travel_dialogue:
            self.text_display.display_dialogue(dialogue['speaker'], dialogue['text'])
        
        if phase.encounter_chance and random.random() < phase.encounter_chance:
            print("\n⚠️ Zufällige Begegnung während der Fahrt!")
            self.handle_travel_encounter(protagonist)
        
        self.current_phase += 1
        return self.execute_current_phase(protagonist)
    
    def execute_action_phase(self, phase, protagonist):
        self.text_display.display_mission_text(phase.description)
        
        success_chance = phase.base_success_chance
        success_chance += (protagonist.level * 0.05)
        success_chance += (protagonist.combat_skill * 0.02) if phase.combat_check else 0
        success_chance += (protagonist.stealth * 0.02) if phase.stealth_check else 0
        
        if random.random() < success_chance:
            print(f"\n[ERFOLG] {phase.success_message}")
            if phase.success_rewards:
                self.apply_rewards(phase.success_rewards, protagonist)
            self.current_phase += 1
            return self.execute_current_phase(protagonist)
        else:
            print(f"\n[FEHLGESCHLAGEN] {phase.failure_message}")
            if phase.failure_consequences:
                self.apply_consequences(phase.failure_consequences, protagonist)
            return self.handle_mission_failure(protagonist)
    
    def execute_escape_phase(self, phase, protagonist):
        self.text_display.display_mission_text(phase.description)
        protagonist.wanted_level = min(5, protagonist.wanted_level + phase.wanted_increase)
        
        escape_chance = 0.4 + (protagonist.stealth * 0.03) - (protagonist.wanted_level * 0.1)
        
        if random.random() < escape_chance:
            print(f"\n[ERFOLG] {phase.escape_success_message}")
            self.current_phase += 1
            return self.execute_current_phase(protagonist)
        else:
            print(f"\n[FEHLGESCHLAGEN] {phase.escape_failure_message}")
            return self.handle_mission_failure(protagonist)
    
    def handle_phase_choices(self, phase, protagonist):
        for i, choice in enumerate(phase.choices):
            print(f"{i+1}. {choice['text']}")
        
        try:
            player_choice = int(input("Wähle eine Option: ")) - 1
            if 0 <= player_choice < len(phase.choices):
                choice = phase.choices[player_choice]
                print(f"\n{choice['response']}")
                
                if choice.get('rewards'):
                    self.apply_rewards(choice['rewards'], protagonist)
                if choice.get('consequences'):
                    self.apply_consequences(choice['consequences'], protagonist)
                
                self.current_phase += 1
                return self.execute_current_phase(protagonist)
            else:
                print("Ungültige Wahl!")
                return self.handle_phase_choices(phase, protagonist)
        except ValueError:
            print("Ungültige Eingabe!")
            return self.handle_phase_choices(phase, protagonist)
    
    def handle_travel_encounter(self, protagonist):
        encounter_types = ["police_patrol", "rival_gang", "civilian_witness"]
        encounter = random.choice(encounter_types)
        
        if encounter == "police_patrol":
            print("Eine Polizeistreife hält dich an!")
            protagonist.wanted_level = min(5, protagonist.wanted_level + 1)
        elif encounter == "rival_gang":
            print("Rivalisierende Gangmitglieder erkennen dich!")
            protagonist.stamina -= 5
        else:
            print("Ein Zeuge sieht dich... aber sagt nichts.")
    
    def handle_mission_failure(self, protagonist):
        self.failed_attempts += 1
        print(f"\n💥 MISSION FEHLGESCHLAGEN (Versuch {self.failed_attempts})")
        
        protagonist.stamina = max(1, protagonist.stamina - 10)
        protagonist.wanted_level = min(5, protagonist.wanted_level + 1)
        
        if random.random() < 0.3:
            dragon = DragonHallucination()
            dragon.trigger_encounter("high_stress", protagonist)
            protagonist.dragon_encounters += 1
        
        retry_choice = input("Möchtest du die Mission wiederholen? (ja/nein): ")
        if retry_choice.lower() == "ja":
            self.current_phase = 0
            return False
        else:
            print("Mission abgebrochen.")
            return False
    
    def apply_rewards(self, rewards, protagonist):
        if rewards.get('cash'):
            protagonist.cash += rewards['cash']
            print(f"+${rewards['cash']} Cash")
        if rewards.get('reputation'):
            protagonist.reputation += rewards['reputation']
            print(f"+{rewards['reputation']} Reputation")
        if rewards.get('stamina'):
            protagonist.stamina = min(protagonist.level * 25, protagonist.stamina + rewards['stamina'])
            print(f"+{rewards['stamina']} Ausdauer")
        if rewards.get('partner_trust'):
            protagonist.partner_trust = min(100, protagonist.partner_trust + rewards['partner_trust'])
            print(f"+{rewards['partner_trust']} Partner-Vertrauen")
    
    def apply_consequences(self, consequences, protagonist):
        if consequences.get('cash'):
            protagonist.cash = max(0, protagonist.cash - consequences['cash'])
            print(f"-${consequences['cash']} Cash")
        if consequences.get('wanted_level'):
            protagonist.wanted_level = min(5, protagonist.wanted_level + consequences['wanted_level'])
            print(f"+{consequences['wanted_level']} Wanted Level")
        if consequences.get('stamina'):
            protagonist.stamina = max(1, protagonist.stamina - consequences['stamina'])
            print(f"-{consequences['stamina']} Ausdauer")
        if consequences.get('partner_trust'):
            protagonist.partner_trust = max(0, protagonist.partner_trust - consequences['partner_trust'])
            print(f"-{consequences['partner_trust']} Partner-Vertrauen")
    
    def complete_mission(self, protagonist):
        self.completed = True
        print(f"\n🎉 MISSION ABGESCHLOSSEN: {self.name}")
        print("Mission-Erfolge:")
        self.apply_rewards(self.rewards, protagonist)
        
        if "completed_missions" not in protagonist.story_flags:
            protagonist.story_flags["completed_missions"] = []
        protagonist.story_flags["completed_missions"].append(self.name)
        
        if self.name == "First Taste of Vice City":
            beach_party = protagonist.mission_manager.all_missions.get("Beach Party Cleanup")
            if beach_party:
                beach_party.available = True
                if "available_missions" not in protagonist.story_flags:
                    protagonist.story_flags["available_missions"] = []
                protagonist.story_flags["available_missions"].append("Beach Party Cleanup")
                print("\n🔓 NEUE MISSION FREIGESCHALTET: Beach Party Cleanup")
        
        protagonist.story_manager.check_chapter_progression(protagonist)
        
        if not protagonist.story_flags.get("first_mission_completed"):
            protagonist.story_flags["first_mission_completed"] = True
            protagonist.story_manager.trigger_story_event("first_crime", protagonist)
        
        return True
