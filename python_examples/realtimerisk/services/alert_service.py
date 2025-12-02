"""
Alert evaluation, Redis snapshot, Redis->WebSocket publish.

Akış:
1) Her yeni yield mesajında alarm kurallarını değerlendirir (level + change/bp),
2) Önceki snapshot'ı Redis’ten okur, tam portföy PV farkını hesaplar,
3) Snapshot'ı günceller,
4) Telegram ve DB'ye yazar,
5) Ayrıca Redis 'alerts' kanalına JSON publish eder (UI için WebSocket ile bridge edilir).
"""
from __future__ import annotations

import copy
import json
import math
from datetime import date, datetime
from typing import Callable

import redis
import redis.asyncio as aioredis

from domain.models import YieldPoint
from domain.thresholds import DEFAULT_THRESHOLDS
from services.telegram_notifier import TelegramNotifier
from app.settings import settings
from rhoova_folder.portfolio import get_rhoova_pv

# ────────────────────────────────────────────────────────────────
# Redis bağlantıları ve sabitler
# ────────────────────────────────────────────────────────────────
_r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
SNAP_KEY = "yield_snapshot"

# Telegram notifier (fallback: print)
notifier = TelegramNotifier(token=settings.telegram_token, chat_id=settings.telegram_chat_id)

# Portföy şablonu (settings üzerinden geliyor)
PORTFOLIO_TEMPLATE = settings.portfolio

try:
    from services.repository import AlertRepository
except ModuleNotFoundError:
    AlertRepository = None  # type: ignore


# --- Safe PV helpers -----------------------------------------------------------
def _to_float_safe(val):
    """Return float or None for None/''/NaN/inf/invalid."""
    if val is None:
        return None
    try:
        f = float(val)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return f

def _get_pv_safe(portf):
    """Return (pv, error_str). If PV compute fails or invalid, returns (None, reason)."""
    try:
        pv = get_rhoova_pv(portf, None)
        pvf = _to_float_safe(pv)
        if pvf is None:
            return None, "rhoova_pv is None/NaN"
        return pvf, None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"
# ------------------------------------------------------------------------------


class AlertService:
    """Evaluates yield alerts and dispatches notifications.

    Parameters
    ----------
    level_thresholds : dict[str, float], optional
        Tenor‑bazlı "level" eşiği (yield < threshold) kullanmak için.
    change_threshold_bp : float, default 50.0
        Günlük değişim (bp) eşiği.
    enable_level_rule : bool, default True
        Level rule aktif/pasif.
    auto_rearm : bool, default False
        Kilit (triggered) bir kez tetiklendikten sonra yeniden tetiklenmeye izin ver.
    cooldown_sec : int, default 180
        Tetik sonrası en az bu kadar saniye geçmeden aynı tenor tekrar tetiklenmez.
    step_realert_bp : float | None, default None
        Eğer ayarlıysa, son alert büyüklüğüne göre +N bp daha büyük hareket olursa kilit kaldırılır.
    """

    def __init__(
        self,
        *,
        level_thresholds: dict[str, float] | None = None,
        change_threshold_bp: float = 50.0,
        notifier: Callable[[str], None] | None = None,
        repo: AlertRepository | None = None,
        enable_level_rule: bool = True,
        auto_rearm: bool = False,
        cooldown_sec: int = 180,
        step_realert_bp: float | None = None,
    ) -> None:
        self._level_thr = level_thresholds or DEFAULT_THRESHOLDS
        self._change_thr = change_threshold_bp
        self._notify = notifier or print
        self._repo = repo
        self._enable_level_rule = enable_level_rule

        # Re-arm / kilit kontrolü
        self._auto_rearm = auto_rearm
        self._cooldown_sec = cooldown_sec
        self._step_realert_bp = step_realert_bp
        self._last_alert_ts: dict[tuple[str, str], datetime] = {}
        self._last_alert_abs: dict[str, float] = {}

        self._triggered: dict[tuple[str, str], bool] = {}
        self._last_reset_date: date = date.today()  # günlük reset takibi

    # ──────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────
    def evaluate(
        self,
        yp: YieldPoint,
        prev_yielddata: list[dict],
        last_yielddata: list[dict],
        *,
        change1d: float | None = None,
    ) -> None:
        """Her yeni veri noktasını değerlendir; gerekirse alarm tetikle."""

        # Günlük reset
        today = date.today()
        if today != self._last_reset_date:
            self.reset()
            self._last_reset_date = today

        tenor = yp.tenor

        # --- Re-arm (opsiyonel): cooldown / histerezis / progresif adım ---
        if self._auto_rearm and self._triggered.get((tenor, "chg")):
            # Cooldown
            ts = self._last_alert_ts.get((tenor, "chg"))
            if ts and (datetime.utcnow() - ts).total_seconds() >= self._cooldown_sec:
                self._triggered.pop((tenor, "chg"), None)
            # Histerezis (band içine dönüş)
            elif change1d is not None and abs(change1d) < 0.6 * self._change_thr:
                self._triggered.pop((tenor, "chg"), None)
            # Progressive re-alert (büyüklük artışı)
            elif change1d is not None and self._step_realert_bp is not None:
                last_abs = self._last_alert_abs.get(tenor, 0.0)
                if abs(change1d) >= last_abs + self._step_realert_bp:
                    self._triggered.pop((tenor, "chg"), None)

        # ── Level Rule ─────────────────────────────────────────
        if self._enable_level_rule:
            lvl_thr = self._level_thr.get(tenor)
            if (
                lvl_thr is not None
                and yp.value < lvl_thr
                and not self._triggered.get((tenor, "lvl"), False)
            ):
                self._raise(
                    f"⚠️ {tenor} yield {yp.value:.4%} below {lvl_thr:.4%}",
                    tenor,
                    "lvl",
                    change1d,
                    prev_pv=None,
                    last_pv=None,
                )

        # ── Change Rule (bp threshold) ─────────────────────────
        if (
            change1d is None
            or abs(change1d) <= self._change_thr
            or self._triggered.get((tenor, "chg"), False)
        ):
            return  # threshold aşılmadı veya zaten tetiklenmiş

        # 1️⃣ Önceki snapshot'ı çek
        prev_snapshot_json = _r.get(SNAP_KEY)
        if not prev_snapshot_json:
            # Snapshot yok → sadece güncel snapshot'ı kur, alarm yok
            self._store_snapshot(last_yielddata)
            return

        prev_snapshot = json.loads(prev_snapshot_json)
        prev_pv = _to_float_safe(prev_snapshot.get("portfolioPV"))  # önceki tam PV
        prev_pv_err = prev_snapshot.get("pvError")  # önceki PV hata mesajı (varsa)
        prev_yielddata_snap: list[dict] = prev_snapshot["yieldData"]

        # 2️⃣ İzole tenor update (opsiyonel – istersen tekrar aktifleştir)
        isolated_yield = copy.deepcopy(prev_yielddata_snap)
        updated = False
        for row in isolated_yield:
            if row["tenor"] == yp.tenor:
                row["value"] = yp.value
                updated = True
                break
        if not updated:
            isolated_yield.append(
                {
                    "tenor": yp.tenor,
                    "value": yp.value,
                    "valuationDate": yp.valuationDate,
                    "instrument": yp.instrument,
                    "currency": yp.currency,
                    "period": "1D",
                    "settlementDate": "2D",
                }
            )

        # 3️⃣ Tam yeni PV (tüm güncellemeler ile)
        full_portf = copy.deepcopy(PORTFOLIO_TEMPLATE)
        full_portf["yieldData"] = last_yielddata
        last_pv, last_pv_err = _get_pv_safe(full_portf)

        # 4️⃣ Snapshot'ı Redis'e güncelle (pvError da sakla)
        self._store_snapshot(last_yielddata, last_pv, pv_error=last_pv_err)

        # 5️⃣ Alarm gönder (PV metni güvenli)
        direction_emoji = "🔺" if (change1d or 0) > 0 else "🔻"
        prev_txt = f"{prev_pv:.0f}" if prev_pv is not None else "—"
        last_txt = f"{last_pv:.0f}" if last_pv is not None else "—"

        if prev_pv is not None and last_pv is not None:
            delta_pv_num = (last_pv - prev_pv)
            dpv_txt = f"{delta_pv_num:.0f}"
            pv_text = f"(PV prev={prev_txt}, last={last_txt}, ΔPV={dpv_txt})"
            err_text = ""
        else:
            err = last_pv_err or prev_pv_err
            delta_pv_num = None
            dpv_txt = "—"
            pv_text = f"(PV prev={prev_txt}, last={last_txt}, ΔPV=—)"
            err_text = f" [PV ERR: {err}]" if err else ""

        # Konsola net PV logu
        print(f"[pv] prev={prev_txt}, last={last_txt}, Δ={dpv_txt}")

        # Zaman damgaları (cooldown ve progressive için)
        self._last_alert_ts[(tenor, "chg")] = datetime.utcnow()
        self._last_alert_abs[tenor] = abs(change1d or 0.0)

        self._raise(
            f"⚠️ {direction_emoji} {tenor} moved {change1d:+.1f} bp {pv_text}{err_text}",
            tenor,
            "chg",
            change1d,
            prev_pv,
            last_pv,
            delta_pv_num=delta_pv_num,
            error=(last_pv_err or prev_pv_err),
        )

    # ──────────────────────────────────────────────────────────
    def reset(self) -> None:
        """Clear triggered flags so rules may fire again."""
        self._triggered.clear()

    # ──────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────
    def _store_snapshot(self, yielddata: list[dict], pv: float | None = None, pv_error: str | None = None) -> None:
        """Snap'ı Redis'e kaydet. `pv` verilmezse güvenli hesapla ve hatayı sakla."""
        if pv is None:
            portf = copy.deepcopy(PORTFOLIO_TEMPLATE)
            portf["yieldData"] = yielddata
            pv, pv_error = _get_pv_safe(portf)

        print(f"[init-pv] İlk snapshot kuruluyor → PV={pv} (hata={pv_error})")
        snapshot = {
            "yieldData": yielddata,
            "portfolioPV": pv,
            "pvError": pv_error,
            "ts": datetime.utcnow().isoformat(timespec="seconds"),
        }
        _r.set(SNAP_KEY, json.dumps(snapshot))
        if pv_error:
            print(f"[rhoova] PV error: {pv_error}")

    def _publish_alert_to_redis(self, msg: str, tenor: str, delta_pv: float | None, error: str | None = None) -> None:
        """Publish alert as JSON to Redis 'alerts' channel."""
        payload = {
            "type": "alert",
            "text": msg,
            "tenor": tenor,
            "ts": datetime.utcnow().timestamp(),
        }
        if delta_pv is not None:
            try:
                payload["deltaPV"] = round(float(delta_pv), 0)
            except Exception:
                pass
        if error:
            payload["error"] = error
        _r.publish("alerts", json.dumps(payload))

    def _raise(
        self,
        msg: str,
        tenor: str,
        rule: str,
        change1d: float | None,
        prev_pv: float | None,
        last_pv: float | None,
        *,
        delta_pv_num: float | None = None,
        error: str | None = None,
    ) -> None:
        """Send notification and persist to DB, then publish to Redis for WS/UI."""
        self._notify(msg)
        self._triggered[(tenor, rule)] = True
        notifier.send_message(msg)

        if self._repo is not None and prev_pv is not None and last_pv is not None:
            self._repo.log_alert(
                timestamp=datetime.utcnow().isoformat(timespec="seconds"),
                tenor=tenor,
                change1d=round((last_pv - prev_pv), 2),
                previous_pv=round(prev_pv, 2),
                last_pv=round(last_pv, 2),
                message=msg,
            )

        # Redis'e publish (WS bridge için)
        self._publish_alert_to_redis(msg, tenor, delta_pv_num, error=error)


# ────────────────────────────────────────────────────────────────
# WebSocket endpoint (opsiyonel – bu dosyada kalabilir)
# ────────────────────────────────────────────────────────────────
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

ws_router = APIRouter()
_r_async = aioredis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

@ws_router.websocket("/ws/alerts")
async def ws_alerts(websocket: WebSocket):
    """Bridge Redis 'alerts' channel to WebSocket clients."""
    await websocket.accept()
    pubsub = _r_async.pubsub()
    await pubsub.subscribe("alerts")
    try:
        async for message in pubsub.listen():
            if message.get("type") != "message":
                continue
            data = message.get("data")  # JSON string (alert publish ediyor)
            await websocket.send_text(data)
    except WebSocketDisconnect:
        pass
    finally:
        try:
            await pubsub.unsubscribe("alerts")
        finally:
            await pubsub.close()
