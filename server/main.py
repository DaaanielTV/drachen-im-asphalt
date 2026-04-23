from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import uuid
from typing import Callable

from server.connection_manager import ConnectionManager
from server.dispatcher import CommandDispatcher
from server.sync import StateSynchronizer
from server.presence import PresenceManager


app = FastAPI(title="Drachen im Asphalt - Multiplayer Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connection_manager = ConnectionManager()
state_synchronizer = StateSynchronizer()
presence_manager = PresenceManager(connection_manager)
dispatcher = CommandDispatcher(
    connection_manager,
    state_synchronizer,
    presence_manager
)


@app.get("/")
async def root():
    return {"message": "Drachen im Asphalt Multiplayer Server", "version": "0.1.0"}


@app.get("/status")
async def server_status():
    return {
        "players_online": connection_manager.get_player_count(),
        "players": presence_manager.get_all_player_info()
    }


@app.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: str):
    await connection_manager.connect(websocket, player_id)
    presence_manager.player_joined(player_id)
    state_synchronizer.notify_player_join(player_id)

    try:
        await websocket.send_json({
            "type": "welcome",
            "player_id": player_id,
            "message": "Willkommen bei Drachen im Asphalt!"
        })

        world_state = state_synchronizer.get_world_state()
        await websocket.send_json({
            "type": "world_state",
            "data": world_state
        })

        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await dispatcher.dispatch(player_id, message)
            except json.JSONDecodeError:
                await connection_manager.send_to_player(player_id, {
                    "type": "error",
                    "message": "Ungueltiges JSON-Format"
                })

    except WebSocketDisconnect:
        connection_manager.disconnect(player_id)
        presence_manager.player_left(player_id)
        state_synchronizer.notify_player_leave(player_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)