from fastapi import WebSocket
from typing import dict
import asyncio


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, player_id: str) -> None:
        await websocket.accept()
        self.active_connections[player_id] = websocket

    def disconnect(self, player_id: str) -> None:
        if player_id in self.active_connections:
            del self.active_connections[player_id]

    async def send_to_player(self, player_id: str, message: dict) -> bool:
        websocket = self.active_connections.get(player_id)
        if not websocket:
            return False
        try:
            await websocket.send_json(message)
            return True
        except Exception:
            self.disconnect(player_id)
            return False

    async def broadcast(self, message: dict, exclude: list[str] | None = None) -> None:
        exclude = exclude or []
        for player_id, websocket in list(self.active_connections.items()):
            if player_id not in exclude:
                try:
                    await websocket.send_json(message)
                except Exception:
                    self.disconnect(player_id)

    async def broadcast_to_district(self, district: str, message: dict, exclude: str | None = None) -> None:
        pass

    def get_player_count(self) -> int:
        return len(self.active_connections)

    def is_connected(self, player_id: str) -> bool:
        return player_id in self.active_connections