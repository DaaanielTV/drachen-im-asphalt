from dataclasses import dataclass, field
from typing import Any
import time


@dataclass
class PlayerState:
    player_id: str
    name: str
    character_type: str
    current_district: str = "Ocean Beach"
    connected: bool = True
    last_active: float = field(default_factory=time.time)
    cash: int = 500
    level: int = 1
    stamina: int = 30
    wanted_level: int = 0
    reputation: int = 0
    chapter: int = 1
    mission_state: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "player_id": self.player_id,
            "name": self.name,
            "character_type": self.character_type,
            "current_district": self.current_district,
            "connected": self.connected,
            "last_active": self.last_active,
            "cash": self.cash,
            "level": self.level,
            "stamina": self.stamina,
            "wanted_level": self.wanted_level,
            "reputation": self.reputation,
            "chapter": self.chapter,
            "mission_state": self.mission_state,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PlayerState":
        return cls(
            player_id=data["player_id"],
            name=data["name"],
            character_type=data["character_type"],
            current_district=data.get("current_district", "Ocean Beach"),
            connected=data.get("connected", True),
            last_active=data.get("last_active", time.time()),
            cash=data.get("cash", 500),
            level=data.get("level", 1),
            stamina=data.get("stamina", 30),
            wanted_level=data.get("wanted_level", 0),
            reputation=data.get("reputation", 0),
            chapter=data.get("chapter", 1),
            mission_state=data.get("mission_state", {}),
        )

    def update_activity(self) -> None:
        self.last_active = time.time()
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False
        self.last_active = time.time()

    def reconnect(self) -> None:
        self.connected = True
        self.last_active = time.time()

    def is_active(self, timeout_seconds: int = 300) -> bool:
        return self.connected and (time.time() - self.last_active) < timeout_seconds

    def update_from_game_state(self, game_state: dict[str, Any]) -> None:
        self.cash = game_state.get("cash", self.cash)
        self.level = game_state.get("level", self.level)
        self.stamina = game_state.get("stamina", self.stamina)
        self.wanted_level = game_state.get("wanted_level", self.wanted_level)
        self.reputation = game_state.get("reputation", self.reputation)
        self.chapter = game_state.get("chapter", self.chapter)
        self.current_district = game_state.get("current_district", self.current_district)


class PlayerRegistry:
    def __init__(self):
        self.players: dict[str, PlayerState] = {}

    def add_player(self, player_id: str, name: str, character_type: str) -> PlayerState:
        player = PlayerState(
            player_id=player_id,
            name=name,
            character_type=character_type,
        )
        self.players[player_id] = player
        return player

    def get_player(self, player_id: str) -> PlayerState | None:
        return self.players.get(player_id)

    def remove_player(self, player_id: str) -> bool:
        if player_id in self.players:
            del self.players[player_id]
            return True
        return False

    def get_all_players(self) -> list[PlayerState]:
        return list(self.players.values())

    def get_active_players(self) -> list[PlayerState]:
        return [p for p in self.players.values() if p.connected]

    def get_players_in_district(self, district_name: str) -> list[PlayerState]:
        return [
            p for p in self.players.values()
            if p.connected and p.current_district == district_name
        ]

    def update_player_state(self, player_id: str, game_state: dict[str, Any]) -> bool:
        player = self.players.get(player_id)
        if not player:
            return False
        player.update_from_game_state(game_state)
        player.update_activity()
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            player_id: player.to_dict()
            for player_id, player in self.players.items()
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PlayerRegistry":
        registry = cls()
        for player_id, player_data in data.items():
            registry.players[player_id] = PlayerState.from_dict(player_data)
        return registry