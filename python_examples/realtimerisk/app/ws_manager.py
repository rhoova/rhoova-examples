# Auto-generated WebSocket manager
from typing import Set
try:
    from starlette.websockets import WebSocket, WebSocketState
except Exception:  # fallback types
    WebSocket = object
    class WebSocketState:
        DISCONNECTED = object()

class WSManager:
    def __init__(self) -> None:
        self.active: Set[WebSocket] = set()

    async def connect(self, ws: WebSocket) -> None:
        try:
            await ws.accept()
        except Exception:
            pass
        self.active.add(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self.active.discard(ws)

    async def safe_send_json(self, ws: WebSocket, data) -> None:
        try:
            if getattr(ws, "application_state", None) == WebSocketState.DISCONNECTED: return
            if getattr(ws, "client_state", None) == WebSocketState.DISCONNECTED: return
        except Exception:
            pass
        try:
            await ws.send_json(data)
        except Exception:
            pass

    async def broadcast(self, data) -> None:
        dead = []
        for ws in list(self.active):
            try:
                await self.safe_send_json(ws, data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

ws_manager = WSManager()
