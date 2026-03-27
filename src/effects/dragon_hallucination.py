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
