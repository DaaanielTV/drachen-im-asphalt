from dataclasses import dataclass
from typing import Optional, Any
import time


@dataclass
class DebugCommand:
    name: str
    description: str
    aliases: list[str]
    category: str


class DebugTools:
    COMMANDS = [
        DebugCommand("spawn_item", "Gegenstand erzeugen", ["spawn", "add"], "Items"),
        DebugCommand("set_stat", "Stat ändern", ["stat", "set"], "Stats"),
        DebugCommand("complete_mission", "Mission abschließen", ["cmpl", "done"], "Missions"),
        DebugCommand("unlock_achievement", "Achievement freischalten", ["achieve", "unlock"], "Achievements"),
        DebugCommand("set_level", "Level setzen", ["lvl", "level"], "Stats"),
        DebugCommand("add_cash", "Cash hinzufügen", ["money", "cash"], "Stats"),
        DebugCommand("set_wanted", "Wanted Level setzen", ["wanted"], "Stats"),
        DebugCommand("god_mode", "Unverwundbarkeit", ["god"], "Combat"),
        DebugCommand("reveal_map", "Karte aufdecken", ["map"], "Exploration"),
        DebugCommand("skip_day", "Tag überspringen", ["day"], "Time"),
        DebugCommand("set_chapter", "Kapitel setzen", ["chapter"], "Story"),
        DebugCommand("teleport", "Teleportieren", ["tp"], "Exploration"),
        DebugCommand("unlock_all", "Alles freischalten", ["all", "full"], "Debug"),
        DebugCommand("reset_progress", "Fortschritt zurücksetzen", ["reset"], "Debug"),
        DebugCommand("spawn_enemy", "Gegner spawnen", ["enemy", "spawn_enemy"], "Combat"),
        DebugCommand("complete_quest", "Quest abschließen", ["quest"], "Missions"),
        DebugCommand("show_stats", "Statistiken anzeigen", ["stats", "statistics"], "Debug"),
        DebugCommand("time_scale", "Zeit-Skala ändern", ["timescale", "speed"], "Time"),
        DebugCommand("print_state", "Zustand ausgeben", ["state", "dump"], "Debug"),
        DebugCommand("test_combat", "Kampf testen", ["combat", "fight"], "Combat"),
    ]

    def __init__(self):
        self.enabled: bool = False
        self.command_history: list[dict] = []
        self.cheats_enabled: dict[str, bool] = {
            "god_mode": False,
            "infinite_stamina": False,
            "infinite_cash": False,
            "no_wanted": False,
        }
        self.debug_log: list[str] = []
        self.test_mode: bool = False

    def enable(self) -> None:
        self.enabled = True
        self.log("Debug-Modus aktiviert")

    def disable(self) -> None:
        self.enabled = False
        self.log("Debug-Modus deaktiviert")

    def is_enabled(self) -> bool:
        return self.enabled

    def log(self, message: str) -> None:
        timestamp = time.strftime("%H:%M:%S")
        self.debug_log.append(f"[{timestamp}] {message}")

    def get_log(self, limit: int = 50) -> list[str]:
        return self.debug_log[-limit:]

    def execute_command(self, command: str, args: list[str], protagonist) -> tuple[bool, str]:
        if not self.enabled:
            return False, "Debug-Modus ist nicht aktiviert."

        self.log(f"Befehl ausgeführt: {command} {' '.join(args)}")

        cmd_lower = command.lower()
        for cmd in self.COMMANDS:
            if cmd.name == cmd_lower or cmd_lower in cmd.aliases:
                return self._handle_command(cmd.name, args, protagonist)

        return False, f"Unbekannter Befehl: {command}"

    def _handle_command(self, cmd_name: str, args: list[str], protagonist) -> tuple[bool, str]:
        if cmd_name == "add_cash":
            amount = int(args[0]) if args else 1000
            protagonist.cash += amount
            return True, f"${amount} hinzugefügt. Neuer Kontostand: ${protagonist.cash}"

        elif cmd_name == "set_level":
            level = int(args[0]) if args else 1
            protagonist.level = max(1, level)
            return True, f"Level auf {level} gesetzt"

        elif cmd_name == "set_wanted":
            wanted = int(args[0]) if args else 0
            protagonist.wanted_level = max(0, min(5, wanted))
            return True, f"Wanted Level auf {protagonist.wanted_level} gesetzt"

        elif cmd_name == "god_mode":
            self.cheats_enabled["god_mode"] = not self.cheats_enabled["god_mode"]
            status = "aktiviert" if self.cheats_enabled["god_mode"] else "deaktiviert"
            return True, f"God Mode {status}"

        elif cmd_name == "set_chapter":
            chapter = int(args[0]) if args else 1
            protagonist.chapter = max(1, min(6, chapter))
            return True, f"Kapitel auf {chapter} gesetzt"

        elif cmd_name == "skip_day":
            protagonist.days += 1
            protagonist.district_manager.advance_time(24)
            return True, f"Tag {protagonist.days} erreicht"

        elif cmd_name == "show_stats":
            stats = f"""[DEBUG] Statistiken:
  Level: {protagonist.level}
  Cash: ${protagonist.cash}
  Tage: {protagonist.days}
  Kapitel: {protagonist.chapter}
  Ausdauer: {protagonist.stamina}
  Wanted: {protagonist.wanted_level}
  Reputation: {protagonist.reputation}
  Partner-Trust: {protagonist.partner_trust}"""
            return True, stats

        elif cmd_name == "spawn_item":
            item_name = args[0] if args else "Pistole"
            from src.items.weapon import Weapon
            weapon = Weapon(
                name=item_name,
                cost=100,
                damage_increase=10,
                illegal_status=True
            )
            protagonist.inventory.append(weapon)
            return True, f"{item_name} zum Inventar hinzugefügt"

        elif cmd_name == "complete_mission":
            mission_name = args[0] if args else "Test Mission"
            if hasattr(protagonist, "story_flags"):
                if "completed_missions" not in protagonist.story_flags:
                    protagonist.story_flags["completed_missions"] = []
                protagonist.story_flags["completed_missions"].append(mission_name)
            return True, f"Mission '{mission_name}' abgeschlossen"

        elif cmd_name == "unlock_achievement":
            achievement_id = args[0] if args else "first_crime"
            if hasattr(protagonist, "achievement_manager"):
                protagonist.achievement_manager.unlock(achievement_id, protagonist.days)
            return True, f"Achievement '{achievement_id}' freigeschaltet"

        elif cmd_name == "unlock_all":
            if hasattr(protagonist, "achievement_manager"):
                for ach_id in protagonist.achievement_manager.achievements:
                    protagonist.achievement_manager.unlock(ach_id, protagonist.days)
            if hasattr(protagonist, "story_flags"):
                for key in protagonist.story_flags:
                    if isinstance(protagonist.story_flags[key], bool):
                        protagonist.story_flags[key] = True
            return True, "Alle Achievements und Flags freigeschaltet"

        elif cmd_name == "reset_progress":
            protagonist.level = 1
            protagonist.cash = 500
            protagonist.days = 0
            protagonist.wanted_level = 0
            protagonist.reputation = 0
            protagonist.stamina = 30
            protagonist.dragon_defeated = False
            return True, "Fortschritt zurückgesetzt"

        elif cmd_name == "teleport":
            district = args[0] if args else "Ocean Beach"
            if district in protagonist.district_manager.districts:
                protagonist.current_district_context = district
                return True, f"Nach {district} teleportiert"
            return False, f"Distrikt '{district}' nicht gefunden"

        elif cmd_name == "print_state":
            import json
            state = {
                "name": protagonist.name,
                "type": protagonist.character_type,
                "level": protagonist.level,
                "cash": protagonist.cash,
                "days": protagonist.days,
                "chapter": protagonist.chapter,
                "story_flags": protagonist.story_flags,
            }
            return True, json.dumps(state, indent=2)

        return False, f"Befehl '{cmd_name}' nicht implementiert"

    def get_available_commands(self) -> list[DebugCommand]:
        return self.COMMANDS

    def get_command_by_name(self, name: str) -> Optional[DebugCommand]:
        for cmd in self.COMMANDS:
            if cmd.name == name:
                return cmd
        return None

    def is_cheat_enabled(self, cheat_name: str) -> bool:
        return self.cheats_enabled.get(cheat_name, False)

    def apply_cheats(self, protagonist) -> None:
        if self.cheats_enabled.get("god_mode"):
            protagonist.wanted_level = 0

        if self.cheats_enabled.get("infinite_stamina"):
            protagonist.stamina = protagonist.level * 25

        if self.cheats_enabled.get("no_wanted"):
            protagonist.wanted_level = 0

    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "cheats_enabled": self.cheats_enabled,
            "debug_log": self.debug_log[-100:],
        }

    def load_from_dict(self, data: dict) -> None:
        if "enabled" in data:
            self.enabled = data["enabled"]
        if "cheats_enabled" in data:
            self.cheats_enabled.update(data["cheats_enabled"])
        if "debug_log" in data:
            self.debug_log = data["debug_log"]


class GameTestRunner:
    def __init__(self):
        self.test_results: list[dict] = []
        self.total_tests: int = 0
        self.passed_tests: int = 0

    def run_test(self, test_name: str, test_func: callable) -> bool:
        self.total_tests += 1
        try:
            result = test_func()
            if result:
                self.passed_tests += 1
                self.test_results.append({"name": test_name, "passed": True, "error": None})
                return True
            else:
                self.test_results.append({"name": test_name, "passed": False, "error": "Test failed"})
                return False
        except Exception as e:
            self.test_results.append({"name": test_name, "passed": False, "error": str(e)})
            return False

    def get_summary(self) -> str:
        return f"Tests: {self.passed_tests}/{self.total_tests} bestanden"

    def get_results(self) -> list[dict]:
        return self.test_results