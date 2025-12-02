# services/telegram_notifier.py
from __future__ import annotations
import requests

class TelegramNotifier:
    """Lightweight Telegram sender.

    Args:
        token: Bot token
        chat_id: Destination chat ID
    """
    def __init__(self, token: str, chat_id: str) -> None:
        self.token = token
        self.chat_id = chat_id

    def send_message(self, message: str) -> None:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": message, "parse_mode": "HTML"}
        try:
            resp = requests.post(url, data=payload, timeout=5)
            if resp.status_code != 200:
                print(f"[Telegram] Error: {resp.status_code} - {resp.text}")
        except requests.RequestException as e:
            print(f"[Telegram] Exception: {e}")
