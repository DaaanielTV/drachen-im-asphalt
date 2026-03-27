import random


class ViceCityDragon:
    def __init__(self):
        self.name = "Der Drache der Konsequenzen"
        self.stamina = 150
        self.level = 15
        self.defeated = False
        self.manifestation = "metaphorisch"
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
        
        dragon_line = random.choice(self.story_lines)
        print(f"[DRACHE] '{dragon_line}'")
        print(f"Deine Schuld und deine schlechten Entscheidungen wiegen schwer...")
        
        if random.random() < 0.3:
            protagonist.partner_trust = max(0, protagonist.partner_trust - 5)
            print("Dein Vertrauen zu deinem Partner schwindet unter der Last der Konsequenzen.")
