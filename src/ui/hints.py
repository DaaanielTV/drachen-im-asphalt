from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.ui.tutorial import TutorialMode


@dataclass
class Hint:
    id: str
    category: str
    priority: int
    title: str
    text: str
    condition_func: Optional[callable] = None
    cooldown_days: int = 0


class HintSystem:
    def __init__(self):
        self.hints: dict[str, Hint] = {}
        self.shown_hints: dict[str, int] = {}
        self.tutorial_mode = False
        self.tutorial: Optional["TutorialMode"] = None
        self._initialize_hints()

    def _initialize_hints(self):
        self.hints = {
            "low_cash_1": Hint(
                id="low_cash_1",
                category="Finanzen",
                priority=1,
                title="Geld verdienen",
                text="Dein Bargeld ist niedrig. Besuche das Schwarzmarkt-Angebot oder nimm Missionen an, um Cash zu verdienen.",
            ),
            "low_stamina_1": Hint(
                id="low_stamina_1",
                category="Ausdauer",
                priority=1,
                title="Ausdauer regenerieren",
                text="Deine Ausdauer ist erschöpft. Ruhe dich aus (Option 2), um neue Kraft zu tanken.",
            ),
            "high_wanted_1": Hint(
                id="high_wanted_1",
                category="Polizei",
                priority=2,
                title="Hohe Fahndungsstufe",
                text="Dein Wanted Level ist hoch. Besuche einen sicheren Ort oder warte, bis sich die Lage beruhigt.",
            ),
            "low_trust_1": Hint(
                id="low_trust_1",
                category="Beziehungen",
                priority=2,
                title="Partner-Vertrauen sinkt",
                text="Dein Partner vertraut dir weniger. Schließe Missionen erfolgreich ab, um das Vertrauen zu stärken.",
            ),
            "new_mission_available": Hint(
                id="new_mission_available",
                category="Missionen",
                priority=1,
                title="Neue Mission verfügbar",
                text="Ein neuer Auftrag wartet auf dich. Besuche das Missionsbrett (Option 6).",
            ),
            "weapon_recommended": Hint(
                id="weapon_recommended",
                category="Ausrüstung",
                priority=2,
                title="Bessere Waffe nötig",
                text="Dein Inventar ist leer. Besuche den Schwarzmarkt, um Waffen zu kaufen.",
            ),
            "drug_available": Hint(
                id="drug_available",
                category="Ausrüstung",
                priority=3,
                title="Drogen verfügbar",
                text="Drogen können kurzfristig helfen, aber sie haben Nebenwirkungen. Sei vorsichtig!",
            ),
            "explore_new_district": Hint(
                id="explore_new_district",
                category="Erkundung",
                priority=2,
                title="Neue Gebiete erkunden",
                text="Du hast noch nicht alle Stadtteile erkundet. Erkundung bringt neue Möglichkeiten.",
            ),
            "dragon_encounter_warning": Hint(
                id="dragon_encounter_warning",
                category="Drachen",
                priority=2,
                title="Drachenschatten nahen",
                text="Dein Stresslevel steigt. Die Drachen werden stärker. Ruhe dich aus oder nimm Drogen - mit Risiko.",
            ),
            "chapter_story_hint": Hint(
                id="chapter_story_hint",
                category="Geschichte",
                priority=1,
                title="Kapitel fortsetzen",
                text="Erreiche ein neues Level, um das nächste Kapitel der Geschichte freizuschalten.",
            ),
            "training_available": Hint(
                id="training_available",
                category="Fähigkeiten",
                priority=2,
                title="Training möglich",
                text="Du kannst deine Fähigkeiten verbessern (Option 5: Training).",
            ),
            "safe_house_benefit": Hint(
                id="safe_house_benefit",
                category="Immobilien",
                priority=3,
                title="Sicheres Haus",
                text="Immobilien können als safe houses dienen. Prüfe das Schwarzmarkt-Angebot.",
            ),
            "black_market_deal": Hint(
                id="black_market_deal",
                category="Handel",
                priority=2,
                title="Schwarzmarkt-Angebot",
                text="Im Schwarzmarkt kannst du kaufen und verkaufen. Preise variieren!",
            ),
            "ng_plus_benefit": Hint(
                id="ng_plus_benefit",
                category="Neuanfang",
                priority=3,
                title="New Game+",
                text="Nach dem Sieg kannst du im New Game+ weiterspielen mit verstärktem Gegner.",
            ),
            "achievement_hint": Hint(
                id="achievement_hint",
                category="Erfolge",
                priority=4,
                title="Mehr Achievements",
                text="Erkunde alle Gebiete und schließe Missionen ab, um Achievements freizuschalten.",
            ),
        }

    def should_show_hint(self, hint_id: str, days: int) -> bool:
        if hint_id not in self.shown_hints:
            return True
        last_shown = self.shown_hints[hint_id]
        hint = self.hints.get(hint_id)
        if hint and days - last_shown >= hint.cooldown_days:
            return True
        return False

    def mark_hint_shown(self, hint_id: str, days: int) -> None:
        self.shown_hints[hint_id] = days

    def get_contextual_hints(self, protagonist) -> list[Hint]:
        hints = []
        days = protagonist.days if hasattr(protagonist, "days") else 0

        if protagonist.cash < 100 and self.should_show_hint("low_cash_1", days):
            hints.append(self.hints["low_cash_1"])
            self.mark_hint_shown("low_cash_1", days)

        if protagonist.stamina < 10 and self.should_show_hint("low_stamina_1", days):
            hints.append(self.hints["low_stamina_1"])
            self.mark_hint_shown("low_stamina_1", days)

        if protagonist.wanted_level >= 3 and self.should_show_hint("high_wanted_1", days):
            hints.append(self.hints["high_wanted_1"])
            self.mark_hint_shown("high_wanted_1", days)

        if protagonist.partner_trust < 50 and self.should_show_hint("low_trust_1", days):
            hints.append(self.hints["low_trust_1"])
            self.mark_hint_shown("low_trust_1", days)

        if len(protagonist.inventory) == 0 and self.should_show_hint("weapon_recommended", days):
            hints.append(self.hints["weapon_recommended"])
            self.mark_hint_shown("weapon_recommended", days)

        if hasattr(protagonist, "hallucination_intensity") and protagonist.hallucination_intensity > 0.5:
            if self.should_show_hint("dragon_encounter_warning", days):
                hints.append(self.hints["dragon_encounter_warning"])
                self.mark_hint_shown("dragon_encounter_warning", days)

        if hasattr(protagonist, "story_flags"):
            explored = protagonist.story_flags.get("explored_districts", [])
            total_districts = len(protagonist.district_manager.districts) if hasattr(protagonist, "district_manager") else 9
            if len(explored) < total_districts // 2 and self.should_show_hint("explore_new_district", days):
                hints.append(self.hints["explore_new_district"])
                self.mark_hint_shown("explore_new_district", days)

        return hints

    def show_hint(self, hint: Hint) -> None:
        print(f"\n{'=' * 50}")
        print(f"[TIPP] {hint.title}")
        print(f"{'=' * 50}")
        print(hint.text)
        print(f"{'=' * 50}\n")

    def show_all_contextual_hints(self, protagonist) -> None:
        hints = self.get_contextual_hints(protagonist)
        if hints:
            print("\n[INFO] AKTUELLE HINWEISE:")
            for hint in hints:
                print(f"  [{hint.category}] {hint.title}: {hint.text[:60]}...")
        else:
            print("\n[INFO] Keine speziellen Hinweise für deine Situation.")

    def enable_tutorial_mode(self) -> None:
        self.tutorial_mode = True
        self._initialize_tutorial_hints()

    def disable_tutorial_mode(self) -> None:
        self.tutorial_mode = False

    def _initialize_tutorial_hints(self) -> None:
        tutorial_hints = {
            "tutorial_movement": Hint(
                id="tutorial_movement",
                category="Tutorial",
                priority=0,
                title="So navigierst du",
                text="Wähle eine Zahl (1-10) und drücke Enter, um eine Aktion auszuführen.",
                cooldown_days=1
            ),
            "tutorial_save": Hint(
                id="tutorial_save",
                category="Tutorial",
                priority=0,
                title="Spielstand speichern",
                text="Wähle Option 9, um deinen Fortschritt zu speichern. Speichere regelmäßig!",
                cooldown_days=1
            ),
            "tutorial_explore": Hint(
                id="tutorial_explore",
                category="Tutorial",
                priority=0,
                title="Vice City erkunden",
                text="Mit Option 3 kannst du die Stadt erkunden und Abenteuer erleben.",
                cooldown_days=1
            ),
            "tutorial_mission": Hint(
                id="tutorial_mission",
                category="Tutorial",
                priority=0,
                title="Missionen annehmen",
                text="Option 6 zeigt verfügbare Missionen. Schließe sie ab, um Cash und Reputation zu verdienen.",
                cooldown_days=1
            ),
            "tutorial_blackmarket": Hint(
                id="tutorial_blackmarket",
                category="Tutorial",
                priority=0,
                title="Schwarzmarkt",
                text="Option 4 öffnet den Schwarzmarkt. Kaufe Waffen und andere Gegenstände.",
                cooldown_days=1
            ),
        }
        self.hints.update(tutorial_hints)

    def get_hint_count(self) -> int:
        return len(self.hints)

    def get_shown_count(self) -> int:
        return len(self.shown_hints)

    def reset_shown_hints(self) -> None:
        self.shown_hints = {}

    def to_dict(self) -> dict:
        return {
            "shown_hints": self.shown_hints,
            "tutorial_mode": self.tutorial_mode
        }

    def load_from_dict(self, data: dict) -> None:
        if "shown_hints" in data:
            self.shown_hints = data["shown_hints"]
        if "tutorial_mode" in data:
            self.tutorial_mode = data["tutorial_mode"]

    def set_tutorial(self, tutorial: "TutorialMode") -> None:
        self.tutorial = tutorial

    def get_current_tutorial_step(self) -> Optional[dict]:
        if self.tutorial:
            step = self.tutorial.get_current_step()
            if step:
                return {"id": step.id, "title": step.title, "content": step.content}
        return None

    def start_tutorial(self) -> None:
        if self.tutorial:
            self.tutorial.start()
            self.tutorial_mode = True

    def advance_tutorial(self) -> bool:
        if self.tutorial:
            return self.tutorial.advance()
        return False