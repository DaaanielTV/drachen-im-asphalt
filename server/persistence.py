import json
import os
from pathlib import Path
from typing import Any


class ServerPersistence:
    def __init__(self, data_dir: str = "data/server"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def save_world_state(self, world_state: dict[str, Any]) -> bool:
        try:
            filepath = self.data_dir / "world_state.json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(world_state, f, indent=2)
            return True
        except Exception:
            return False

    def load_world_state(self) -> dict[str, Any] | None:
        try:
            filepath = self.data_dir / "world_state.json"
            with open(filepath, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def save_player_state(self, player_id: str, state: dict[str, Any]) -> bool:
        try:
            filepath = self.data_dir / f"player_{player_id}.json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
            return True
        except Exception:
            return False

    def load_player_state(self, player_id: str) -> dict[str, Any] | None:
        try:
            filepath = self.data_dir / f"player_{player_id}.json"
            with open(filepath, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def delete_player_state(self, player_id: str) -> bool:
        try:
            filepath = self.data_dir / f"player_{player_id}.json"
            if filepath.exists():
                filepath.unlink()
            return True
        except Exception:
            return False

    def list_saved_players(self) -> list[str]:
        try:
            return [
                f.stem.replace("player_", "")
                for f in self.data_dir.glob("player_*.json")
            ]
        except Exception:
            return []