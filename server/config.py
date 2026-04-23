import os


SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8000"))

WORLD_STATE_FILE = "data/server/world_state.json"
PLAYER_DATA_DIR = "data/server/players"

BROADCAST_INTERVAL = 5.0
PLAYER_TIMEOUT = 300

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")