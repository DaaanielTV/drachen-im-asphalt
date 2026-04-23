import asyncio
import json
import websockets
from typing import Callable


class GameClient:
    def __init__(self, server_url: str = "ws://localhost:8000"):
        self.server_url = server_url
        self.websocket = None
        self.player_id = None
        self.running = False
        self.handlers: dict[str, Callable] = {}

    def register_handler(self, msg_type: str, handler: Callable) -> None:
        self.handlers[msg_type] = handler

    async def connect(self, player_id: str) -> bool:
        self.player_id = player_id
        url = f"{self.server_url}/ws/{player_id}"
        try:
            self.websocket = await websockets.connect(url)
            self.running = True
            return True
        except Exception:
            return False

    async def disconnect(self) -> None:
        self.running = False
        if self.websocket:
            await self.websocket.close()

    async def send(self, msg_type: str, payload: dict) -> None:
        if not self.websocket:
            return
        message = {"type": msg_type, "payload": payload}
        await self.websocket.send(json.dumps(message))

    async def send_command(self, command: str, **params) -> None:
        await self.send("command", {"command": command, "params": params})

    async def create_character(self, name: str, character_type: str) -> None:
        await self.send("create_character", {"name": name, "character_type": character_type})

    async def send_chat(self, message: str, chat_type: str = "local") -> None:
        await self.send("chat", {"message": message, "chat_type": chat_type})

    async def ping(self) -> None:
        import time
        await self.send("ping", {"timestamp": time.time()})

    async def listen(self) -> None:
        while self.running:
            try:
                if not self.websocket:
                    break
                message = await self.websocket.recv()
                await self._handle_message(message)
            except Exception:
                break

    async def _handle_message(self, raw: str) -> None:
        try:
            message = json.loads(raw)
        except json.JSONDecodeError:
            return

        msg_type = message.get("type")
        handler = self.handlers.get(msg_type)
        if handler:
            await handler(message)

    async def receive_loop(self) -> None:
        asyncio.create_task(self.listen())

        while self.running:
            await asyncio.sleep(0.1)