"""Smoke test for :class:`services.alert_service.AlertService`."""
from services.alert_service import AlertService
from domain.models import YieldPoint


def test_alert_triggers(monkeypatch):  # noqa: D103
    received = {}

    def _fake_notifier(msg: str) -> None:
        received["msg"] = msg

    svc = AlertService(notifier=_fake_notifier, thresholds={"5Y": 0.30})
    yp = YieldPoint(
        tenor="5Y",
        value=0.28,
        valuationDate="2025-02-25",
        publishedAt="2025-06-27T19:00:00Z",
    )
    svc.evaluate(yp)
    assert "5Y" in received["msg"]
