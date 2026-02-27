import json
import os
import random
import time
import re
import sys

# GTA 6: Vice City Dragons - Text Adventure
# Ein kriminelles Abenteuer inspiriert von GTA 6 mit Jason und Lucia in Vice City
# Der Drache erscheint als Metapher für die Konsequenzen oder durch Drogeneinflüsse

class TextDisplayManager:
    def __init__(self):
        self.display_mode = "progressive"  # "instant", "progressive", "typewriter"
        self.chunk_size = 80  # Maximum characters per line
        self.prompt_text = "[Leertaste zum Fortfahren]"
        self.skip_enabled = True
        self.clear_screen_enabled = False  # New feature: clear screen between chunks
        
    def split_text_into_chunks(self, text):
        """Split text into manageable chunks for progressive display"""
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Handle empty text
        if not text:
            return []
        
        # Split by paragraphs first (double newlines)
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # Split paragraph into sentences
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            
            current_chunk = ""
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                # If adding this sentence would exceed chunk size, start new chunk
                if len(current_chunk + sentence) > self.chunk_size and current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    current_chunk += (" " if current_chunk else "") + sentence
            
            # Add remaining text from paragraph
            if current_chunk:
                chunks.append(current_chunk.strip())
        
        return chunks
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def add_white_space(self):
        """Add 100-200 rows of white space"""
        white_lines = random.randint(100, 200)
        
        # Add white space
        for _ in range(white_lines):
            print()
        return True  # Normal continuation
    
    def display_progressive(self, text, force_instant=False):
        """Display text progressively with white space between chunks"""
        if self.display_mode == "instant" or force_instant:
            print(text)
            return
        
        chunks = self.split_text_into_chunks(text)
        
        for i, chunk in enumerate(chunks):
            # Clear screen before displaying new chunk (except first chunk) if enabled
            if i > 0 and self.clear_screen_enabled:
                self.clear_screen()
                print(f"[Bildschirm gelöscht - Zeige nächsten Textabschnitt]\n")
            
            print(chunk)
            
            # Don't add white space after the last chunk
            if i < len(chunks) - 1:
                # Add white space between chunks
                self.add_white_space()
    
    def display_story_event(self, event_text):
        """Display story events with special formatting"""
        print("\n[STORY] GESCHICHTEN-MOMENT:")
        self.display_progressive(event_text)
        print()
    
    def display_dialogue(self, speaker, text):
        """Display character dialogue"""
        print(f"\n{speaker}:")
        self.display_progressive(text)
    
    def display_mission_text(self, text):
        """Display mission-related text"""
        print("\n[MISSION]")
        self.display_progressive(text)
    
    def display_dragon_text(self, text):
        """Display dragon-related text with special formatting"""
        print(f"\n {text}")
    
    def set_display_mode(self, mode):
        """Set the display mode ('instant', 'progressive', 'typewriter')"""
        if mode in ["instant", "progressive", "typewriter"]:
            self.display_mode = mode
    
    def toggle_clear_screen(self):
        """Toggle screen clearing between chunks"""
        self.clear_screen_enabled = not self.clear_screen_enabled
        status = "aktiviert" if self.clear_screen_enabled else "deaktiviert"
        print(f"Bildschirm-Löschung zwischen Textabschnitten {status}.")
        return self.clear_screen_enabled

class DrugEffect:
    def __init__(self, name, intensity, duration):
        self.name = name
        self.intensity = intensity  # 0.1 bis 1.0
        self.duration = duration    # in Runden
        self.remaining = duration
    
    def apply_effect(self, protagonist):
        if self.remaining > 0:
            # Auslösen von Drachen-Halluzinationen bei hoher Intensität
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

class Location:
    def __init__(self, name, description, danger_level, opportunities):
        self.name = name
        self.description = description
        self.danger_level = danger_level  # 1-10
        self.opportunities = opportunities  # Liste von möglichen Aktivitäten
    
    def describe(self):
        print(f"\n[ORT] {self.name}")
        print(f"{self.description}")
        print(f"Gefahrenlevel: {'*' * self.danger_level}")

class DragonHallucination:
    def __init__(self):
        self.encounters = [
            {
                "trigger": "high_stress",
                "description": "Der Druck wird zu groß. Ein Drache der Konsequenzen erhebt sich vor dir.",
                "effect": "paranoia"
            },
            {
                "trigger": "drug_use", 
                "description": "Die Drogen wirken. Drachenschatten umtanzen dich im Neonlicht.",
                "effect": "hallucination"
            },
            {
                "trigger": "betrayal",
                "description": "Der Verrat nagt an dir. Ein Drache des Misstrauens flüstert in deinem Kopf.",
                "effect": "distrust"
            }
        ]
    
    def trigger_encounter(self, trigger_type, protagonist):
        encounter = random.choice([e for e in self.encounters if e["trigger"] == trigger_type])
        if encounter:
            print(f"\n[DRACHE] {encounter['description']}")
            self.apply_effect(encounter['effect'], protagonist)
            return True
        return False
    
    def apply_effect(self, effect_type, protagonist):
        if effect_type == "paranoia":
            protagonist.stamina = max(1, protagonist.stamina - 10)
            print("Dein Stresslevel steigt. Ausdauer verringert.")
        elif effect_type == "hallucination":
            protagonist.cash = max(0, protagonist.cash - random.randint(50, 200))
            print("In der Verwirrung verlierst du Geld.")
        elif effect_type == "distrust":
            if hasattr(protagonist, 'partner_trust'):
                protagonist.partner_trust = max(0, protagonist.partner_trust - 10)
                print("Das Vertrauen zu deinem Partner schwindet.")

class Weapon:
    def __init__(self, name, cost, damage_increase, illegal_status):
        self.name = name
        self.cost = cost
        self.damage_increase = damage_increase
        self.illegal_status = illegal_status  # 1-5 (5 = hochgradig illegal)

class StoryManager:
    def __init__(self, text_display_manager=None):
        self.text_display = text_display_manager or TextDisplayManager()
        self.chapters = {
            1: {
                "title": "Ankunft in Vice City",
                "opening": "Die Neonlichter von Vice City empfangen dich wie ein verlockendes Versprechen. Die Stadt der Möglichkeiten - oder des Untergangs.",
                "motivation": {
                    "jason": "Deine militärische Vergangenheit liegt hinter dir, aber die Schatten der Kriegserlebnisse verfolgen dich. Vice City ist deine Chance auf einen Neuanfang.",
                    "lucia": "Die Fußfessel an deinem Knöchel erinnert dich an die frische Vergangenheit. Vice City bietet dir die Freiheit, die du so sehr begehrst."
                }
            },
            2: {
                "title": "Kleine Fische im großen Teich",
                "opening": "Die ersten Schritte in der Unterwelt von Vice City. Jede kleine Tat bringt dich näher an die großen Fische - oder an die Haken des Gesetzes.",
                "theme": "Erfahrung sammeln und Grenzen austesten"
            },
            3: {
                "title": "Aufstieg durch die Ränge",
                "opening": "Dein Name beginnt, in den dunklen Ecken von Vice City Respekt zu erzeugen. Aber mit jedem Erfolg wächst auch die Gefahr.",
                "theme": "Ambition trifft auf Konsequenzen"
            },
            4: {
                "title": "Der Punkt ohne Wiederkehr",
                "opening": "Die Linie zwischen Krimineller und Monster verschwimmt. Jede Entscheidung zieht dunklere Schatten nach sich.",
                "theme": "Moralische Zerreißproben"
            },
            5: {
                "title": "Die Konsequenzen entfesseln",
                "opening": "Der Höhepunkt deiner kriminellen Karriere - aber der Preis ist deine Seele. Die Drachen werden unübersehbar.",
                "theme": "Psychologischer Zusammenbruch"
            },
            6: {
                "title": "Der Drache der Konsequenzen",
                "opening": "Der Moment der Wahrheit ist gekommen. Alle deine Taten, alle deine Entscheidungen führen zu diesem einen Kampf.",
                "theme": "Endgültige Konfrontation"
            }
        }
        
        self.story_events = {
            "first_crime": "Dein erstes Verbrechen in Vice City. Das Adrenalin pulsiert durch deine Adern, aber ein Schatten in Form eines Drachen huscht über die Wand.",
            "first_dragon": "Zum ersten Mal siehst du ihn klar - ein Drache aus Neonlicht und Schatten. Er ist real, oder? Die Konsequenzen deiner Taten nehmen Form an.",
            "partner_trust_low": "Das Misstrauen zwischen euch wächst. In den Neonlichtern siehst du Drachenaugen, die dich verurteilen.",
            "high_wanted": "Dein Gesicht ist überall. Die Stadt wird zu einem Käfig, und die Drachen lauern an jeder Ecke.",
            "drug_overdose": "Die Drogen wirken stärker als erwartet. Die Drachen tanzen um dich herum und flüstern von deinen Fehlern.",
            "betrayal": "Verrat schmerzt mehr als jede Kugel. Ein Drache des Misstrauens erhebt sich in deinem Herzen.",
            "redemption_chance": "Es gibt noch einen Weg zurück. Ein Lichtstrahl durch die Drachenschatten - die Chance auf Erlösung."
        }
    
    def get_chapter_story(self, chapter):
        return self.chapters.get(chapter, self.chapters[1])
    
    def trigger_story_event(self, event_type, protagonist):
        if event_type in self.story_events:
            self.text_display.display_story_event(self.story_events[event_type])
            return True
        return False
    
    def check_chapter_progression(self, protagonist):
        # Kapitel-Fortschritt basierend auf Level und Erfahrung
        new_chapter = min(6, 1 + protagonist.level // 3)
        if new_chapter > protagonist.chapter:
            protagonist.chapter = new_chapter
            chapter_info = self.get_chapter_story(new_chapter)
            print(f"\n[STORY] KAPITEL {new_chapter}: {chapter_info['title']}")
            self.text_display.display_progressive(chapter_info['opening'])
            if 'theme' in chapter_info:
                print(f"Thema: {chapter_info['theme']}")
            return True
        return False

class Mission:
    def __init__(self, name, chapter, difficulty, rewards, text_display_manager=None):
        self.name = name
        self.chapter = chapter  # Required chapter level
        self.difficulty = difficulty  # 1-10
        self.rewards = rewards  # {"cash": int, "reputation": int, "items": list}
        self.text_display = text_display_manager or TextDisplayManager()
        self.phases = []  # List of MissionPhase objects
        self.completed = False
        self.failed_attempts = 0
        self.current_phase = 0
        self.available = False
        
    def is_available(self, protagonist):
        """Check if mission is available based on protagonist's chapter and reputation"""
        return (protagonist.chapter >= self.chapter and 
                not self.completed and 
                self.available)
    
    def start_mission(self, protagonist):
        """Start the mission from phase 1"""
        self.current_phase = 0
        print(f"\n[MISSION] MISSION START: {self.name}")
        print(f"Schwierigkeit: {'⭐' * self.difficulty}")
        time.sleep(2)
        return self.execute_current_phase(protagonist)
    
    def execute_current_phase(self, protagonist):
        """Execute the current mission phase"""
        if self.current_phase >= len(self.phases):
            return self.complete_mission(protagonist)
        
        phase = self.phases[self.current_phase]
        print(f"\n--- PHASE {self.current_phase + 1}: {phase.name} ---")
        time.sleep(1)
        
        # Execute phase based on type
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
        """Execute dialogue phase with character interactions"""
        self.text_display.display_mission_text(phase.description)
        for dialogue in phase.dialogue:
            self.text_display.display_dialogue(dialogue['speaker'], dialogue['text'])
        
        if phase.choices:
            return self.handle_phase_choices(phase, protagonist)
        else:
            self.current_phase += 1
            return self.execute_current_phase(protagonist)
    
    def execute_travel_phase(self, phase, protagonist):
        """Execute travel phase with dialogue during movement"""
        self.text_display.display_mission_text(phase.description)
        protagonist.stamina -= phase.stamina_cost or 5
        
        # Travel dialogue
        for dialogue in phase.travel_dialogue:
            self.text_display.display_dialogue(dialogue['speaker'], dialogue['text'])
        
        # Random encounter during travel
        if phase.encounter_chance and random.random() < phase.encounter_chance:
            print("\n⚠️ Zufällige Begegnung während der Fahrt!")
            self.handle_travel_encounter(protagonist)
        
        self.current_phase += 1
        return self.execute_current_phase(protagonist)
    
    def execute_action_phase(self, phase, protagonist):
        """Execute action phase with skill checks"""
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
        """Execute escape/chase phase"""
        self.text_display.display_mission_text(phase.description)
        protagonist.wanted_level = min(5, protagonist.wanted_level + phase.wanted_increase)
        
        # Chase mechanics
        escape_chance = 0.4 + (protagonist.stealth * 0.03) - (protagonist.wanted_level * 0.1)
        
        if random.random() < escape_chance:
            print(f"\n[ERFOLG] {phase.escape_success_message}")
            self.current_phase += 1
            return self.execute_current_phase(protagonist)
        else:
            print(f"\n[FEHLGESCHLAGEN] {phase.escape_failure_message}")
            return self.handle_mission_failure(protagonist)
    
    def handle_phase_choices(self, phase, protagonist):
        """Handle player choices in dialogue phases"""
        for i, choice in enumerate(phase.choices):
            print(f"{i+1}. {choice['text']}")
        
        try:
            player_choice = int(input("Wähle eine Option: ")) - 1
            if 0 <= player_choice < len(phase.choices):
                choice = phase.choices[player_choice]
                print(f"\n{choice['response']}")
                
                # Apply choice consequences
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
        """Handle random encounters during travel phases"""
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
        """Handle mission failure scenarios"""
        self.failed_attempts += 1
        print(f"\n💥 MISSION FEHLGESCHLAGEN (Versuch {self.failed_attempts})")
        
        # Apply failure penalties
        protagonist.stamina = max(1, protagonist.stamina - 10)
        protagonist.wanted_level = min(5, protagonist.wanted_level + 1)
        
        # Chance for dragon hallucination after failure
        if random.random() < 0.3:
            dragon = DragonHallucination()
            dragon.trigger_encounter("high_stress", protagonist)
            protagonist.dragon_encounters += 1
        
        # Allow retry or abandon
        retry_choice = input("Möchtest du die Mission wiederholen? (ja/nein): ")
        if retry_choice.lower() == "ja":
            self.current_phase = 0  # Reset to beginning
            return False  # Mission not completed
        else:
            print("Mission abgebrochen.")
            return False
    
    def apply_rewards(self, rewards, protagonist):
        """Apply mission rewards to protagonist"""
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
        """Apply mission consequences to protagonist"""
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
        """Complete the mission and apply rewards"""
        self.completed = True
        print(f"\n🎉 MISSION ABGESCHLOSSEN: {self.name}")
        print("Mission-Erfolge:")
        self.apply_rewards(self.rewards, protagonist)
        
        # Update story flags with mission completion
        if "completed_missions" not in protagonist.story_flags:
            protagonist.story_flags["completed_missions"] = []
        protagonist.story_flags["completed_missions"].append(self.name)
        
        # Unlock next missions
        if self.name == "First Taste of Vice City":
            beach_party = protagonist.mission_manager.all_missions.get("Beach Party Cleanup")
            if beach_party:
                beach_party.available = True
                if "available_missions" not in protagonist.story_flags:
                    protagonist.story_flags["available_missions"] = []
                protagonist.story_flags["available_missions"].append("Beach Party Cleanup")
                print("\n🔓 NEUE MISSION FREIGESCHALTET: Beach Party Cleanup")
        
        # Check for chapter progression
        protagonist.story_manager.check_chapter_progression(protagonist)
        
        # Story event for mission completion
        if not protagonist.story_flags.get("first_mission_completed"):
            protagonist.story_flags["first_mission_completed"] = True
            protagonist.story_manager.trigger_story_event("first_crime", protagonist)
        
        return True

class MissionPhase:
    def __init__(self, name, phase_type, description):
        self.name = name
        self.phase_type = phase_type  # "dialogue", "travel", "action", "escape"
        self.description = description
        self.dialogue = []  # List of {"speaker": str, "text": str}
        self.travel_dialogue = []  # Dialogue during travel
        self.choices = []  # Player choices
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

class ViceCityDragon:
    def __init__(self):
        self.name = "Der Drache der Konsequenzen"
        self.stamina = 150
        self.level = 15
        self.defeated = False
        self.manifestation = "metaphorisch"  # Kann sich ändern
        self.story_lines = [
            "Ich bin die Summe all deiner schlechten Entscheidungen.",
            "Jedes Verbrechen hat mich stärker gemacht.",
            "Du kannst nicht vor dir selbst fliehen.",
            "Die Neonlichter von Vice City sind meine Schuppen.",
            "Dein Partnervertrauen? Ich habe es gefressen.",
            "Die Fußfessel ist nur der Anfang deiner Ketten.",
            "Ich bin der Grund, warum du nachts nicht schlafen kannst."
        ]
    
    def attack_protagonist(self, protagonist):
        damage = random.randint(15, 30)
        protagonist.stamina -= damage
        print(f"Der Drache der Konsequenzen greift an! Du verlierst {damage} Ausdauer.")
        
        # Story-Text vom Drachen
        dragon_line = random.choice(self.story_lines)
        print(f"[DRACHE] '{dragon_line}'")
        print(f"Deine Schuld und deine schlechten Entscheidungen wiegen schwer...")
        
        # Chance auf zusätzliche mentale Schäden
        if random.random() < 0.3:
            protagonist.partner_trust = max(0, protagonist.partner_trust - 5)
            print("Dein Vertrauen zu deinem Partner schwindet unter der Last der Konsequenzen.")

class MissionGiver:
    def __init__(self, name, location, personality, description):
        self.name = name
        self.location = location
        self.personality = personality  # "professional", "crazy", "desperate", "mysterious"
        self.description = description
        self.available_missions = []
        self.relationship_level = 0  # 0-100
        self.met_before = False
        
    def introduce(self, protagonist):
        """Introduce the mission giver"""
        if not self.met_before:
            print(f"\n[KONTAKT] NEUER KONTAKT: {self.name}")
            print(f"Ort: {self.location}")
            print(f"Beschreibung: {self.description}")
            self.met_before = True
        else:
            print(f"\n[KONTAKT] KONTAKT: {self.name}")
            
    def offer_mission(self, mission, protagonist):
        """Offer a mission to the protagonist"""
        if mission.is_available(protagonist):
            print(f"\n[MISSION] MISSION-ANGEBOT: {mission.name}")
            print(f"Schwierigkeit: {'*' * mission.difficulty}")
            print(f"Belohnung: ${mission.rewards.get('cash', 0)}, +{mission.rewards.get('reputation', 0)} Reputation")
            
            accept = input("Möchtest du diese Mission annehmen? (ja/nein): ")
            if accept.lower() == "ja":
                return True
        else:
            print(f"\n[UNVERFÜGBAR] Mission '{mission.name}' ist noch nicht verfügbar.")
            if protagonist.chapter < mission.chapter:
                print(f"Benötigt Kapitel {mission.chapter} (Du bist in Kapitel {protagonist.chapter})")
        return False
    
    def update_relationship(self, change):
        """Update relationship level with protagonist"""
        self.relationship_level = max(0, min(100, self.relationship_level + change))

class MissionManager:
    def __init__(self):
        self.mission_givers = {}
        self.all_missions = {}
        self.active_missions = []
        self.completed_missions = []
        
    def register_mission_giver(self, giver):
        """Register a mission giver"""
        self.mission_givers[giver.name] = giver
        
    def register_mission(self, mission):
        """Register a mission"""
        self.all_missions[mission.name] = mission
        
    def get_available_missions(self, protagonist):
        """Get list of available missions for protagonist"""
        available = []
        for mission in self.all_missions.values():
            if mission.is_available(protagonist) and mission not in self.active_missions:
                available.append(mission)
        return available
    
    def start_mission(self, mission, protagonist):
        """Start a mission"""
        if mission.start_mission(protagonist):
            self.active_missions.append(mission)
            self.completed_missions.append(mission)
            return True
        return False
    
    def check_mission_unlocks(self, protagonist):
        """Check and unlock new missions based on protagonist progress"""
        for mission in self.all_missions.values():
            if not mission.available and mission.is_available(protagonist):
                mission.available = True
                print(f"\n🔓 NEUE MISSION VERFÜGBAR: {mission.name}")

class District:
    def __init__(self, name, description, danger_level, opportunities, special_feature=None):
        self.name = name
        self.description = description
        self.danger_level = danger_level  # 1-10
        self.opportunities = opportunities  # Liste von möglichen Aktivitäten
        self.special_feature = special_feature  # District-specific feature
        self.reputation = 0  # District-specific reputation
        self.control_level = 0  # Player's control/influence in district
        self.discovered_features = []  # Unlocked special features
        
    def describe(self):
        print(f"\n{self.name}")
        print(f"{self.description}")
        print(f"Gefahrenlevel: {'*' * self.danger_level}")
        print(f"Dein Ruf: {self.reputation} | Einfluss: {self.control_level}%")
        if self.special_feature and self.special_feature in self.discovered_features:
            print(f"Spezial-Feature: {self.get_special_feature_description()}")
    
    def get_special_feature_description(self):
        features = {
            "tourism_season": "Tourismus-Saison System",
            "motel_network": "Motel-Netzwerk",
            "surveillance": "Überwachungs-System",
            "container_management": "Container-Management",
            "corporate_crime": "Unternehmenskriminalität",
            "territory_control": "Gebiets-Kontrolle",
            "social_climbing": "Gesellschaftlicher Aufstieg",
            "swamp_base": "Sumpf-Basis",
            "island_smuggling": "Insel-Schmuggel"
        }
        return features.get(self.special_feature, "Unbekanntes Feature")
    
    def unlock_feature(self):
        if self.special_feature and self.special_feature not in self.discovered_features:
            self.discovered_features.append(self.special_feature)
            return True
        return False

class DistrictManager:
    def __init__(self, protagonist):
        self.protagonist = protagonist
        self.districts = {}
        self.seasonal_events = {}
        self.initialize_districts()
        
    def initialize_districts(self):
        self.districts = {
            "Ocean Beach": District(
                "Ocean Beach",
                "Strände, Neonlichter und Touristenfallen. Perfekt für kleine Diebstähle.",
                3,
                ["taschendiebstahl", "touristen_abzocken"],
                "tourism_season"
            ),
            "Washington Beach": District(
                "Washington Beach",
                "Mittelmäßige Strände und heruntergekommene Motels. Ein Ort, an dem Touristen seltener werden und die Kriminalität zunimmt.",
                4,
                ["motel_raids", "beach_vendor_extortion", "tourist_scamming"],
                "motel_network"
            ),
            "Vice Point": District(
                "Vice Point",
                "Wohngegend mit reichen Bewohnern. Gute Gelegenheiten für Einbrüche.",
                5,
                ["einbruch", "autodiebstahl"],
                "surveillance"
            ),
            "Viceport": District(
                "Viceport",
                "Container-Terminals und Lagerhäuser dominieren die Skyline. Hier laufen die illegalen Importe der Stadt zusammen.",
                6,
                ["container_smuggling", "dockyard_heists", "shipping_theft"],
                "container_management"
            ),
            "Downtown": District(
                "Downtown",
                "Geschäftsviertel mit Banken und Bürogebäuden. Risiko, aber hohe Gewinne.",
                7,
                ["überfall", "erpressung"],
                "corporate_crime"
            ),
            "Little Haiti": District(
                "Little Haiti",
                "Gebiet mit starkem Gang-Einfluss. Gefährlich aber lohnend.",
                8,
                ["gang_kämpfe", "drogen_deals"],
                "territory_control"
            ),
            "Starfish Island": District(
                "Starfish Island",
                "Luxusvillen und gepflegte Gärten verbergen dunkle Geheimnisse. Nur die Reichsten und Gefährlichsten leben hier.",
                7,
                ["mansion_burglary", "extortion_rackets", "high_society_crimes"],
                "social_climbing"
            ),
            "Everglades": District(
                "Everglades",
                "Sumpfgebiet außerhalb der Stadt. Treffpunkt für illegale Geschäfte.",
                9,
                ["schmuggel", "drogen_labore"],
                "swamp_base"
            ),
            "Vice Keys": District(
                "Vice Keys",
                "Inseln vor der Küste. Abgeschieden und ideal für verbotene Aktivitäten.",
                6,
                ["schwarzmarkt", "people_smuggling"],
                "island_smuggling"
            )
        }
        
        # Initialize seasonal events for Ocean Beach
        self.seasonal_events = {
            "high_season": {
                "name": "Hauptsaison",
                "tourist_multiplier": 2.0,
                "police_multiplier": 1.5,
                "rewards_bonus": 1.3
            },
            "low_season": {
                "name": "Nebensaison", 
                "tourist_multiplier": 0.5,
                "police_multiplier": 0.8,
                "rewards_bonus": 0.7
            },
            "normal_season": {
                "name": "Normalsaison",
                "tourist_multiplier": 1.0,
                "police_multiplier": 1.0,
                "rewards_bonus": 1.0
            }
        }
        
        # Set current season
        self.current_season = "normal_season"
        self.season_day_counter = 0
    
    def get_district(self, name):
        return self.districts.get(name)
    
    def update_season(self):
        self.season_day_counter += 1
        if self.season_day_counter >= 7:  # Change season every week
            self.season_day_counter = 0
            seasons = list(self.seasonal_events.keys())
            current_index = seasons.index(self.current_season)
            self.current_season = seasons[(current_index + 1) % len(seasons)]
            print(f"\n[SEASON] SAISONWECHSEL: {self.seasonal_events[self.current_season]['name']} in Ocean Beach!")
    
    def check_feature_unlock(self, district_name):
        district = self.get_district(district_name)
        if district and district.special_feature:
            # Features unlock based on player level and reputation
            unlock_requirements = {
                "tourism_season": {"level": 1, "reputation": 0},
                "motel_network": {"level": 2, "reputation": 10},
                "surveillance": {"level": 3, "reputation": 20},
                "container_management": {"level": 4, "reputation": 30},
                "corporate_crime": {"level": 5, "reputation": 40},
                "territory_control": {"level": 6, "reputation": 50},
                "social_climbing": {"level": 7, "reputation": 60},
                "swamp_base": {"level": 8, "reputation": 70},
                "island_smuggling": {"level": 9, "reputation": 80}
            }
            
            requirements = unlock_requirements.get(district.special_feature, {"level": 1, "reputation": 0})
            
            if (self.protagonist.level >= requirements["level"] and 
                self.protagonist.reputation >= requirements["reputation"] and
                district.special_feature not in district.discovered_features):
                
                if district.unlock_feature():
                    print(f"\n[UNLOCK] NEUES FEATURE FREIGESCHALTET: {district.get_special_feature_description()} in {district_name}!")
                    return True
        return False

class Protagonist:
    def __init__(self, name, character_type):
        self.name = name
        self.character_type = character_type  # "jason" oder "lucia"
        self.cash = 500  # Startgeld für kleine Verbrechen
        self.level = 1
        self.inventory = []
        self.stamina = 30
        self.days = 0
        self.wanted_level = 0
        self.reputation = 0
        self.drug_effects = []
        self.dragon_encounters = 0
        self.chapter = 1
        self.partner_trust = 100  # Vertrauen zum Partner
        self.ankle_monitor = character_type == "lucia"  # Lucia startet mit Fußfessel
        
        # Create TextDisplayManager and share it with other managers
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
        
        # Charakter-spezifische Attribute
        if character_type == "jason":
            self.combat_skill = 15  # Militärerfahrung
            self.stealth = 10
        else:  # lucia
            self.combat_skill = 10
            self.stealth = 15  # Gefängniserfahrung
    
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
        # Wird später implementiert für Charakter-Wechsel
        pass
    
    def rest(self, location="sicherer Unterschlupf"):
        print(f"\n[RUHEN] Du ruhst dich in {location} aus...")
        self.days += 1
        self.stamina = self.level * 25
        self.wanted_level = max(0, self.wanted_level - 1)
        
        # Drogeneffekte abklingen lassen
        self.drug_effects = [effect for effect in self.drug_effects if effect.remaining > 0]
        
        # Chance auf Drachen-Halluzination während der Ruhe
        if self.dragon_encounters > 0 and random.random() < 0.3:
            dragon = DragonHallucination()
            dragon.trigger_encounter("high_stress", self)
            
        print(f"Ausdauer wiederhergestellt: {self.stamina}")
        if self.wanted_level > 0:
            print(f"Wanted Level gesunken: {self.wanted_level}")
    
    def explore_vice_city(self):
        # Update seasons and check for feature unlocks
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
                # Check for feature unlock
                self.district_manager.check_feature_unlock(district.name)
                self.explore_district(district)
            else:
                print("Ungültige Wahl!")
        except ValueError:
            print("Ungültige Eingabe!")
    
    def explore_district(self, district):
        district.describe()
        
        # Check for special district features
        if district.special_feature in district.discovered_features:
            self.handle_district_feature(district)
            return
        
        # Fußfessel kann Aktivitäten einschränken
        if self.ankle_monitor and random.random() < 0.3:
            print("\n[FUSSFESSEL] Deine Fußfessel schlägt Alarm! Die Polizei ist auf dem Weg!")
            self.wanted_level = min(5, self.wanted_level + 2)
            self.stamina = max(1, self.stamina - 5)
            return
        
        # Zufällige Begegnung basierend auf Gefahrenlevel
        encounter_chance = 0.3 + (district.danger_level * 0.1)
        
        if random.random() < encounter_chance:
            self.criminal_encounter(district)
        else:
            print("\n[STADT] Die Straße ist ruhig. Du findest nichts Nützliches hier.")
            self.stamina = max(1, self.stamina - 2)
    
    def handle_district_feature(self, district):
        """Handle special district features"""
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
        """Regular district exploration without special features"""
        # Fußfessel kann Aktivitäten einschränken
        if self.ankle_monitor and random.random() < 0.3:
            print("\n[FUSSFESSEL] Deine Fußfessel schlägt Alarm! Die Polizei ist auf dem Weg!")
            self.wanted_level = min(5, self.wanted_level + 2)
            self.stamina = max(1, self.stamina - 5)
            return
        
        # Zufällige Begegnung basierend auf Gefahrenlevel
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
        
        if encounter["type"] == "police":
            self.police_encounter()
        elif encounter["type"] == "security":
            self.security_encounter()
        elif encounter["type"] == "motel_security":
            self.motel_security_encounter()
        elif encounter["type"] == "swat":
            self.swat_encounter()
        elif encounter["type"] == "dock_security":
            self.dock_security_encounter()
        elif encounter["type"] == "customs":
            self.customs_encounter()
        elif encounter["type"] == "container_guard":
            self.container_guard_encounter()
        elif encounter["type"] == "private_security":
            self.private_security_encounter()
        elif encounter["type"] == "coast_guard":
            self.coast_guard_encounter()
        elif encounter["type"] == "gang":
            self.gang_encounter("gang")
        elif encounter["type"] == "cartel":
            self.gang_encounter("cartel")
        elif encounter["type"] == "dealer":
            self.drug_encounter()
        elif encounter["type"] == "tourist":
            self.opportunity_encounter("tourist", district)
        elif encounter["type"] == "rich_person":
            self.opportunity_encounter("rich_person", district)
        elif encounter["type"] == "car":
            self.opportunity_encounter("car", district)
        elif encounter["type"] == "beach_vendor":
            self.opportunity_encounter("beach_vendor", district)
        elif encounter["type"] == "tourist_family":
            self.opportunity_encounter("tourist_family", district)
        elif encounter["type"] == "bank_teller":
            self.opportunity_encounter("bank_teller", district)
        elif encounter["type"] == "businessman":
            self.opportunity_encounter("businessman", district)
        elif encounter["type"] == "informant":
            self.opportunity_encounter("informant", district)
        elif encounter["type"] == "drug_lab":
            self.opportunity_encounter("drug_lab", district)
        elif encounter["type"] == "smugglers":
            self.opportunity_encounter("smugglers", district)
        elif encounter["type"] == "black_market":
            self.opportunity_encounter("black_market", district)
        elif encounter["type"] == "smuggler_boat":
            self.opportunity_encounter("smuggler_boat", district)
        elif encounter["type"] == "alligators":
            self.alligator_encounter()
        elif encounter["type"] == "wealthy_resident":
            self.opportunity_encounter("wealthy_resident", district)
        elif encounter["type"] == "elite_criminal":
            self.opportunity_encounter("elite_criminal", district)
    def police_encounter(self):
        print("\n[POLICE] POLIZEI-KONFRONTATION")
        action = input("Möchtest du kämpfen, fliehen oder bestechen? (kämpfen/fliehen/bestechen) ")
        
        if action == "kämpfen":
            self.combat_police("police")
        elif action == "fliehen":
            self.flee_police("police")
        elif action == "bestechen":
            self.bribe_police("police")
        else:
            print("Du zögerst zu lange!")
            self.combat_police("police")
    
    def combat_police(self, police_type):
        police_stats = {
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
        
        stats = police_stats.get(police_type, police_stats["police"])
        police_stamina = stats["stamina"]
        
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
            
            # Chance auf Drachen-Halluzination nach Niederlage
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
        bribe_cost = {
            "police": 200,
            "security": 150,
            "swat": 500,
            "coast_guard": 300,
            "motel_security": 100,
            "dock_security": 175,
            "customs": 250,
            "container_guard": 125,
            "private_security": 400
        }
        
        cost = bribe_cost.get(police_type, 200)
        
        if self.cash >= cost:
            self.cash -= cost
            print(f"Du bestechst die {police_type}-Einheit mit ${cost}!")
            self.wanted_level = max(0, self.wanted_level - 1)
        else:
            print(f"Du hast nicht genug Geld für die Bestechung (${cost} benötigt)!")
            self.combat_police(police_type)

    def security_encounter(self):
        """Handle security guard encounters"""
        print("\n[SECURITY] SICHERHEITS-KONFRONTATION")
        action = input("Möchtest du kämpfen, fliehen oder bestechen? (kämpfen/fliehen/bestechen) ")
        
        if action == "kämpfen":
            self.combat_police("security")
        elif action == "fliehen":
            self.flee_police("security")
        elif action == "bestechen":
            self.bribe_police("security")
        else:
            print("Du zögerst zu lange!")
            self.combat_police("security")

    def motel_security_encounter(self):
        """Handle motel security encounters"""
        print("\n[MOTEL] MOTEL-SICHERHEITS-KONFRONTATION")
        action = input("Möchtest du kämpfen, fliehen oder bestechen? (kämpfen/fliehen/bestechen) ")
        
        if action == "kämpfen":
            self.combat_police("motel_security")
        elif action == "fliehen":
            self.flee_police("motel_security")
        elif action == "bestechen":
            self.bribe_police("motel_security")
        else:
            print("Du zögerst zu lange!")
            self.combat_police("motel_security")

    def swat_encounter(self):
        """Handle SWAT team encounters"""
        print("\n[SWAT] SWAT-KONFRONTATION")
        action = input("Möchtest du kämpfen, fliehen oder bestechen? (kämpfen/fliehen/bestechen) ")
        
        if action == "kämpfen":
            self.combat_police("swat")
        elif action == "fliehen":
            self.flee_police("swat")
        elif action == "bestechen":
            self.bribe_police("swat")
        else:
            print("Du zögerst zu lange!")
            self.combat_police("swat")

    def dock_security_encounter(self):
        """Handle dock security encounters"""
        print("\n[DOCK] DOCK-SICHERHEITS-KONFRONTATION")
        action = input("Möchtest du kämpfen, fliehen oder bestechen? (kämpfen/fliehen/bestechen) ")
        
        if action == "kämpfen":
            self.combat_police("dock_security")
        elif action == "fliehen":
            self.flee_police("dock_security")
        elif action == "bestechen":
            self.bribe_police("dock_security")
        else:
            print("Du zögerst zu lange!")
            self.combat_police("dock_security")

    def customs_encounter(self):
        """Handle customs encounters"""
        print("\n[CUSTOMS] ZOLL-KONFRONTATION")
        action = input("Möchtest du kämpfen, fliehen oder bestechen? (kämpfen/fliehen/bestechen) ")
        
        if action == "kämpfen":
            self.combat_police("customs")
        elif action == "fliehen":
            self.flee_police("customs")
        elif action == "bestechen":
            self.bribe_police("customs")
        else:
            print("Du zögerst zu lange!")
            self.combat_police("customs")

    def container_guard_encounter(self):
        """Handle container guard encounters"""
        print("\n[CONTAINER] CONTAINER-WÄCHTER-KONFRONTATION")
        action = input("Möchtest du kämpfen, fliehen oder bestechen? (kämpfen/fliehen/bestechen) ")
        
        if action == "kämpfen":
            self.combat_police("container_guard")
        elif action == "fliehen":
            self.flee_police("container_guard")
        elif action == "bestechen":
            self.bribe_police("container_guard")
        else:
            print("Du zögerst zu lange!")
            self.combat_police("container_guard")

    def private_security_encounter(self):
        """Handle private security encounters"""
        print("\n[PRIVATE] PRIVATE-SICHERHEITS-KONFRONTATION")
        action = input("Möchtest du kämpfen, fliehen oder bestechen? (kämpfen/fliehen/bestechen) ")
        
        if action == "kämpfen":
            self.combat_police("private_security")
        elif action == "fliehen":
            self.flee_police("private_security")
        elif action == "bestechen":
            self.bribe_police("private_security")
        else:
            print("Du zögerst zu lange!")
            self.combat_police("private_security")

    def coast_guard_encounter(self):
        """Handle coast guard encounters"""
        print("\n[COAST] KÜSTENWACHE-KONFRONTATION")
        action = input("Möchtest du kämpfen, fliehen oder bestechen? (kämpfen/fliehen/bestechen) ")
        
        if action == "kämpfen":
            self.combat_police("coast_guard")
        elif action == "fliehen":
            self.flee_police("coast_guard")
        elif action == "bestechen":
            self.bribe_police("coast_guard")
        else:
            print("Du zögerst zu lange!")
            self.combat_police("coast_guard")

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
        gang_power = random.randint(20, 40) if gang_type == "gang" else random.randint(30, 60)
        
        combat_chance = 0.4 + (self.combat_skill * 0.02) + (len(self.inventory) * 0.08)
        
        if random.random() < combat_chance:
            print(f"Du besiegst die {gang_type}-Mitglieder!")
            loot = random.randint(300, 800) if gang_type == "cartel" else random.randint(150, 400)
            self.cash += loot
            self.reputation += 10
            print(f"Du erbeutest ${loot} und Waffen!")
            
            # Kapitel-Fortschritt prüfen
            self.story_manager.check_chapter_progression(self)
        else:
            print(f"Du wirst von der {gang_type} besiegt!")
            self.cash = max(0, self.cash // 3)
            self.stamina = max(1, self.stamina - 20)
            self.partner_trust = max(0, self.partner_trust - 15)
            print("Du verlierst Geld und das Vertrauen deines Partners!")
            
            # Story-Event für niedriges Partner-Vertrauen
            if self.partner_trust < 30 and not self.story_flags["partner_betrayed"]:
                self.story_flags["partner_betrayed"] = True
                self.story_manager.trigger_story_event("partner_trust_low", self)
            
            # Hohe Chance auf Drachen-Halluzination nach Gang-Niederlage
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
            
            # Kapitel-Fortschritt prüfen
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
                
                # Sofortige Halluzination bei starker Droge
                if drug["intensity"] > 0.6:
                    effect.trigger_dragon_hallucination(self)
                    self.dragon_encounters += 1
                    
                    # Story-Event für erste Drachen-Halluzination
                    if not self.story_flags["first_dragon_seen"]:
                        self.story_flags["first_dragon_seen"] = True
                        self.story_manager.trigger_story_event("first_dragon", self)
            else:
                print("Du hast nicht genug Geld für Drogen!")
        else:
            print("Du lehnst das Angebot ab.")
    
    def alligator_encounter(self):
        """Handle alligator encounters in the Everglades"""
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
    
    def handle_tourism_season(self, district):
        """Handle Ocean Beach tourism season feature"""
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
            if choice == 1:
                self.tourist_robbery_season(district)
            elif choice == 2:
                self.organize_beach_party(district)
            elif choice == 3:
                self.infiltrate_hotel_reception(district)
            elif choice == 4:
                self.explore_district_regular(district)
            else:
                print("Ungültige Wahl!")
                self.explore_district_regular(district)
        except ValueError:
            print("Ungültige Eingabe!")
            self.explore_district_regular(district)
    
    def tourist_robbery_season(self, district):
        """Tourist robbery with season bonuses"""
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
        
        # Adjusted encounter chance based on season
        police_chance = 0.3 * season["police_multiplier"]
        
        if random.random() < police_chance:
            print("\n[POLICE] Ein Polizist hat dich bemerkt!")
            self.police_encounter("police")
        else:
            print(f"\n[SUCCESS] Erfolgreicher Diebstahl bei {tourist_type}!")
            print(f"Basis: ${base_cash} + Saison-Bonus: ${bonus_cash} = ${total_cash}")
            self.cash += total_cash
            district.reputation += 2
            self.stamina -= 3
    
    def organize_beach_party(self, district):
        """Organize beach party for profit"""
        print("\n[PARTY] Du organisierst eine Strand-Party...")
        
        if self.cash < 100:
            print("Du brauchst mindestens $100 für die Organisation!")
            return
        
        self.cash -= 100
        self.stamina -= 5
        
        # Party success based on reputation and stealth
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
        """Infiltrate hotel reception for information theft"""
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
        """Handle Washington Beach motel network feature"""
        print(f"\n[MOTEL] MOTEL-NETZWERK in {district.name}")
        print("Das Motel-Netzwerk bietet verschiedene Möglichkeiten:")
        print("1. Motel-Gäste ausrauben")
        print("2. Motel-Rezeption infiltrieren")
        print("3. Motel-Zimmer als Versteck mieten")
        print("4. Reguläre Erkundung")
        
        try:
            choice = int(input("Wähle eine Option (1-4): "))
            if choice == 1:
                self.motel_guest_robbery(district)
            elif choice == 2:
                self.motel_reception_infiltrate(district)
            elif choice == 3:
                self.rent_motel_room(district)
            elif choice == 4:
                self.explore_district_regular(district)
            else:
                print("Ungültige Wahl!")
                self.explore_district_regular(district)
        except ValueError:
            print("Ungültige Eingabe!")
            self.explore_district_regular(district)
    
    def handle_surveillance(self, district):
        """Handle Vice Point surveillance feature"""
        print(f"\n[SURVEILLANCE] ÜBERWACHUNGS-SYSTEM in {district.name}")
        print("Die Überwachungskameras können ein Vorteil oder Hindernis sein:")
        print("1. Überwachung umgehen (Einbruch)")
        print("2. Überwachungsdaten stehlen")
        print("3. Reiche Bewohner beobachten")
        print("4. Reguläre Erkundung")
        
        try:
            choice = int(input("Wähle eine Option (1-4): "))
            if choice == 1:
                self.bypass_surveillance(district)
            elif choice == 2:
                self.steal_surveillance_data(district)
            elif choice == 3:
                self.observe_residents(district)
            elif choice == 4:
                self.explore_district_regular(district)
            else:
                print("Ungültige Wahl!")
                self.explore_district_regular(district)
        except ValueError:
            print("Ungültige Eingabe!")
            self.explore_district_regular(district)
    
    def handle_container_management(self, district):
        """Handle Viceport container management feature"""
        print(f"\n[CONTAINER] CONTAINER-MANAGEMENT in {district.name}")
        print("Die Container-Terminals bieten viele Möglichkeiten:")
        print("1. Container plündern")
        print("2. Schmuggel-Container finden")
        print("3. Dock-Arbeiter bestechen")
        print("4. Reguläre Erkundung")
        
        try:
            choice = int(input("Wähle eine Option (1-4): "))
            if choice == 1:
                self.loot_container(district)
            elif choice == 2:
                self.find_smuggle_container(district)
            elif choice == 3:
                self.bribe_dock_workers(district)
            elif choice == 4:
                self.explore_district_regular(district)
            else:
                print("Ungültige Wahl!")
                self.explore_district_regular(district)
        except ValueError:
            print("Ungültige Eingabe!")
            self.explore_district_regular(district)
    
    def handle_corporate_crime(self, district):
        """Handle Downtown corporate crime feature"""
        print(f"\n[CORPORATE] UNTERNEHMENSKRIMINALITÄT in {district.name}")
        print("Die Geschäftswelt hat ihre dunklen Seiten:")
        print("1. Firma erpressen")
        print("2. Banküberfall planen")
        print("3. Geschäftsdaten stehlen")
        print("4. Reguläre Erkundung")
        
        try:
            choice = int(input("Wähle eine Option (1-4): "))
            if choice == 1:
                self.extort_company(district)
            elif choice == 2:
                self.plan_bank_heist(district)
            elif choice == 3:
                self.steal_business_data(district)
            elif choice == 4:
                self.explore_district_regular(district)
            else:
                print("Ungültige Wahl!")
                self.explore_district_regular(district)
        except ValueError:
            print("Ungültige Eingabe!")
            self.explore_district_regular(district)
    
    def handle_territory_control(self, district):
        """Handle Little Haiti territory control feature"""
        print(f"\n[TERRITORY] GEBIETS-KONTROLLE in {district.name}")
        print("Gebiets-Kontrolle erfordert Strategie:")
        print("1. Rivale Gang angreifen")
        print("2. Gebiet übernehmen")
        print("3. Schutzgelder eintreiben")
        print("4. Reguläre Erkundung")
        
        try:
            choice = int(input("Wähle eine Option (1-4): "))
            if choice == 1:
                self.attack_rival_gang(district)
            elif choice == 2:
                self.take_territory(district)
            elif choice == 3:
                self.collect_protection_money(district)
            elif choice == 4:
                self.explore_district_regular(district)
            else:
                print("Ungültige Wahl!")
                self.explore_district_regular(district)
        except ValueError:
            print("Ungültige Eingabe!")
            self.explore_district_regular(district)
    
    def handle_social_climbing(self, district):
        """Handle Starfish Island social climbing feature"""
        print(f"\n[SOCIAL] GESELLSCHAFTLICHER AUFSTIEG in {district.name}")
        print("In der High Society geht es um Einfluss:")
        print("1. Luxus-Party infiltrieren")
        print("2. Reiche Kontakte knüpfen")
        print("3. Villa ausrauben")
        print("4. Reguläre Erkundung")
        
        try:
            choice = int(input("Wähle eine Option (1-4): "))
            if choice == 1:
                self.infiltrate_luxury_party(district)
            elif choice == 2:
                self.make_rich_contacts(district)
            elif choice == 3:
                self.rob_mansion(district)
            elif choice == 4:
                self.explore_district_regular(district)
            else:
                print("Ungültige Wahl!")
                self.explore_district_regular(district)
        except ValueError:
            print("Ungültige Eingabe!")
            self.explore_district_regular(district)
    
    def handle_swamp_base(self, district):
        """Handle Everglades swamp base feature"""
        print(f"\n[SWAMP] SUMPF-BASIS in {district.name}")
        print("Der Sumpf bietet ideale Verstecke:")
        print("1. Sumpf-Versteck einrichten")
        print("2. Drogenlabor finden")
        print("3. Schmuggler-Routen nutzen")
        print("4. Reguläre Erkundung")
        
        try:
            choice = int(input("Wähle eine Option (1-4): "))
            if choice == 1:
                self.setup_swamp_hideout(district)
            elif choice == 2:
                self.find_drug_lab_swamp(district)
            elif choice == 3:
                self.use_smuggler_routes(district)
            elif choice == 4:
                self.explore_district_regular(district)
            else:
                print("Ungültige Wahl!")
                self.explore_district_regular(district)
        except ValueError:
            print("Ungültige Eingabe!")
            self.explore_district_regular(district)
    
    def handle_island_smuggling(self, district):
        """Handle Vice Keys island smuggling feature"""
        print(f"\n[ISLAND] INSEL-SCHMUGGEL in {district.name}")
        print("Die Inseln sind perfekt für Schmuggel:")
        print("1. Schmuggel-Boot kapern")
        print("2. Schwarzmarkt besuchen")
        print("3. Menschenhandel unterbinden")
        print("4. Reguläre Erkundung")
        
        try:
            choice = int(input("Wähle eine Option (1-4): "))
            if choice == 1:
                self.hijack_smuggle_boat(district)
            elif choice == 2:
                self.visit_island_black_market(district)
            elif choice == 3:
                self.stop_human_trafficking(district)
            elif choice == 4:
                self.explore_district_regular(district)
            else:
                print("Ungültige Wahl!")
                self.explore_district_regular(district)
        except ValueError:
            print("Ungültige Eingabe!")
            self.explore_district_regular(district)
    
    def steal_business_data(self, district):
        """Steal corporate data for ransom"""
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
    
    def attack_rival_gang(self, district):
        """Attack rival gangs for territory control"""
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
        """Take control of territory from rivals"""
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
        """Collect protection money from local businesses"""
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
        """Infiltrate luxury parties for theft and networking"""
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
        """Make contacts with rich and influential people"""
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
        """Rob mansions in Starfish Island"""
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
        """Set up a hideout in the Everglades"""
        print("\n[SWAMP] Du richtest ein Sumpf-Versteck ein...")
        if self.cash >= 300:
            self.cash -= 300
            print("\n[SUCCESS] Sumpf-Versteck eingerichtet! Sicherer Rückzugsort.")
            self.stamina = min(self.level * 25, self.stamina + 15)
            district.reputation += 2
        else:
            print("Du hast nicht genug Geld für ein Versteck ($300 benötigt)!")
    
    def find_drug_lab_swamp(self, district):
        """Find and raid drug labs in the Everglades"""
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
        """Use smuggler routes for quick transport and profit"""
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
        """Hijack smuggling boats for cargo and profit"""
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
        """Visit exclusive island black market"""
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
        """Stop human trafficking operations (for reward)"""
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
                    
                    # Story-Event für erstes Verbrechen
                    if not self.story_flags["first_crime_committed"]:
                        self.story_flags["first_crime_committed"] = True
                        self.story_manager.trigger_story_event("first_crime", self)
                    
                    # Kapitel-Fortschritt prüfen
                    self.story_manager.check_chapter_progression(self)
                else:
                    print("Die Aktion schlägt fehl!")
                    self.wanted_level = min(5, self.wanted_level + 1)
                    self.stamina = max(1, self.stamina - opp["stamina_cost"] - 5)
            else:
                print("Du hast nicht genug Ausdauer für diese Aktion!")
        else:
            print("Du lässt die Gelegenheit verstreichen.")
    
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
                    # Erhöhe Wanted Level basierend auf Illegalität
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
        # Kampfkraft basiert auf Waffen, Level und mentaler Stärke
        weapon_damage = sum(item.damage_increase for item in self.inventory)
        mental_strength = max(0, 100 - (self.dragon_encounters * 5))
        
        confront_chance = 0.3 + (self.level * 0.05) + (weapon_damage * 0.01) + (mental_strength * 0.002)
        
        if random.random() < confront_chance:
            damage = random.randint(20, 40) + weapon_damage + (self.level * 3)
            dragon.stamina -= damage
            print(f'Du stellst dich deinen Dämonen! Du verursachst {damage} "psychischen" Schaden!')
            print(f"Drachen-Stärke: {max(0, dragon.stamina)}")
            
            # Drache kontert mit Konsequenzen
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
                dragon.stamina += 10  # Drache wird durch Vermeidung stärker
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
        
        # Speichere den Sieg
        self.dragon_defeated = True
    
    def dragon_defeat(self, dragon):
        print("\n*** DEINE KONSEKUENZEN HOLEN DICH EIN ***")
        print("Der Drache der Konsequenzen hat dich verschlungen.")
        print("Du verlierst alles und landest fuer immer im Gefaengnis... oder schlimmer.")
        
        self.cash = 0
        self.wanted_level = 5
        self.partner_trust = 0
        self.days += 7  # Eine Woche im Krankenhaus/Gefaengnis
        self.stamina = 10
        
        print("Alles ist verloren. Das kriminelle Leben hat dich bezahlt.")
    
    def visit_mission_board(self):
        """Display available missions and mission givers"""
        print("\n[MISSION] MISSION-BRETT")
        print("Verfügbare Missionen und Kontakte:")
        
        # Check for mission unlocks
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
        """Start a specific mission"""
        if self.mission_manager.start_mission(mission, self):
            print(f"\n🎉 Mission '{mission.name}' erfolgreich abgeschlossen!")
        else:
            print(f"\n💥 Mission '{mission.name}' fehlgeschlagen oder abgebrochen.")
    
    def initialize_missions(self):
        """Initialize all missions and mission givers"""
        # Create mission givers
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
        
        # Register mission givers
        self.mission_manager.register_mission_giver(rico)
        self.mission_manager.register_mission_giver(maria)
        
        # Create missions
        self.create_first_taste_mission()
        self.create_beach_party_mission()
        
        # Make first mission available
        first_mission = self.mission_manager.all_missions.get("First Taste of Vice City")
        if first_mission:
            first_mission.available = True
    
    def create_first_taste_mission(self):
        """Create the first tutorial mission"""
        mission = Mission(
            "First Taste of Vice City",
            1,  # Chapter 1
            2,  # Difficulty
            {"cash": 500, "reputation": 5, "partner_trust": 5},
            self.text_display
        )
        
        # Phase 1: The Set-up (Dialogue)
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
        
        # Phase 2: Travel to Vice Point
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
        
        # Phase 3: The Action (Car Theft)
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
        
        # Phase 4: The Escape
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
        """Create the second mission"""
        mission = Mission(
            "Beach Party Cleanup",
            1,  # Chapter 1
            3,  # Difficulty
            {"cash": 800, "reputation": 8, "partner_trust": 3},
            self.text_display
        )
        
        # Phase 1: The Set-up
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
        
        # Phase 2: Infiltration
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
        
        # Phase 3: The Complication
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
        
        # Phase 4: The Escape
        phase4 = MissionPhase(
            "Polizeiflucht",
            "escape",
            "Die Polizei ist wegen des Kampfes auf der Party alarmiert worden!"
        )
        phase4.wanted_increase = 2
        phase4.escape_success_message = "Du verlierst die Polizei in den engen Gassen von Ocean Beach!"
        phase4.escape_failure_message = "Die Polizei stellt dich! Du landest kurzzeitig in Gewahrsam."
        
        mission.phases = [phase1, phase2, phase3, phase4]
        mission.available = False  # Requires first mission completion
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
    
    def save_game(self, filename="savegame.json"):
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
            "clear_screen_enabled": self.text_display.clear_screen_enabled  # Save clear screen preference
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            print(f"Spiel gespeichert als {filename}!")
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
    
    def load_game(self, filename="savegame.json"):
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
            # Restore clear screen preference
            self.text_display.clear_screen_enabled = save_data.get("clear_screen_enabled", False)
            
            return True
        except FileNotFoundError:
            print("Kein Speicherstand gefunden!")
            return False
        except Exception as e:
            print(f"Fehler beim Laden: {e}")
            return False
    
    def save_dragon(self, dragon, filename="dragon.json"):
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
    
    def load_dragon(self, filename="dragon.json"):
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


def main():
    print("=== WILLKOMMEN IN VICE CITY DRAGONS! ===")
    print("Ein kriminelles Abenteuer inspiriert von GTA 6")
    print("1. Neues Spiel starten")
    print("2. Spiel laden")
    choice = input("Waehle eine Option (1-2): ")
    
    if choice == "1":
        print("\nWaehle deinen Protagonisten:")
        print("1. Jason Duval (Ex-Militaer, gute Kampffaehigkeiten)")
        print("2. Lucia Caminos (Frueher aus dem Gefaengnis, gute Stealth-Faehigkeiten)")
        
        protagonist_choice = input("Waehle deinen Charakter (1-2): ")
        if protagonist_choice == "1":
            character_type = "jason"
        elif protagonist_choice == "2":
            character_type = "lucia"
        else:
            print("Standardwahl: Jason")
            character_type = "jason"
        
        hero_name = input(f"Gib den Namen deines {character_type.title()} ein: ")
        protagonist = Protagonist(hero_name, character_type)
        protagonist.initialize_missions()  # Initialize mission system
        dragon = ViceCityDragon()
        
        print(f"\nKAPITEL 1: DER ANFANG")
        chapter_info = protagonist.story_manager.get_chapter_story(1)
        protagonist.text_display.display_progressive(chapter_info['opening'])
        protagonist.text_display.display_progressive(chapter_info['motivation'][character_type])
        print("\n[MISSION] NEUE FUNKTION: Mission-Brett im Hauptmenü verfügbar!")
            
    elif choice == "2":
        protagonist = Protagonist("", "jason")  # Temporaerer Typ
        if protagonist.load_game():
            protagonist.initialize_missions()  # Initialize mission system after loading
            # Restore mission states
            for mission_name, mission in protagonist.mission_manager.all_missions.items():
                if mission_name in protagonist.story_flags.get("completed_missions", []):
                    mission.completed = True
                if mission_name in protagonist.story_flags.get("available_missions", []):
                    mission.available = True
            
            dragon = protagonist.load_dragon()
            print(f"\nWillkommen zurueck, {protagonist.name}!")
            chapter_info = protagonist.story_manager.get_chapter_story(protagonist.chapter)
            print(f"Kapitel {protagonist.chapter}: {chapter_info['title']}")
            protagonist.text_display.display_progressive(chapter_info['opening'])
        else:
            print("Kein gueltiger Speicherstand gefunden. Neues Spiel wird gestartet.")
            hero_name = input("Gib den Namen deines Helden ein: ")
            protagonist = Protagonist(hero_name, "jason")
            protagonist.initialize_missions()
            dragon = ViceCityDragon()
    else:
        print("Ungueltige Wahl! Neues Spiel wird gestartet.")
        hero_name = input("Gib den Namen deines Helden ein: ")
        protagonist = Protagonist(hero_name, "jason")
        protagonist.initialize_missions()
        dragon = ViceCityDragon()
    
    while True:
        print("\n=== VICE CITY HAUPTMENUE ===")
        print("1. Attribute anzeigen")
        print("2. Rasten/Unterschlupf")
        print("3. Vice City erkunden")
        print("4. Schwarzmarkt besuchen")
        print("5. Kriminelles Training")
        print("6. Mission-Brett (Neu!)")
        print("7. Drachen der Konsequenzen konfrontieren")
        print("8. Bildschirm-Löschung umschalten")
        print("9. Spiel speichern")
        print("10. Spiel beenden")
        choice = input("Waehle eine Aktion (1-10): ")
        
        if choice == "1":
            protagonist.display_attributes()
        elif choice == "2":
            protagonist.rest()
        elif choice == "3":
            protagonist.explore_vice_city()
        elif choice == "4":
            protagonist.visit_black_market()
        elif choice == "5":
            protagonist.criminal_training()
        elif choice == "6":
            protagonist.visit_mission_board()
        elif choice == "7":
            protagonist.confront_dragon(dragon)
            protagonist.save_dragon(dragon)
            if protagonist.dragon_defeated:
                print("\n*** VICE CITY DRAGONS BEENDET! ***")
                print("Danke fuers Spielen dieser kriminellen Saga!")
                break
        elif choice == "8":
            protagonist.text_display.toggle_clear_screen()
        elif choice == "9":
            protagonist.save_game()
            protagonist.save_dragon(dragon)
        elif choice == "10":
            save_choice = input("Moechtest du vor dem Beenden speichern? (j/n) ")
            if save_choice.lower() == "j":
                protagonist.save_game()
                protagonist.save_dragon(dragon)
            print("Auf Wiedersehen, Krimineller!")
            break
        else:
            print("Ungültige Wahl, bitte versuche es erneut.")

if __name__ == "__main__":
    main()