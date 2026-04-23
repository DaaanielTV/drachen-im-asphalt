import asyncio
import uuid
from client.connection import GameClient


class TerminalUI:
    def __init__(self):
        self.client = GameClient()
        self.player_id = str(uuid.uuid4())[:8]
        self.game_state = {}
        self.world_state = {}
        self.players = []
        self.message_queue = []
        self._setup_handlers()

    def _setup_handlers(self):
        self.client.register_handler("welcome", self._on_welcome)
        self.client.register_handler("character_created", self._on_character_created)
        self.client.register_handler("command_result", self._on_command_result)
        self.client.register_handler("player_list", self._on_player_list)
        self.client.register_handler("world_state", self._on_world_state)
        self.client.register_handler("game_state", self._on_game_state)
        self.client.register_handler("chat", self._on_chat)
        self.client.register_handler("district_update", self._on_district_update)
        self.client.register_handler("error", self._on_error)
        self.client.register_handler("pong", self._on_pong)

    async def _on_welcome(self, msg):
        print(f"\n>>> {msg['message']} (ID: {msg['player_id']})")

    async def _on_character_created(self, msg):
        self.game_state = msg.get("game_state", {})
        print(f"\n>>> Charakter erstellt: {msg['message']}")
        self._print_status()

    async def _on_command_result(self, msg):
        if msg.get("success"):
            print(f"\n>>> {msg.get('message', 'Befehl ausgefuehrt')}")
            if "game_state" in msg:
                self.game_state = msg["game_state"]
            if "updates" in msg and msg["updates"].get("type") == "quit":
                print("\n>>> Spiel beendet. Auf Wiedersehen!")
                await self.client.disconnect()
        else:
            print(f"\n>>> FEHLER: {msg.get('message')}")

    async def _on_player_list(self, msg):
        self.players = msg.get("players", [])
        print(f"\n>>> Spieler online: {len(self.players)}")
        for p in self.players:
            print(f"   - {p['name']} ({p['character_type']}) in {p['current_district']}")

    async def _on_world_state(self, msg):
        self.world_state = msg.get("data", {})
        print(f"\n>>> Welt aktualisiert: Kapitel {self.world_state.get('chapter')}")

    async def _on_game_state(self, msg):
        self.game_state = msg.get("data", {})
        self._print_status()

    async def _on_chat(self, msg):
        print(f"\n[CHAT] {msg['player_name']}: {msg['message']}")

    async def _on_district_update(self, msg):
        district = msg.get("district")
        players = msg.get("players", [])
        print(f"\n>>> {district}: Spieler vor Ort: {', '.join(players) if players else 'Nur du'}")

    async def _on_error(self, msg):
        print(f"\n>>> FEHLER: {msg.get('message')}")

    async def _on_pong(self, msg):
        print(f"\n>>> Ping bestaetigt")

    def _print_status(self):
        if not self.game_state:
            return
        print(f"\n=== STATUS ===")
        print(f"Name: {self.game_state.get('name', 'N/A')}")
        print(f"Level: {self.game_state.get('level', 1)}")
        print(f"Cash: ${self.game_state.get('cash', 0)}")
        print(f"Ausdauer: {self.game_state.get('stamina', 0)}")
        print(f"Tage: {self.game_state.get('days', 0)}")
        print(f"Wanted: {self.game_state.get('wanted_level', 0)}")
        print(f"Reputation: {self.game_state.get('reputation', 0)}")
        print(f"Stadtteil: {self.game_state.get('current_district', 'N/A')}")
        print(f"Zeit: {self.game_state.get('time', 'N/A')}")
        print(f"=============\n")

    async def create_character_menu(self):
        print("\n=== CHARAKTER ERSTELLEN ===")
        name = input("Name: ").strip()
        if not name:
            print("Name erforderlich!")
            return

        print("Waehle Charakter:")
        print("1. Jason (mehr Kampf)")
        print("2. Lucia (mehr Heimlichkeit)")
        choice = input("> ").strip()

        char_type = "jason" if choice == "1" else "lucia"
        await self.client.create_character(name, char_type)

    async def command_menu(self):
        if not self.game_state:
            print("\nKein Charakter erstellt. Bitte erstelle zuerst einen Charakter.")
            await self.create_character_menu()
            return

        print("\n=== BEFEHL ===")
        print("1. Erkunden (Stadt)")
        print("2. Erkunden (bestimmter Stadtteil)")
        print("3. Ausruhen")
        print("4. Status")
        print("5. Inventar")
        print("6. Missionen")
        print("7. Erfolge")
        print("8. Kapitel")
        print("9. Chat")
        print("0. Welt synchronisieren")
        print("q. Beenden")
        choice = input("> ").strip()

        if choice == "1":
            await self.client.send_command("explore")
        elif choice == "2":
            print("Stadtteile: Ocean Beach, Washington Beach, Vice Point, Viceport, Downtown, Little Haiti, Starfish Island, Everglades, Vice Keys")
            district = input("Stadtteil: ").strip()
            await self.client.send_command("explore", district_name=district)
        elif choice == "3":
            await self.client.send_command("rest")
        elif choice == "4":
            await self.client.send_command("status")
        elif choice == "5":
            await self.client.send_command("inventory")
        elif choice == "6":
            await self.client.send_command("mission")
        elif choice == "7":
            await self.client.send_command("achievements")
        elif choice == "8":
            await self.client.send_command("chapter")
        elif choice == "9":
            msg = input("Nachricht: ").strip()
            if msg:
                await self.client.send_chat(msg)
        elif choice == "0":
            await self.client.send("sync", {})
        elif choice.lower() == "q":
            await self.client.send_command("quit")

    async def run(self):
        print("=== DRACHEN IM ASPHALT - MULTIPLAYER ===")
        print(f"Verbindung zu Server: {self.client.server_url}")
        print(f"Deine ID: {self.player_id}")

        connected = await self.client.connect(self.player_id)
        if not connected:
            print("Verbindung fehlgeschlagen!")
            return

        print("Verbunden! Warte auf Willkommensnachricht...")
        await asyncio.sleep(1)

        asyncio.create_task(self.client.listen())

        while self.client.running:
            if not self.game_state:
                await self.create_character_menu()
            else:
                await self.command_menu()

            await asyncio.sleep(0.5)


async def main():
    ui = TerminalUI()
    await ui.run()


if __name__ == "__main__":
    asyncio.run(main())