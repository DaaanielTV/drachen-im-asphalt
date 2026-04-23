import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import time
from src.networking.world_state import SharedWorldState, DistrictState
from src.districts.district_manager import DistrictManager


class StateSynchronizer:
    def __init__(self):
        self.world_state = SharedWorldState()
        self._initialize_world()
        self.last_broadcast = time.time()
        self.broadcast_interval = 5.0

    def _initialize_world(self) -> None:
        district_names = [
            "Ocean Beach", "Washington Beach", "Vice Point", "Viceport",
            "Downtown", "Little Haiti", "Starfish Island", "Everglades", "Vice Keys"
        ]
        for name in district_names:
            self.world_state.district_states[name] = DistrictState(name=name)

    def get_world_state(self) -> dict:
        return self.world_state.to_dict()

    def update_world_from_player(self, player_id: str, game_state: dict) -> None:
        if "current_district" in game_state:
            district = game_state["current_district"]
            if district in self.world_state.district_states:
                ds = self.world_state.district_states[district]
                if "reputation" in game_state:
                    ds.reputation = game_state["reputation"]

        if "chapter" in game_state:
            chapter = game_state["chapter"]
            if chapter > self.world_state.chapter:
                self.world_state.chapter = chapter
                self.world_state.set_story_flag(f"chapter_{chapter}_unlocked", True)

    def add_completed_mission(self, mission_name: str) -> bool:
        return self.world_state.add_completed_mission(mission_name)

    def notify_player_join(self, player_id: str) -> None:
        active = self.world_state.active_events
        if "players_online" not in active:
            active.append("players_online")
        self.world_state.last_update = time.time()

    def notify_player_leave(self, player_id: str) -> None:
        self.world_state.last_update = time.time()

    def get_changes_since(self, timestamp: float) -> dict:
        return self.world_state.get_changes_since(timestamp)

    def save_world(self, filepath: str) -> bool:
        return self.world_state.save(filepath)

    def load_world(self, filepath: str) -> bool:
        loaded = SharedWorldState.load(filepath)
        if loaded:
            self.world_state = loaded
            return True
        return False

    def should_broadcast(self) -> bool:
        now = time.time()
        if now - self.last_broadcast >= self.broadcast_interval:
            self.last_broadcast = now
            return True
        return False