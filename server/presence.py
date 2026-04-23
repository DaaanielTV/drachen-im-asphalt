from typing import dict
from server.connection_manager import ConnectionManager


class PresenceManager:
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.player_info: dict[str, dict] = {}

    def update_player_info(self, player_id: str, info: dict) -> None:
        if player_id not in self.player_info:
            self.player_info[player_id] = {}
        self.player_info[player_id].update(info)

    def get_player_info(self, player_id: str) -> dict | None:
        return self.player_info.get(player_id)

    def player_joined(self, player_id: str) -> None:
        self.player_info[player_id] = {
            "player_id": player_id,
            "status": "online"
        }

    def player_left(self, player_id: str) -> None:
        if player_id in self.player_info:
            self.player_info[player_id]["status"] = "offline"

    def get_all_player_info(self) -> list[dict]:
        return list(self.player_info.values())

    def get_players_in_district(self, district: str) -> list[str]:
        return [
            pid for pid, info in self.player_info.items()
            if info.get("district") == district and info.get("status") == "online"
        ]