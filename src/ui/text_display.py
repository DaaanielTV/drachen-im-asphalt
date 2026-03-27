import os
import random
import re


class TextDisplayManager:
    def __init__(self):
        self.display_mode = "progressive"
        self.chunk_size = 80
        self.prompt_text = "[Leertaste zum Fortfahren]"
        self.skip_enabled = True
        self.clear_screen_enabled = False
        
    def split_text_into_chunks(self, text):
        text = text.strip()
        
        if not text:
            return []
        
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            
            current_chunk = ""
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                if len(current_chunk + sentence) > self.chunk_size and current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    current_chunk += (" " if current_chunk else "") + sentence
            
            if current_chunk:
                chunks.append(current_chunk.strip())
        
        return chunks
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def add_white_space(self):
        white_lines = random.randint(100, 200)
        
        for _ in range(white_lines):
            print()
        return True
    
    def display_progressive(self, text, force_instant=False):
        if self.display_mode == "instant" or force_instant:
            print(text)
            return
        
        chunks = self.split_text_into_chunks(text)
        
        for i, chunk in enumerate(chunks):
            if i > 0 and self.clear_screen_enabled:
                self.clear_screen()
                print(f"[Bildschirm gelöscht - Zeige nächsten Textabschnitt]\n")
            
            print(chunk)
            
            if i < len(chunks) - 1:
                self.add_white_space()
    
    def display_story_event(self, event_text):
        print("\n[STORY] GESCHICHTEN-MOMENT:")
        self.display_progressive(event_text)
        print()
    
    def display_dialogue(self, speaker, text):
        print(f"\n{speaker}:")
        self.display_progressive(text)
    
    def display_mission_text(self, text):
        print("\n[MISSION]")
        self.display_progressive(text)
    
    def display_dragon_text(self, text):
        print(f"\n {text}")
    
    def set_display_mode(self, mode):
        if mode in ["instant", "progressive", "typewriter"]:
            self.display_mode = mode
    
    def toggle_clear_screen(self):
        self.clear_screen_enabled = not self.clear_screen_enabled
        status = "aktiviert" if self.clear_screen_enabled else "deaktiviert"
        print(f"Bildschirm-Löschung zwischen Textabschnitten {status}.")
        return self.clear_screen_enabled
