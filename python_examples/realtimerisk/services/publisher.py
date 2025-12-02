"""
CSV tabanlı canlı yayıncı
-------------------------
* yielddata.csv dosyasını belleğe alır.
* Satırları sonsuz döngüde sırayla gönderir.
* Her gönderimde:
    - value alanına ±(variation_pct) kadar *rastgele* sapma uygular.
    - publishedAt alanını UTC 'now' ile günceller.
"""
import asyncio
import json
import random
from datetime import datetime

import pandas as pd
import redis.asyncio as redis  # decode_responses used below

from app.settings import settings

# ============================================================================
CSV_PATH = "yielddata.csv"          # Proje kökünde olmalı
variation_pct = 0.03                # ±3 %’e kadar rastgele oynama
# ============================================================================


async def run() -> None:
    df = pd.read_csv(CSV_PATH)
    if df.empty:
        raise RuntimeError(f"📂 {CSV_PATH} boş!")

    r = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        idx = 0
        while True:
            row = df.iloc[idx]

            # --- Rastgele varyasyon -------------------------------------------------
            base_val = float(row["value"])
            jitter = 1 + random.uniform(-variation_pct, variation_pct)
            new_val = round(base_val * jitter, 6)

            # --- Mesajı oluştur -----------------------------------------------------
            msg = {
                "tenor": row["tenor"],
                "value": new_val,
                "instrument": row.get("instrument", "OIS"),
                "currency": row.get("currency", "TRY"),
                "valuationDate": row.get("valuationDate", "2025-02-25"),
                "publishedAt": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                "source": "csv+noise",
            }

            await r.publish("yield_data", json.dumps(msg))
            print(f"✅ Published ({idx + 1}/{len(df)}):", msg)

            # --- Sonraki satıra geç (sonsuz döngü) ----------------------------------
            idx = (idx + 1) % len(df)
            await asyncio.sleep(settings.refresh_sec)
    finally:
        await r.close()


if __name__ == "__main__":
    asyncio.run(run())

async def _connect(url: str):
    return redis.from_url(url, decode_responses=True)
