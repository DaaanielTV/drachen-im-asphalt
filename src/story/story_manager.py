from src.ui.text_display import TextDisplayManager


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
            "partner_trust_high": "Dein Partner steht hinter dir. Für einen Moment wirken die Drachen kleiner als eure Loyalität.",
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
        new_chapter = min(6, 1 + protagonist.level // 3)
        if new_chapter > protagonist.chapter:
            protagonist.chapter = new_chapter
            chapter_info = self.get_chapter_story(new_chapter)
            print(f"\n[STORY] KAPITEL {new_chapter}: {chapter_info['title']}")
            self.text_display.display_progressive(chapter_info['opening'])
            if 'theme' in chapter_info:
                print(f"Thema: {chapter_info['theme']}")
            self.trigger_dynamic_consequence_events(protagonist, new_chapter)
            return True
        return False

    def trigger_dynamic_consequence_events(self, protagonist, chapter):
        if not hasattr(protagonist, "consequence_manager"):
            return

        shown_events = protagonist.story_flags.setdefault("shown_consequence_events", [])
        dynamic_events = protagonist.consequence_manager.get_chapter_events(chapter, shown_events)

        for event_id, event_text in dynamic_events:
            self.text_display.display_story_event(event_text)
            shown_events.append(event_id)
