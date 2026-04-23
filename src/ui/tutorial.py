from dataclasses import dataclass
from typing import Optional


@dataclass
class TutorialStep:
    id: str
    title: str
    content: str
    action_required: Optional[str] = None
    completed: bool = False
    shown: bool = False


class TutorialMode:
    def __init__(self):
        self.steps: list[TutorialStep] = []
        self.current_step: int = 0
        self.active: bool = False
        self._initialize_steps()

    def _initialize_steps(self):
        self.steps = [
            TutorialStep(
                id="welcome",
                title="Willkommen in Vice City",
                content="""Du bist gerade in Vice City angekommen - eine Stadt voller Möglichkeiten und Gefahren.

Dein Ziel: Baue deine kriminelle Karriere auf, meistere die Unterwelt und besiege den Drachen der Konsequenzen.

Die Stadt hat verschiedene Stadtteile mit unterschiedlichen Gefahren und Belohnungen.""",
                action_required=None
            ),
            TutorialStep(
                id="character",
                title="Dein Charakter",
                content="""Du hast einen von zwei Charakteren gewählt:

JASON - Der Ex-Soldat:
- Hoher Nahkampf-Wert (15)
- Mittlerer Stealth-Wert (10)
- Gut für direkte Konfrontation

LUCIA - Die Ausbrecherin:
- Mittlerer Nahkampf-Wert (10)
- Hoher Stealth-Wert (15)
- Gut für heimliche Aktionen

Deine Entscheidungen beeinflussen das Vertrauen deines Partners.""",
                action_required=None
            ),
            TutorialStep(
                id="basic_actions",
                title="Grundlegende Aktionen",
                content="""Im Hauptmenü hast du folgende Optionen:

1. Attribute anzeigen - Zeigt deinen Status (Cash, Level, etc.)
2. Ausruhen - Stellt Ausdauer wieder her
3. Erkunden - Erkunde die Stadt für Zufallsereignisse
4. Schwarzmarkt - Kaufe Waffen und andere Gegenstände
5. Training - Verbessere deine Fähigkeiten
6. Missionsbrett - Nimm Aufträge an
7. Drachen konfrontieren - Fordere das Endspiel heraus

Tipp: Speichere regelmäßig mit Option 9!""",
                action_required=None
            ),
            TutorialStep(
                id="resources",
                title="Ressourcen verwalten",
                content="""Achte auf deine Ressourcen:

AUSDAUER: Wird bei Aktionen verbraucht. Ruhe aus, um sie zu regenerieren.
CASH: Dein Bargeld. Verdiene es durch Missionen und Verbrechen.
WANTED LEVEL: Je höher, desto mehr Polizei sucht dich.
REPUTATION: Dein Ruf in der Unterwelt. Steigt durch Erfolge.
PARTNER-TRUST: Das Vertrauen deines Partners. Sinkt bei Verrat.""",
                action_required=None
            ),
            TutorialStep(
                id="missions",
                title="Missionen",
                content="""Missionen sind dein Haupteinkommensquelle:

- Nimm Missionen über das Missionsbrett an
- Jede Mission hat Phasen: Dialog, Reise, Aktion, Flucht
- Dein Erfolg hängt von Level, Kampfkunst und Stealth ab
- Belohnungen: Cash, Reputation, Partner-Vertrauen
- Misserfolge erhöhen das Wanted Level und kosten Ausdauer

Schließe deine erste Mission ab, um ins nächste Kapitel zu kommen!""",
                action_required="mission"
            ),
            TutorialStep(
                id="exploration",
                title="Erkundung",
                content="""Die Stadt hat 9 verschiedene Stadtteile:

Ocean Beach - Touristen, niedrige Gefahr
Washington Beach - Motels, mittlere Gefahr
Vice Point - Einbrüche, hohe Gefahr
Viceport - Schmuggel, sehr hohe Gefahr
Downtown - Überfälle, hohe Gefahr
Little Haiti - Gang-Gebiet, gefährlich
Starfish Island - Luxusvillen, mittlere Gefahr
Everglades - Sumpf, am gefährlichsten
Vice Keys - Inseln, Boot-Schmuggel

Jeder Stadtteil hat einzigartige Verbrechensmöglichkeiten!""",
                action_required=None
            ),
            TutorialStep(
                id="draconian_consequences",
                title="Der Drache der Konsequenzen",
                content="""Deine Taten haben Konsequenzen - buchstäblich:

- Jede kriminelle Handlung erhöht den 'Stress'
- Hoher Stress führt zu Drachen-Halluzinationen
- Drogen verstärken die Halluzinationen
- Die Drachen werden stärker, je mehr du sündigst

Wenn dein Stress zu hoch wird, siehst du Drachen in der Stadt.
Am Ende musst du den Drachen der Konsequenzen besiegen!""",
                action_required=None
            ),
            TutorialStep(
                id="advanced",
                title="Fortgeschrittene Tipps",
                content="""Fortgeschrittene Strategien:

- STEALTH: Reduziert Entdeckungs-Chance
- TRAINING: Verbessert dauerhaft deine Fähigkeiten
- PARTNER: Hohe Trust = bessere Belohnungen
- NEW GAME+: Nach dem Sieg mit verstärkten Feinden weiterspielen

Erkunde alles, schließe Missionen ab und finde deinen Weg zum Sieg!
Viel Glück, Krimineller!""",
                action_required=None
            ),
        ]

    def start(self) -> None:
        self.active = True
        self.current_step = 0
        for step in self.steps:
            step.completed = False
            step.shown = False

    def stop(self) -> None:
        self.active = False

    def get_current_step(self) -> Optional[TutorialStep]:
        if not self.active or self.current_step >= len(self.steps):
            return None
        return self.steps[self.current_step]

    def advance(self) -> bool:
        if self.current_step < len(self.steps):
            self.steps[self.current_step].completed = True
            self.current_step += 1
            if self.current_step < len(self.steps):
                self.steps[self.current_step].shown = True
            return True
        return False

    def skip_to_step(self, step_id: str) -> bool:
        for i, step in enumerate(self.steps):
            if step.id == step_id:
                self.current_step = i
                step.shown = True
                return True
        return False

    def get_progress(self) -> tuple[int, int]:
        completed = sum(1 for s in self.steps if s.completed)
        return (completed, len(self.steps))

    def show_all(self) -> None:
        self.active = True
        for step in self.steps:
            step.shown = True

    def to_dict(self) -> dict:
        return {
            "active": self.active,
            "current_step": self.current_step,
            "steps": [
                {"id": s.id, "completed": s.completed, "shown": s.shown}
                for s in self.steps
            ]
        }

    def load_from_dict(self, data: dict) -> None:
        if "active" in data:
            self.active = data["active"]
        if "current_step" in data:
            self.current_step = data["current_step"]
        if "steps" in data:
            for step_data in data["steps"]:
                for step in self.steps:
                    if step.id == step_data.get("id"):
                        step.completed = step_data.get("completed", False)
                        step.shown = step_data.get("shown", False)