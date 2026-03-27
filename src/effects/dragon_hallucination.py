import random


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
        self.distortion_chars = {
            "a": ["à", "@", "ä"],
            "e": ["3", "€", "ë"],
            "i": ["1", "!", "ï"],
            "o": ["0", "ö"],
            "s": ["$", "§"],
            "u": ["ü", "µ"]
        }
    
    def trigger_encounter(self, trigger_type, protagonist, intensity=0.0):
        matching = [e for e in self.encounters if e["trigger"] == trigger_type]
        encounter = random.choice(matching) if matching else None
        if encounter:
            description = self.distort_text(encounter["description"], intensity)
            print(f"\n[DRACHE] {description}")
            self.apply_effect(encounter["effect"], protagonist, intensity)
            if hasattr(protagonist, "dragon_encounters"):
                protagonist.dragon_encounters += 1
            return True
        return False
    
    def apply_effect(self, effect_type, protagonist, intensity=0.0):
        intensity_bonus = max(0, int(intensity * 10))
        if effect_type == "paranoia":
            protagonist.stamina = max(1, protagonist.stamina - (8 + intensity_bonus))
            if hasattr(protagonist, "stress_level"):
                protagonist.stress_level = min(100, protagonist.stress_level + 10 + intensity_bonus)
            print("Dein Stresslevel steigt. Ausdauer verringert.")
        elif effect_type == "hallucination":
            protagonist.cash = max(0, protagonist.cash - random.randint(50, 200 + (intensity_bonus * 10)))
            print("In der Verwirrung verlierst du Geld.")
        elif effect_type == "distrust":
            if hasattr(protagonist, 'partner_trust'):
                protagonist.partner_trust = max(0, protagonist.partner_trust - (10 + intensity_bonus))
                print("Das Vertrauen zu deinem Partner schwindet.")

    def distort_text(self, text, intensity):
        if intensity <= 0.2:
            return text
        distorted_text = []
        for char in text:
            lower_char = char.lower()
            if lower_char in self.distortion_chars and random.random() < intensity * 0.25:
                replacement = random.choice(self.distortion_chars[lower_char])
                distorted_text.append(replacement)
            elif random.random() < intensity * 0.03:
                distorted_text.append(char * 2)
            else:
                distorted_text.append(char)
        return "".join(distorted_text)
