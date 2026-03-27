class MissionManager:
    def __init__(self):
        self.mission_givers = {}
        self.all_missions = {}
        self.active_missions = []
        self.completed_missions = []
        
    def register_mission_giver(self, giver):
        self.mission_givers[giver.name] = giver
        
    def register_mission(self, mission):
        self.all_missions[mission.name] = mission
        
    def get_available_missions(self, protagonist):
        available = []
        for mission in self.all_missions.values():
            if mission.is_available(protagonist) and mission not in self.active_missions:
                available.append(mission)
        return available
    
    def start_mission(self, mission, protagonist):
        if mission.start_mission(protagonist):
            self.active_missions.append(mission)
            self.completed_missions.append(mission)
            return True
        return False
    
    def check_mission_unlocks(self, protagonist):
        for mission in self.all_missions.values():
            if not mission.available and mission.is_available(protagonist):
                mission.available = True
                print(f"\n🔓 NEUE MISSION VERFÜGBAR: {mission.name}")
