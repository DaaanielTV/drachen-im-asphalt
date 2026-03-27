import random
import time


class DrugEffect:
    def __init__(self, name, intensity, duration):
        self.name = name
        self.intensity = intensity
        self.duration = duration
        self.remaining = duration
    
    def apply_effect(self, protagonist):
        if self.remaining > 0:
            if hasattr(protagonist, "stress_level"):
                stress_shift = int((self.intensity * 6) - 1)
                protagonist.stress_level = min(100, max(0, protagonist.stress_level + stress_shift))

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
