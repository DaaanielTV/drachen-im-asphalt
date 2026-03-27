class District:
    def __init__(self, name, description, danger_level, opportunities, special_feature=None):
        self.name = name
        self.description = description
        self.danger_level = danger_level
        self.opportunities = opportunities
        self.special_feature = special_feature
        self.reputation = 0
        self.control_level = 0
        self.discovered_features = []
        
    def describe(self):
        print(f"\n{self.name}")
        print(f"{self.description}")
        print(f"Gefahrenlevel: {'*' * self.danger_level}")
        print(f"Dein Ruf: {self.reputation} | Einfluss: {self.control_level}%")
        if self.special_feature and self.special_feature in self.discovered_features:
            print(f"Spezial-Feature: {self.get_special_feature_description()}")
    
    def get_special_feature_description(self):
        features = {
            "tourism_season": "Tourismus-Saison System",
            "motel_network": "Motel-Netzwerk",
            "surveillance": "Überwachungs-System",
            "container_management": "Container-Management",
            "corporate_crime": "Unternehmenskriminalität",
            "territory_control": "Gebiets-Kontrolle",
            "social_climbing": "Gesellschaftlicher Aufstieg",
            "swamp_base": "Sumpf-Basis",
            "island_smuggling": "Insel-Schmuggel"
        }
        return features.get(self.special_feature, "Unbekanntes Feature")
    
    def unlock_feature(self):
        if self.special_feature and self.special_feature not in self.discovered_features:
            self.discovered_features.append(self.special_feature)
            return True
        return False
