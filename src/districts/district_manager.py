from src.districts.district import District


class DistrictManager:
    def __init__(self, protagonist):
        self.protagonist = protagonist
        self.districts = {}
        self.seasonal_events = {}
        self.initialize_districts()
        
    def initialize_districts(self):
        self.districts = {
            "Ocean Beach": District(
                "Ocean Beach",
                "Strände, Neonlichter und Touristenfallen. Perfekt für kleine Diebstähle.",
                3,
                ["taschendiebstahl", "touristen_abzocken"],
                "tourism_season"
            ),
            "Washington Beach": District(
                "Washington Beach",
                "Mittelmäßige Strände und heruntergekommene Motels. Ein Ort, an dem Touristen seltener werden und die Kriminalität zunimmt.",
                4,
                ["motel_raids", "beach_vendor_extortion", "tourist_scamming"],
                "motel_network"
            ),
            "Vice Point": District(
                "Vice Point",
                "Wohngegend mit reichen Bewohnern. Gute Gelegenheiten für Einbrüche.",
                5,
                ["einbruch", "autodiebstahl"],
                "surveillance"
            ),
            "Viceport": District(
                "Viceport",
                "Container-Terminals und Lagerhäuser dominieren die Skyline. Hier laufen die illegalen Importe der Stadt zusammen.",
                6,
                ["container_smuggling", "dockyard_heists", "shipping_theft"],
                "container_management"
            ),
            "Downtown": District(
                "Downtown",
                "Geschäftsviertel mit Banken und Bürogebäuden. Risiko, aber hohe Gewinne.",
                7,
                ["überfall", "erpressung"],
                "corporate_crime"
            ),
            "Little Haiti": District(
                "Little Haiti",
                "Gebiet mit starkem Gang-Einfluss. Gefährlich aber lohnend.",
                8,
                ["gang_kämpfe", "drogen_deals"],
                "territory_control"
            ),
            "Starfish Island": District(
                "Starfish Island",
                "Luxusvillen und gepflegte Gärten verbergen dunkle Geheimnisse. Nur die Reichsten und Gefährlichsten leben hier.",
                7,
                ["mansion_burglary", "extortion_rackets", "high_society_crimes"],
                "social_climbing"
            ),
            "Everglades": District(
                "Everglades",
                "Sumpfgebiet außerhalb der Stadt. Treffpunkt für illegale Geschäfte.",
                9,
                ["schmuggel", "drogen_labore"],
                "swamp_base"
            ),
            "Vice Keys": District(
                "Vice Keys",
                "Inseln vor der Küste. Abgeschieden und ideal für verbotene Aktivitäten.",
                6,
                ["schwarzmarkt", "people_smuggling"],
                "island_smuggling"
            )
        }
        
        self.seasonal_events = {
            "high_season": {
                "name": "Hauptsaison",
                "tourist_multiplier": 2.0,
                "police_multiplier": 1.5,
                "rewards_bonus": 1.3
            },
            "low_season": {
                "name": "Nebensaison", 
                "tourist_multiplier": 0.5,
                "police_multiplier": 0.8,
                "rewards_bonus": 0.7
            },
            "normal_season": {
                "name": "Normalsaison",
                "tourist_multiplier": 1.0,
                "police_multiplier": 1.0,
                "rewards_bonus": 1.0
            }
        }
        
        self.current_season = "normal_season"
        self.season_day_counter = 0
    
    def get_district(self, name):
        return self.districts.get(name)
    
    def update_season(self):
        self.season_day_counter += 1
        if self.season_day_counter >= 7:
            self.season_day_counter = 0
            seasons = list(self.seasonal_events.keys())
            current_index = seasons.index(self.current_season)
            self.current_season = seasons[(current_index + 1) % len(seasons)]
            print(f"\n[SEASON] SAISONWECHSEL: {self.seasonal_events[self.current_season]['name']} in Ocean Beach!")
    
    def check_feature_unlock(self, district_name):
        district = self.get_district(district_name)
        if district and district.special_feature:
            unlock_requirements = {
                "tourism_season": {"level": 1, "reputation": 0},
                "motel_network": {"level": 2, "reputation": 10},
                "surveillance": {"level": 3, "reputation": 20},
                "container_management": {"level": 4, "reputation": 30},
                "corporate_crime": {"level": 5, "reputation": 40},
                "territory_control": {"level": 6, "reputation": 50},
                "social_climbing": {"level": 7, "reputation": 60},
                "swamp_base": {"level": 8, "reputation": 70},
                "island_smuggling": {"level": 9, "reputation": 80}
            }
            
            requirements = unlock_requirements.get(district.special_feature, {"level": 1, "reputation": 0})
            
            if (self.protagonist.level >= requirements["level"] and 
                self.protagonist.reputation >= requirements["reputation"] and
                district.special_feature not in district.discovered_features):
                
                if district.unlock_feature():
                    print(f"\n[UNLOCK] NEUES FEATURE FREIGESCHALTET: {district.get_special_feature_description()} in {district_name}!")
                    return True
        return False
