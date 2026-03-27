from __future__ import annotations


class MissionBoardService:
    def __init__(self, mission_manager):
        self.mission_manager = mission_manager

    def refresh_available_missions(self, protagonist):
        self.mission_manager.check_mission_unlocks(protagonist)
        return self.mission_manager.get_available_missions(protagonist)

    def select_mission(self, available_missions, choice_index):
        if 0 <= choice_index < len(available_missions):
            return available_missions[choice_index]
        return None

    def run_mission(self, mission, protagonist):
        return self.mission_manager.start_mission(mission, protagonist)
