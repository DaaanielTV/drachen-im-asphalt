class Journal:
    def __init__(self):
        self.active_missions = []
        self.completed_missions = []
        self.chapter_progress = {
            "current_chapter": 1,
            "chapter_history": [1]
        }
        self.major_choices = []
        self.npc_relationships = {}

    def sync_missions(self, mission_manager):
        self.active_missions = [mission.name for mission in mission_manager.active_missions if not mission.completed]
        self.completed_missions = [mission.name for mission in mission_manager.completed_missions]

    def set_chapter(self, chapter):
        self.chapter_progress["current_chapter"] = chapter
        if chapter not in self.chapter_progress["chapter_history"]:
            self.chapter_progress["chapter_history"].append(chapter)
            self.chapter_progress["chapter_history"].sort()

    def record_choice(self, choice_text, consequence_text=""):
        entry = {"choice": choice_text}
        if consequence_text:
            entry["consequence"] = consequence_text
        self.major_choices.append(entry)

    def set_relationship(self, npc_name, value):
        self.npc_relationships[npc_name] = value

    def to_dict(self):
        return {
            "active_missions": self.active_missions,
            "completed_missions": self.completed_missions,
            "chapter_progress": self.chapter_progress,
            "major_choices": self.major_choices,
            "npc_relationships": self.npc_relationships,
        }

    @classmethod
    def from_dict(cls, data):
        journal = cls()
        journal.active_missions = data.get("active_missions", [])
        journal.completed_missions = data.get("completed_missions", [])
        journal.chapter_progress = data.get(
            "chapter_progress",
            {"current_chapter": 1, "chapter_history": [1]}
        )
        journal.major_choices = data.get("major_choices", [])
        journal.npc_relationships = data.get("npc_relationships", {})
        return journal

    def display(self, story_manager):
        print("\n=== JOURNAL & QUEST-LOG ===")

        print("\n[AKTIVE MISSIONEN]")
        if self.active_missions:
            for mission in self.active_missions:
                print(f"- {mission}")
        else:
            print("- Keine aktiven Missionen")

        print("\n[ABGESCHLOSSENE MISSIONEN]")
        if self.completed_missions:
            for mission in self.completed_missions:
                print(f"- {mission}")
        else:
            print("- Noch keine Mission abgeschlossen")

        chapter = self.chapter_progress.get("current_chapter", 1)
        chapter_info = story_manager.get_chapter_story(chapter)
        print("\n[KAPITEL-FORTSCHRITT]")
        print(f"Aktuelles Kapitel: {chapter} - {chapter_info['title']}")
        history = ", ".join(str(c) for c in self.chapter_progress.get("chapter_history", [chapter]))
        print(f"Freigeschaltete Kapitel: {history}")

        print("\n[WICHTIGE ENTSCHEIDUNGEN]")
        if self.major_choices:
            for i, choice in enumerate(self.major_choices[-10:], 1):
                line = f"{i}. {choice.get('choice', 'Unbekannte Entscheidung')}"
                if choice.get("consequence"):
                    line += f" -> {choice['consequence']}"
                print(line)
        else:
            print("- Noch keine wichtigen Entscheidungen protokolliert")

        print("\n[NPC-BEZIEHUNGEN]")
        if self.npc_relationships:
            for npc, score in self.npc_relationships.items():
                print(f"- {npc}: {score}")
        else:
            print("- Keine Beziehungen bekannt")
