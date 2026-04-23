from dataclasses import dataclass, field
from typing import Optional
import select
import threading
import socket


@dataclass
class PlayerSession:
    player_id: int
    character_name: str
    character_type: str
    is_active: bool = True
    turn_order: int = 0
    shared_resources: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "player_id": self.player_id,
            "character_name": self.character_name,
            "character_type": self.character_type,
            "is_active": self.is_active,
            "turn_order": self.turn_order,
            "shared_resources": self.shared_resources,
        }


@dataclass
class CoOpState:
    mode_enabled: bool = False
    player1_session: Optional[PlayerSession] = None
    player2_session: Optional[PlayerSession] = None
    current_turn: int = 1
    turn_type: str = "individual"
    shared_cash: int = 0
    shared_inventory: list = field(default_factory=list)
    turn_timeout: int = 120
    allow_parallel_actions: bool = False


class LocalCoOpManager:
    def __init__(self):
        self.coop_state = CoOpState()
        self.round_counter: int = 0
        self.action_history: list[dict] = []

    def start_coop_session(self, player1_name: str, player1_type: str, player2_name: str, player2_type: str) -> CoOpState:
        self.coop_state.mode_enabled = True
        self.coop_state.player1_session = PlayerSession(
            player_id=1,
            character_name=player1_name,
            character_type=player1_type,
            turn_order=1,
        )
        self.coop_state.player2_session = PlayerSession(
            player_id=2,
            character_name=player2_name,
            character_type=player2_type,
            turn_order=2,
        )
        self.coop_state.current_turn = 1
        self.coop_state.shared_cash = 0
        self.coop_state.shared_inventory = []
        self.round_counter = 0
        self.action_history = []

        return self.coop_state

    def end_coop_session(self) -> None:
        self.coop_state.mode_enabled = False
        self.coop_state.player1_session = None
        self.coop_state.player2_session = None
        self.coop_state.current_turn = 1
        self.action_history = []

    def is_coop_enabled(self) -> bool:
        return self.coop_state.mode_enabled

    def get_current_player(self) -> Optional[PlayerSession]:
        if self.coop_state.current_turn == 1:
            return self.coop_state.player1_session
        return self.coop_state.player2_session

    def get_other_player(self) -> Optional[PlayerSession]:
        if self.coop_state.current_turn == 1:
            return self.coop_state.player2_session
        return self.coop_state.player1_session

    def switch_turn(self) -> None:
        if self.coop_state.turn_type == "individual":
            self.coop_state.current_turn = 2 if self.coop_state.current_turn == 1 else 1
        elif self.coop_state.turn_type == "round":
            self.round_counter += 1
            self.coop_state.current_turn = 1

    def set_turn_type(self, turn_type: str) -> bool:
        if turn_type in ["individual", "round", "simultaneous"]:
            self.coop_state.turn_type = turn_type
            return True
        return False

    def record_action(self, player_id: int, action: str, result: str, rewards: dict = None) -> None:
        self.action_history.append({
            "round": self.round_counter,
            "player_id": player_id,
            "action": action,
            "result": result,
            "rewards": rewards or {},
        })

    def get_shared_resources(self) -> dict:
        return {
            "cash": self.coop_state.shared_cash,
            "inventory": self.coop_state.shared_inventory,
            "player1": self.coop_state.player1_session.to_dict() if self.coop_state.player1_session else None,
            "player2": self.coop_state.player2_session.to_dict() if self.coop_state.player2_session else None,
        }

    def add_shared_cash(self, amount: int) -> None:
        self.coop_state.shared_cash += amount

    def split_shared_cash(self, ratio: tuple[int, int] = (50, 50)) -> tuple[int, int]:
        total = self.coop_state.shared_cash
        player1_share = int(total * ratio[0] / 100)
        player2_share = int(total * ratio[1] / 100)
        self.coop_state.shared_cash = 0
        return player1_share, player2_share

    def add_shared_item(self, item: dict) -> None:
        self.coop_state.shared_inventory.append(item)

    def remove_shared_item(self, item_name: str) -> bool:
        for i, item in enumerate(self.coop_state.shared_inventory):
            if item.get("name") == item_name:
                self.coop_state.shared_inventory.pop(i)
                return True
        return False

    def is_turn_timeout(self) -> bool:
        return False

    def get_turn_display(self) -> str:
        current = self.get_current_player()
        if not current:
            return "Unbekannte Runde"

        if self.coop_state.turn_type == "simultaneous":
            return "Gemeinsame Aktion"
        elif self.coop_state.turn_type == "round":
            return f"Runde {self.round_counter + 1} - {current.character_name}"
        else:
            return f"Spieler {current.player_id}: {current.character_name}"

    def get_action_summary(self, player_id: int) -> str:
        player_actions = [a for a in self.action_history if a["player_id"] == player_id]
        if not player_actions:
            return "Keine Aktionen in dieser Sitzung."

        summary = f"Aktionen von Spieler {player_id}:\n"
        for action in player_actions[-5:]:
            summary += f"  - {action['action']}: {action['result']}\n"
        return summary


class NetworkPlayManager:
    def __init__(self):
        self.server_socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None
        self.is_host: bool = False
        self.is_connected: bool = False
        self.game_state: dict = {}
        self.sync_interval: int = 5
        self.last_sync: int = 0

    def start_host(self, port: int = 5555) -> tuple[bool, str]:
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', port))
            self.server_socket.listen(1)
            self.is_host = True
            return True, f"Host gestartet auf Port {port}"
        except Exception as e:
            return False, f"Host-Fehler: {str(e)}"

    def connect_to_host(self, host: str, port: int = 5555) -> tuple[bool, str]:
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
            self.is_host = False
            self.is_connected = True
            return True, f"Verbunden mit {host}:{port}"
        except Exception as e:
            return False, f"Verbindungsfehler: {str(e)}"

    def wait_for_connection(self, timeout: int = 30) -> tuple[bool, str]:
        if not self.server_socket:
            return False, "Kein Server aktiv"

        self.server_socket.settimeout(timeout)
        try:
            self.client_socket, addr = self.server_socket.accept()
            self.is_connected = True
            return True, f"Spieler verbunden von {addr}"
        except Exception as e:
            return False, f"Timeout oder Fehler: {str(e)}"

    def accept_connection(self) -> tuple[bool, str]:
        if self.client_socket:
            self.is_connected = True
            return True, "Verbindung akzeptiert"
        return False, "Keine Verbindung"

    def disconnect(self) -> None:
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
        self.is_connected = False
        self.is_host = False

    def send_game_state(self, state: dict) -> bool:
        if not self.is_connected:
            return False

        try:
            import json
            data = json.dumps(state).encode('utf-8')
            self.client_socket.sendall(len(data).to_bytes(4, 'big'))
            self.client_socket.sendall(data)
            return True
        except Exception:
            return False

    def receive_game_state(self) -> Optional[dict]:
        if not self.is_connected:
            return None

        try:
            import json
            size_data = self.client_socket.recv(4)
            if not size_data:
                return None
            size = int.from_bytes(size_data, 'big')
            data = b''
            while len(data) < size:
                packet = self.client_socket.recv(size - len(data))
                if not packet:
                    return None
                data += packet
            return json.loads(data.decode('utf-8'))
        except Exception:
            return None

    def sync_state(self, local_state: dict) -> tuple[bool, Optional[dict]]:
        if self.is_host:
            success = self.send_game_state(local_state)
            return success, None
        else:
            remote_state = self.receive_game_state()
            return remote_state is not None, remote_state

    def is_network_active(self) -> bool:
        return self.is_connected

    def get_connection_info(self) -> dict:
        return {
            "is_host": self.is_host,
            "is_connected": self.is_connected,
        }


class MultiplayerMission:
    def __init__(self, mission_name: str):
        self.mission_name = mission_name
        self.player1_objectives: list[dict] = []
        self.player2_objectives: list[dict] = []
        self.shared_objectives: list[dict] = []
        self.completed_objectives: dict = {"player1": [], "player2": [], "shared": []}

    def add_objective(self, player: str, description: str, reward: dict) -> None:
        objective = {"description": description, "reward": reward, "completed": False}
        if player == "player1":
            self.player1_objectives.append(objective)
        elif player == "player2":
            self.player2_objectives.append(objective)
        else:
            self.shared_objectives.append(objective)

    def complete_objective(self, player: str, objective_index: int) -> bool:
        key = "player1" if player == "player1" else "player2" if player == "player2" else "shared"
        obj_list = getattr(self, f"{key}_objectives")

        if 0 <= objective_index < len(obj_list):
            obj_list[objective_index]["completed"] = True
            self.completed_objectives[key].append(objective_index)
            return True
        return False

    def is_complete(self) -> bool:
        all_complete = True
        for obj in self.player1_objectives + self.player2_objectives + self.shared_objectives:
            if not obj["completed"]:
                all_complete = False
                break
        return all_complete

    def get_progress(self) -> dict:
        total = len(self.player1_objectives) + len(self.player2_objectives) + len(self.shared_objectives)
        completed = sum(len(v) for v in self.completed_objectives.values())
        return {
            "total": total,
            "completed": completed,
            "percentage": (completed / total * 100) if total > 0 else 100
        }