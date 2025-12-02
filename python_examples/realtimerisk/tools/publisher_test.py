"""Quick Redis publisher to test /ws/alerts broadcast."""
import asyncio, json, os
from redis.asyncio import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CHANNEL   = os.getenv("REDIS_CHANNEL", "yield_data")

async def main():
    r = Redis.from_url(REDIS_URL, decode_responses=True)
    payloads = [
        {"type":"tick","tenor":"2W","value":0.445,"ts":"2025-08-25T12:05:00Z"},
        {"type":"tick","tenor":"2M","value":0.448,"ts":"2025-08-25T12:05:01Z"},
        {"type":"tick","tenor":"1Y","value":0.512,"ts":"2025-08-25T12:05:02Z"},
    ]
    for p in payloads:
        await r.publish(CHANNEL, json.dumps(p))
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())
