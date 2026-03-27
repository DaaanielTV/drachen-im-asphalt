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
        self.action_options = []
        self.allow_escape_route_planning = False


class Mission:
    def __init__(self, name, chapter, difficulty, rewards, text_display_manager=None, district_name=None):
        self.name = name
        self.chapter = chapter
        self.difficulty = difficulty
        self.district_name = district_name
        self.rewards = rewards
        self.text_display = text_display_manager or TextDisplayManager()
        self.phases = []
        self.completed = False
        self.failed_attempts = 0
        self.current_phase = 0
        self.available = False
        self.required_flags_all = []
        self.required_flags_any = []
        self.blocked_flags = []
        
    def is_available(self, protagonist):
        district_reputation_ok = True
        if self.district_name:
            district_reputation_ok = protagonist.get_district_reputation(self.district_name) >= -20
        return (protagonist.chapter >= self.chapter and 
                not self.completed and 
                self.available and
                district_reputation_ok)

    def get_effective_difficulty(self, protagonist):
        if not self.district_name:
            return self.difficulty
        district_rep = protagonist.get_district_reputation(self.district_name)
        difficulty_modifier = 0
        if district_rep <= -40:
            difficulty_modifier = 2
        elif district_rep <= -20:
            difficulty_modifier = 1
        elif district_rep >= 40:
            difficulty_modifier = -1
        return max(1, self.difficulty + difficulty_modifier)
    
    def start_mission(self, protagonist):
        self.current_phase = 0
        effective_difficulty = self.get_effective_difficulty(protagonist)
        print(f"\n[MISSION] MISSION START: {self.name}")
        print(f"Schwierigkeit: {'⭐' * effective_difficulty}")
        time.sleep(2)
        return self.execute_current_phase(protagonist)
    
    def execute_current_phase(self, protagonist):
        if self.current_phase >= len(self.phases):
            return self.complete_mission(protagonist)
        
        if hasattr(protagonist, "update_psychological_state"):
            protagonist.update_psychological_state(context="mission_phase")
        
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
            dialogue_text = dialogue["text"]
            if hasattr(protagonist, "maybe_unreliable_dialogue"):
                dialogue_text = protagonist.maybe_unreliable_dialogue(dialogue["speaker"], dialogue_text)
            self.text_display.display_dialogue(dialogue['speaker'], dialogue_text)
        
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
        effective_difficulty = self.get_effective_difficulty(protagonist)
        success_chance += (protagonist.level * 0.05)
        success_chance += (protagonist.combat_skill * 0.02) if phase.combat_check else 0
        success_chance += (protagonist.stealth * 0.02) if phase.stealth_check else 0
        success_chance -= (effective_difficulty - 1) * 0.04
        
        if self.district_name:
            district_rep = protagonist.get_district_reputation(self.district_name)
            success_chance += district_rep * 0.001
        
        if random.random() < success_chance:
            print(f"\n[ERFOLG] {phase.success_message}")
            if phase.success_rewards:
                self.apply_rewards(phase.success_rewards, protagonist)
            if (
                hasattr(protagonist, "hallucination_intensity")
                and protagonist.hallucination_intensity > 0.65
                and random.random() < protagonist.hallucination_intensity * 0.4
            ):
                protagonist.delayed_consequences.append(random.choice(["cash_loss", "wanted_spike"]))
                print("Ein Detail entgeht dir im Adrenalinrausch. Die Folgen kommen später.")
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
        if self.district_name:
            district_rep = protagonist.get_district_reputation(self.district_name)
            escape_chance += district_rep * 0.001
        
        if random.random() < escape_chance:
            print(f"\n[ERFOLG] {phase.escape_success_message}")
            self.current_phase += 1
            return self.execute_current_phase(protagonist)
        else:
            print(f"\n[FEHLGESCHLAGEN] {phase.escape_failure_message}")
            return self.handle_mission_failure(protagonist)
    
    def handle_phase_choices(self, phase, protagonist):
        if hasattr(protagonist, "build_perceived_choices"):
            perceived_choices = protagonist.build_perceived_choices(phase.choices)
        else:
            perceived_choices = [{"kind": "real", "choice": choice} for choice in phase.choices]
        
        for i, choice_data in enumerate(perceived_choices):
            print(f"{i+1}. {choice_data['choice']['text']}")
        
        try:
            player_choice = int(input("Wähle eine Option: ")) - 1
            if 0 <= player_choice < len(perceived_choices):
                chosen_data = perceived_choices[player_choice]
                choice = chosen_data["choice"]
                print(f"\n{choice['response']}")
                
                if chosen_data["kind"] == "false":
                    if hasattr(protagonist, "delayed_consequences"):
                        protagonist.delayed_consequences.append("trust_drop")
                        print("Die Entscheidung war eine Halluzination. Dein Team reagiert irritiert.")
                    self.current_phase += 1
                    return self.execute_current_phase(protagonist)
                
                if choice.get('rewards'):
                    self.apply_rewards(choice['rewards'], protagonist)
                if choice.get('consequences'):
                    self.apply_consequences(choice['consequences'], protagonist)

                if hasattr(protagonist, "journal"):
                    protagonist.journal.record_choice(choice.get('text', ''), choice.get('response', ''))
                    protagonist.update_journal_state()

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
            intensity = getattr(protagonist, "hallucination_intensity", 0.0)
            dragon.trigger_encounter("high_stress", protagonist, intensity)
        
        retry_choice = input("Möchtest du die Mission wiederholen? (ja/nein): ")
        if retry_choice.lower() == "ja":
            self.current_phase = 0
            return False
        else:
            print("Mission abgebrochen.")
            return False
    
    def apply_rewards(self, rewards, protagonist):
        reward_multiplier = getattr(protagonist, "get_reward_multiplier", lambda: 1.0)()
        
        if rewards.get('cash'):
            cash_reward = int(rewards['cash'] * reward_multiplier)
            protagonist.cash += cash_reward
            print(f"+${cash_reward} Cash")
        if rewards.get('reputation'):
            reputation_reward = max(1, int(rewards['reputation'] * reward_multiplier))
            protagonist.reputation += reputation_reward
            print(f"+{reputation_reward} Reputation")
        if rewards.get('stamina'):
            protagonist.stamina = min(protagonist.level * 25, protagonist.stamina + rewards['stamina'])
            print(f"+{rewards['stamina']} Ausdauer")
        if rewards.get('partner_trust'):
            protagonist.partner_trust = min(100, protagonist.partner_trust + rewards['partner_trust'])
            print(f"+{rewards['partner_trust']} Partner-Vertrauen")

        if hasattr(protagonist, "journal"):
            protagonist.update_journal_state()
    
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

        if hasattr(protagonist, "journal"):
            protagonist.update_journal_state()
    
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
        
        if self.name in ("Beach Party Cleanup", "First Taste of Vice City", "Broken Pact", "Ride or Die: Harbor Strike"):
            loyalty_mission = protagonist.mission_manager.all_missions.get("Ride or Die: Harbor Strike")
            broken_mission = protagonist.mission_manager.all_missions.get("Broken Pact")
            if loyalty_mission and protagonist.partner_trust >= 70 and not loyalty_mission.completed:
                loyalty_mission.available = True
                print("\n🔓 VERTRAUENS-PFAD FREIGESCHALTET: Ride or Die: Harbor Strike")
            if broken_mission and protagonist.partner_trust <= 35 and not broken_mission.completed:
                broken_mission.available = True
                print("\n🔓 MISSTRAUENS-PFAD FREIGESCHALTET: Broken Pact")
        
        protagonist.story_manager.check_chapter_progression(protagonist)
        
        if not protagonist.story_flags.get("first_mission_completed"):
            protagonist.story_flags["first_mission_completed"] = True
            protagonist.story_manager.trigger_story_event("first_crime", protagonist)
        
        if hasattr(protagonist, "journal"):
            protagonist.update_journal_state()

        return True
