import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.networking.engine import GameEngine
from src.networking.world_state import SharedWorldState
from src.networking.player_state import PlayerRegistry
from server.connection_manager import ConnectionManager
from server.sync import StateSynchronizer
from server.presence import PresenceManager


class CommandDispatcher:
    def __init__(
        self,
        connection_manager: ConnectionManager,
        state_synchronizer: StateSynchronizer,
        presence_manager: PresenceManager
    ):
        self.connection_manager = connection_manager
        self.state_synchronizer = state_synchronizer
        self.presence_manager = presence_manager

        self.engines: dict[str, GameEngine] = {}
        self.player_registry = PlayerRegistry()

    def get_engine(self, player_id: str) -> GameEngine:
        if player_id not in self.engines:
            self.engines[player_id] = GameEngine()
        return self.engines[player_id]

    async def dispatch(self, player_id: str, message: dict) -> None:
        msg_type = message.get("type")
        payload = message.get("payload", {})

        handlers = {
            "create_character": self._handle_create_character,
            "command": self._handle_game_command,
            "chat": self._handle_chat,
            "ping": self._handle_ping,
            "sync": self._handle_sync,
        }

        handler = handlers.get(msg_type)
        if not handler:
            await self.connection_manager.send_to_player(player_id, {
                "type": "error",
                "message": f"Unbekannter Nachrichtentyp: {msg_type}"
            })
            return

        await handler(player_id, payload)

    async def _handle_create_character(self, player_id: str, payload: dict) -> None:
        name = payload.get("name")
        character_type = payload.get("character_type")

        if not name or not character_type:
            await self.connection_manager.send_to_player(player_id, {
                "type": "error",
                "message": "Name und Charaktertyp erforderlich"
            })
            return

        engine = self.get_engine(player_id)
        result = engine.create_character(name, character_type)

        if result.success:
            self.player_registry.add_player(player_id, name, character_type)
            self.presence_manager.update_player_info(
                player_id,
                {"name": name, "character_type": character_type, "district": "Ocean Beach"}
            )

            await self.connection_manager.send_to_player(player_id, {
                "type": "character_created",
                "game_state": result.game_state,
                "message": result.message
            })

            await self._broadcast_player_list()
        else:
            await self.connection_manager.send_to_player(player_id, {
                "type": "error",
                "message": result.message
            })

    async def _handle_game_command(self, player_id: str, payload: dict) -> None:
        engine = self.engines.get(player_id)
        if not engine:
            await self.connection_manager.send_to_player(player_id, {
                "type": "error",
                "message": "Kein Charakter erstellt"
            })
            return

        command = payload.get("command")
        params = payload.get("params", {})

        result = engine.execute_command(command, **params)

        if result.success:
            if "game_state" in result.message:
                game_state = result.game_state
            else:
                game_state = engine.get_state()

            self.player_registry.update_player_state(player_id, game_state)

            district = game_state.get("current_district")
            if district:
                self.presence_manager.update_player_info(
                    player_id,
                    {"district": district}
                )
                await self._broadcast_district_update(district)

            await self.connection_manager.send_to_player(player_id, {
                "type": "command_result",
                "success": True,
                "message": result.message,
                "game_state": game_state,
                "updates": result.updates
            })

            if result.updates.get("type") in ("new_character", "quit"):
                await self._broadcast_player_list()
        else:
            await self.connection_manager.send_to_player(player_id, {
                "type": "command_result",
                "success": False,
                "message": result.message
            })

    async def _handle_chat(self, player_id: str, payload: dict) -> None:
        player = self.player_registry.get_player(player_id)
        if not player:
            return

        chat_type = payload.get("chat_type", "local")
        message = payload.get("message", "")

        if chat_type == "local":
            target_district = player.current_district
            recipients = self.player_registry.get_players_in_district(target_district)
        else:
            recipients = self.player_registry.get_active_players()

        chat_message = {
            "type": "chat",
            "player_id": player_id,
            "player_name": player.name,
            "message": message,
            "chat_type": chat_type
        }

        for recipient in recipients:
            await self.connection_manager.send_to_player(
                recipient.player_id,
                chat_message
            )

    async def _handle_ping(self, player_id: str, payload: dict) -> None:
        await self.connection_manager.send_to_player(player_id, {
            "type": "pong",
            "timestamp": payload.get("timestamp")
        })

    async def _handle_sync(self, player_id: str, payload: dict) -> None:
        world_state = self.state_synchronizer.get_world_state()
        await self.connection_manager.send_to_player(player_id, {
            "type": "world_state",
            "data": world_state
        })

        engine = self.engines.get(player_id)
        if engine:
            game_state = engine.get_state()
            await self.connection_manager.send_to_player(player_id, {
                "type": "game_state",
                "data": game_state
            })

    async def _broadcast_player_list(self) -> None:
        players = [
            {
                "player_id": p.player_id,
                "name": p.name,
                "character_type": p.character_type,
                "current_district": p.current_district,
                "connected": p.connected
            }
            for p in self.player_registry.get_active_players()
        ]

        await self.connection_manager.broadcast({
            "type": "player_list",
            "players": players
        })

    async def _broadcast_district_update(self, district: str) -> None:
        players_in_district = self.player_registry.get_players_in_district(district)
        await self.connection_manager.broadcast({
            "type": "district_update",
            "district": district,
            "players": [p.name for p in players_in_district]
        })