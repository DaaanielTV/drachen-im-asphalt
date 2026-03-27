class MissionGiver:
    def __init__(self, name, location, personality, description):
        self.name = name
        self.location = location
        self.personality = personality
        self.description = description
        self.available_missions = []
        self.relationship_level = 0
        self.met_before = False
        
    def introduce(self, protagonist):
        if not self.met_before:
            print(f"\n[KONTAKT] NEUER KONTAKT: {self.name}")
            print(f"Ort: {self.location}")
            print(f"Beschreibung: {self.description}")
            self.met_before = True
        else:
            print(f"\n[KONTAKT] KONTAKT: {self.name}")
            
    def offer_mission(self, mission, protagonist):
        if mission.is_available(protagonist):
            print(f"\n[MISSION] MISSION-ANGEBOT: {mission.name}")
            print(f"Schwierigkeit: {'*' * mission.difficulty}")
            print(f"Belohnung: ${mission.rewards.get('cash', 0)}, +{mission.rewards.get('reputation', 0)} Reputation")
            
            accept = input("Möchtest du diese Mission annehmen? (ja/nein): ")
            if accept.lower() == "ja":
                return True
        else:
            print(f"\n[UNVERFÜGBAR] Mission '{mission.name}' ist noch nicht verfügbar.")
            if protagonist.chapter < mission.chapter:
                print(f"Benötigt Kapitel {mission.chapter} (Du bist in Kapitel {protagonist.chapter})")
        return False
    
    def update_relationship(self, change):
        self.relationship_level = max(0, min(100, self.relationship_level + change))
