"""
Unified Alert Listener

Listens to Redis `yield_data` channel, evaluates threshold breaches
using :class:`services.alert_service.AlertService`, and writes alerts
to SQLite via :class:`services.repository.AlertRepository`.

Run directly:
    python -m real_time_risk.services.services_alert_listener
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import datetime

import redis
import pandas as pd

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  

# Ensure project root in path
sys.path.append(str(Path(__file__).resolve().parents[2]))
CSV_PATH = Path(__file__).resolve().parents[1] / "yielddata.csv"

from domain.models import YieldPoint
from domain.thresholds import load_thresholds
from services.alert_service import AlertService
from services.repository import AlertRepository

_yield_curve_cache: dict[str, dict] = {}

def load_yield_curve_from_csv() -> None:
    """Read existing yielddata.csv into _yield_curve_cache."""
    if not CSV_PATH.exists():
        return
    df = pd.read_csv(CSV_PATH)
    for _, row in df.iterrows():
        tenor = str(row["tenor"])
        _yield_curve_cache[tenor] = {
            "value":         float(row["value"]),
            "valuationDate": str(row.get("valuationDate", "")),
            "currency":      str(row.get("currency", "")),
            "instrument":    str(row.get("instrument", "")),
            "settlementDate": str(row.get("settlementDate", "")),
            "period":         str(row.get("period", "")),
            "publishedAt":    str(row.get("publishedAt", "")),  # optional
        }

def get_current_yield_curve() -> dict[str, dict]:
    """Return a COPY of the most-recent OIS yield curve."""
    return _yield_curve_cache.copy()
	
def get_current_yield_curve_df() -> pd.DataFrame:
    """Bellekteki cache’i DataFrame olarak döndürür (dinamik kolonlar)."""
    if not _yield_curve_cache:
        return pd.DataFrame()

    df = (
        pd.DataFrame.from_dict(_yield_curve_cache, orient="index")
        .reset_index()
        .rename(columns={"index": "tenor"})
        .sort_values("tenor")
    )
    return df

def load_prev_values_from_csv() -> dict[str, float]:
    """yielddata.csv içindeki son değerleri tenor-bazlı dict olarak döndürür."""
    if not CSV_PATH.exists():
        return {}
    df = pd.read_csv(CSV_PATH).fillna("")
    return {
        str(row["tenor"]): float(row["value"])
        for _, row in df.iterrows()
        if str(row["value"]).strip() != ""
    }

# ------------------------------------------------------------------ #
def _build_engine() -> AlertService:
    repo = AlertRepository()
    thresholds = load_thresholds()
    # Buradaki parametrelerle davranışı kontrol edebilirsin:
    # - cooldown_sec: tetikten sonra bekleme (saniye)
    # - step_realert_bp: son alert büyüklüğü + N bp artmadan tekrar tetikleme (None = kapalı)
    # - auto_rearm: re-arm mekanizmasını genel olarak aç/kapat
    return AlertService(
        level_thresholds=thresholds,
        repo=repo,
        enable_level_rule=False,
        auto_rearm=True,
        cooldown_sec=60,       # örnek: 60 saniye
        step_realert_bp=0.0,  # örnek: +25 bp artınca yeniden tetikle (isteğe bağlı: 0, 10, None...)
    )

# ------------------------------------------------------------------ #
def start_listener(
    redis_host: str = "localhost",
    redis_port: int = 6379,
    channel: str = "yield_data",
) -> None:
    """Blocking listener loop."""
    engine = _build_engine()

    r = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(channel)

    prev_values: dict[str, float] = load_prev_values_from_csv()
    yieldata = pd.read_csv(CSV_PATH).fillna("")
    columns_ = ["value", "valuationDate","instrument","currency","period","settlementDate","tenor"]
    prev_yielddata = yieldata[columns_].to_dict('records')

    print(f"[alert_listener] 🎧 Subscribed to Redis channel '{channel}'")
    try:
        for raw in pubsub.listen():
            if raw.get("type") != "message":
                continue
            try:
                payload: dict = json.loads(raw["data"])
            except json.JSONDecodeError:
                print(f"[alert_listener] ⚠️ Malformed JSON – skipped: {raw['data']!r}")
                continue

            try:
                yp = YieldPoint(**payload)
                published_at = yp.publishedAt or datetime.utcnow().isoformat()
                _yield_curve_cache[yp.tenor] = {
                    "value":         yp.value,
                    "valuationDate": yp.valuationDate,
                    "instrument":    yp.instrument,
                    "currency":      yp.currency,
                    "period": "1D",
                    "settlementDate":"2D",
                    "source":        getattr(yp, "source", ""),
                    "publishedAt":   published_at,
                }
                # CSV/görsel tablo için DataFrame'e dönüştür
                try:
                    yield_data_df = get_current_yield_curve_df()
                    columns_ = ["value", "valuationDate","instrument","currency","period","settlementDate","tenor"]
                    last_yielddata = yield_data_df[columns_].to_dict('records')
                except Exception as exc:
                    logger.error("yielddata.csv güncellenirken hata: %s", exc)
                    last_yielddata = prev_yielddata  # en azından önceki ile devam
            except Exception as exc:
                print(f"[alert_listener] ⚠️ Invalid payload – {exc}")
                continue

            tenor = yp.tenor
            prev_value = prev_values.get(tenor)
            print({"Tenors": tenor, "Last Value": yp.value, "Previos Value Value": prev_value, "Change(bp)": (yp.value - (prev_value if prev_value is not None else yp.value)) * 10000})
            change1d = None
            if prev_value is not None:
                change1d = round((yp.value - prev_value) * 10000, 2)  # bp
            prev_values[tenor] = yp.value

            # Evaluate rules (guarded)
            try:
                engine.evaluate(yp, prev_yielddata, last_yielddata, change1d=change1d)
            except Exception as exc:
                logger.exception("[alert_listener] rule-engine error: %s", exc)
            finally:
                prev_yielddata = last_yielddata
    except KeyboardInterrupt:
        print("[alert_listener] ❌ Interrupted by user – shutting down.")
    finally:
        pubsub.close()
        r.close()

# ------------------------------------------------------------------ #
if __name__ == "__main__":
    start_listener()
