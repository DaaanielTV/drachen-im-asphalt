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
        self.visited_count = 0
        self.available_activities = []
        self.npc_contacts = []
        self.resources = {"weapons": [], "drugs": [], "intel": []}

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
            "island_smuggling": "Insel-Schmuggel",
            "industrial_zone": "Industrie-Gebiet",
            "airport_operations": "Flughafen-Operationen",
            "suburban_network": "Vorstadt-Netzwerk",
            "casino_empire": "Casino-Imperium",
        }
        return features.get(self.special_feature, "Unbekanntes Feature")

    def unlock_feature(self):
        if self.special_feature and self.special_feature not in self.discovered_features:
            self.discovered_features.append(self.special_feature)
            return True
        return False

    def visit(self):
        self.visited_count += 1

    def get_encounter_difficulty(self) -> int:
        base = self.danger_level
        if self.control_level > 50:
            base -= 1
        elif self.control_level < 25:
            base += 1
        return max(1, base)

    def add_npc_contact(self, npc_name: str, role: str) -> None:
        contact = {"name": npc_name, "role": role}
        if contact not in self.npc_contacts:
            self.npc_contacts.append(contact)

    def get_available_activities(self) -> list[str]:
        activities = []
        if self.control_level >= 20:
            activities.append("protective_shake")
        if self.control_level >= 40:
            activities.append("resource_collection")
        if self.control_level >= 60:
            activities.append("expansion_operations")
        if self.control_level >= 80:
            activities.append("territory_upgrade")
        if self.visited_count >= 5:
            activities.append("deep_cover")
        return activities

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "danger_level": self.danger_level,
            "reputation": self.reputation,
            "control_level": self.control_level,
            "discovered_features": self.discovered_features,
            "visited_count": self.visited_count,
            "npc_contacts": self.npc_contacts,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "District":
        district = cls(
            name=data["name"],
            description=data.get("description", ""),
            danger_level=data.get("danger_level", 5),
            opportunities=data.get("opportunities", []),
            special_feature=data.get("special_feature"),
        )
        district.reputation = data.get("reputation", 0)
        district.control_level = data.get("control_level", 0)
        district.discovered_features = data.get("discovered_features", [])
        district.visited_count = data.get("visited_count", 0)
        district.npc_contacts = data.get("npc_contacts", [])
        return district
