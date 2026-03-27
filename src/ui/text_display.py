import os
import re


class TextDisplayManager:
    def __init__(self):
        self.display_mode = "progressive"
        self.chunk_size = 220
        self.prompt_text = "[Enter = weiter | s = Abschnitt ueberspringen | i = sofort alles]"
        self.skip_enabled = True
        self.clear_screen_enabled = False
        self.compact_spacing = True

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

                candidate = (current_chunk + " " + sentence).strip()
                if len(candidate) > self.chunk_size and current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    current_chunk = candidate

            if current_chunk:
                chunks.append(current_chunk.strip())

        return chunks

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _wait_for_advance(self):
        if not self.skip_enabled:
            return "continue"

        while True:
            try:
                user_choice = input(f"\n{self.prompt_text} ").strip().lower()
            except EOFError:
                return "instant"

            if user_choice in {"", "weiter", "w"}:
                return "continue"
            if user_choice in {"s", "skip", "u", "ueberspringen"}:
                return "skip"
            if user_choice in {"i", "instant", "sofort"}:
                return "instant"

            print("Eingabe nicht erkannt. Nutze Enter, s oder i.")

    def display_progressive(self, text, force_instant=False):
        if self.display_mode == "instant" or force_instant:
            print(text)
            return

        chunks = self.split_text_into_chunks(text)
        if not chunks:
            return

        instant_from_here = False

        for i, chunk in enumerate(chunks):
            if i > 0 and self.clear_screen_enabled:
                self.clear_screen()
                print("[Bildschirm geloescht - naechster Abschnitt]\n")

            print(chunk)

            if i >= len(chunks) - 1:
                continue
            if instant_from_here:
                continue

            user_action = self._wait_for_advance()
            if user_action == "skip":
                break
            if user_action == "instant":
                instant_from_here = True

            if not self.compact_spacing:
                print()

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
        print(f"\n{text}")

    def set_display_mode(self, mode):
        if mode in ["instant", "progressive", "typewriter"]:
            self.display_mode = mode
            print(f"Textmodus gesetzt auf: {mode}")

    def set_readability_mode(self, mode):
        settings = {
            "schnell": {"chunk_size": 320, "compact_spacing": True},
            "standard": {"chunk_size": 220, "compact_spacing": True},
            "fokussiert": {"chunk_size": 140, "compact_spacing": False},
        }

        if mode not in settings:
            print("Unbekannter Modus. Verfuegbar: schnell, standard, fokussiert")
            return False

        selected = settings[mode]
        self.chunk_size = selected["chunk_size"]
        self.compact_spacing = selected["compact_spacing"]
        print(f"Lesemodus aktiv: {mode} (Abschnittslaenge: {self.chunk_size})")
        return True

    def toggle_clear_screen(self):
        self.clear_screen_enabled = not self.clear_screen_enabled
        status = "aktiviert" if self.clear_screen_enabled else "deaktiviert"
        print(f"Bildschirm-Loeschung zwischen Textabschnitten {status}.")
        return self.clear_screen_enabled

    def get_controls_help(self):
        return (
            "[HILFE] TEXTEINGABE\n"
            "- Enter: naechsten Abschnitt anzeigen\n"
            "- s: Rest des aktuellen Textblocks ueberspringen\n"
            "- i: verbleibenden Textblock sofort anzeigen\n"
            "- Lesemodus im Hauptmenue anpassbar (schnell/standard/fokussiert)."
        )
