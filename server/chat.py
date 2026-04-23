from dataclasses import dataclass, field
from typing import list
import time


@dataclass
class ChatMessage:
    player_id: str
    player_name: str
    message: str
    timestamp: float = field(default_factory=time.time)
    chat_type: str = "local"


class ChatManager:
    def __init__(self):
        self.global_messages: list[ChatMessage] = []
        self.local_messages: dict[str, list[ChatMessage]] = {}
        self.max_global = 50
        self.max_local = 20

    def add_global_message(self, player_id: str, player_name: str, message: str) -> ChatMessage:
        chat_msg = ChatMessage(
            player_id=player_id,
            player_name=player_name,
            message=message,
            chat_type="global"
        )
        self.global_messages.append(chat_msg)
        if len(self.global_messages) > self.max_global:
            self.global_messages = self.global_messages[-self.max_global:]
        return chat_msg

    def add_local_message(self, player_id: str, player_name: str, district: str, message: str) -> ChatMessage:
        chat_msg = ChatMessage(
            player_id=player_id,
            player_name=player_name,
            message=message,
            chat_type="local"
        )
        if district not in self.local_messages:
            self.local_messages[district] = []
        self.local_messages[district].append(chat_msg)
        if len(self.local_messages[district]) > self.max_local:
            self.local_messages[district] = self.local_messages[district][-self.max_local:]
        return chat_msg

    def get_global_messages(self, since: float = 0) -> list[dict]:
        return [
            {"player_name": m.player_name, "message": m.message, "timestamp": m.timestamp}
            for m in self.global_messages if m.timestamp > since
        ]

    def get_local_messages(self, district: str, since: float = 0) -> list[dict]:
        messages = self.local_messages.get(district, [])
        return [
            {"player_name": m.player_name, "message": m.message, "timestamp": m.timestamp}
            for m in messages if m.timestamp > since
        ]

    def to_dict(self) -> dict:
        return {
            "global": [
                {"player_name": m.player_name, "message": m.message, "timestamp": m.timestamp}
                for m in self.global_messages
            ]
        }