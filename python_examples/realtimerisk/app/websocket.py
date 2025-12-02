from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import os
from typing import Set, Optional
from contextlib import asynccontextmanager

# Use redis asyncio client (install: pip install redis)
try:
    import redis.asyncio as aioredis  # redis>=4.2
except Exception:  # fallback import name
    aioredis = None  # runtime error will explain

router = APIRouter()

class WSManager:
    def __init__(self) -> None:
        self.active: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self.active.add(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self.active.discard(ws)

    async def broadcast_text(self, text: str) -> None:
        async with self._lock:
            targets = list(self.active)
        for ws in targets:
            try:
                await ws.send_text(text)
            except Exception:
                self.disconnect(ws)

ws_manager_yield = WSManager()
ws_manager_alerts = WSManager()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
YIELD_CHANNEL = os.getenv("YIELD_CHANNEL", "yield_data")
ALERTS_CHANNEL = os.getenv("ALERTS_CHANNEL", "alerts")

@asynccontextmanager
async def redis_pubsub(channel: str):
    if aioredis is None:
        raise RuntimeError("redis package not installed. Run: pip install redis")
    r = aioredis.from_url(REDIS_URL, decode_responses=True)
    pubsub = r.pubsub()
    await pubsub.subscribe(channel)
    try:
        yield pubsub
    finally:
        try:
            await pubsub.unsubscribe(channel)
        finally:
            await r.close()

async def _pump_ws_from_redis(ws: WebSocket, manager: WSManager, channel: str):
    await manager.connect(ws)
    try:
        async with redis_pubsub(channel) as pubsub:
            async for m in pubsub.listen():
                if m.get("type") != "message":
                    continue
                data = m.get("data")
                await ws.send_text(data)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_text(f'{{"error":"{str(e)}"}}')
        except Exception:
            pass
    finally:
        manager.disconnect(ws)

@router.websocket("/ws/yield")
async def ws_yield(websocket: WebSocket):
    await _pump_ws_from_redis(websocket, ws_manager_yield, YIELD_CHANNEL)

@router.websocket("/ws/alerts")
async def ws_alerts(websocket: WebSocket):
    await _pump_ws_from_redis(websocket, ws_manager_alerts, ALERTS_CHANNEL)
