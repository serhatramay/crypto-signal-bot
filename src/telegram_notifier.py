import requests
from datetime import datetime, timezone
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, MAX_SCORE


def send_message(text: str) -> bool:
    """Telegram'a mesaj gonderir."""
    if not TELEGRAM_BOT_TOKEN:
        print("[WARN] TELEGRAM_BOT_TOKEN ayarlanmamis, mesaj gonderilemiyor.")
        print(text)
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            return True
        print(f"[ERROR] Telegram API hatasi: {resp.status_code} - {resp.text}")
        return False
    except requests.RequestException as e:
        print(f"[ERROR] Telegram baglanti hatasi: {e}")
        return False


def format_signal(signal: dict) -> str:
    """Sinyal mesajini formatlar."""
    direction = signal["direction"]
    emoji = "\U0001f7e2" if direction == "LONG" else "\U0001f534"  # green/red circle
    symbol = signal["symbol"]
    entry = signal["entry_price"]
    tp = signal["tp_price"]
    sl = signal["sl_price"]
    tp_pct = signal["tp_pct"]
    sl_pct = signal["sl_pct"]
    score = signal["score"]
    rsi = signal["rsi"]
    details = signal["details"]
    now = datetime.now(timezone.utc).strftime("%H:%M UTC")

    # Guven bari
    filled = "\u2588" * score
    empty = "\u2591" * (MAX_SCORE - score)
    confidence_bar = filled + empty

    # Gosterge detaylari
    macd_icon = "\u2705" if details.get("MACD") else "\u274c"
    bb_icon = "\u2705" if details.get("BB") else "\u274c"
    ema_icon = "\u2705" if details.get("EMA") else "\u274c"
    vol_icon = "\u2705" if details.get("VOL") else "\u274c"
    trend_icon = "\u2705" if details.get("TREND") else "\u274c"

    # Fiyat formatlama
    if entry >= 1000:
        price_fmt = f"{entry:,.2f}"
        tp_fmt = f"{tp:,.2f}"
        sl_fmt = f"{sl:,.2f}"
    elif entry >= 1:
        price_fmt = f"{entry:.4f}"
        tp_fmt = f"{tp:.4f}"
        sl_fmt = f"{sl:.4f}"
    else:
        price_fmt = f"{entry:.6f}"
        tp_fmt = f"{tp:.6f}"
        sl_fmt = f"{sl:.6f}"

    tp_sign = "+" if direction == "LONG" else "-"
    sl_sign = "-" if direction == "LONG" else "+"

    text = (
        f"{emoji} <b>{direction} S\u0130NYAL\u0130 - {symbol}</b>\n"
        f"\n"
        f"\U0001f4b0 Giri\u015f: ${price_fmt}\n"
        f"\U0001f3af Hedef: ${tp_fmt} ({tp_sign}{tp_pct:.1f}%)\n"
        f"\U0001f6d1 Stop: ${sl_fmt} ({sl_sign}{sl_pct:.1f}%)\n"
        f"\n"
        f"\U0001f4ca G\u00fcven: {confidence_bar} {score}/{MAX_SCORE}\n"
        f"\U0001f4c8 RSI: {rsi:.1f} | MACD: {macd_icon} | BB: {bb_icon}\n"
        f"    EMA: {ema_icon} | VOL: {vol_icon} | TREND: {trend_icon}\n"
        f"\u23f0 {now}\n"
        f"\n"
        f"\u26a0\ufe0f <i>Bu finansal tavsiye de\u011fildir.</i>"
    )
    return text


def send_signal(signal: dict) -> bool:
    """Formatlı sinyal mesaji gonderir."""
    text = format_signal(signal)
    return send_message(text)


def send_daily_summary(total: int, successful: int, failed: int):
    """Gunluk ozet raporu gonderir."""
    if total == 0:
        rate = 0
    else:
        rate = (successful / total) * 100

    text = (
        f"\U0001f4cb <b>G\u00fcnl\u00fck \u00d6zet Raporu</b>\n"
        f"\n"
        f"\U0001f4e8 Toplam Sinyal: {total}\n"
        f"\u2705 Ba\u015far\u0131l\u0131: {successful}\n"
        f"\u274c Ba\u015far\u0131s\u0131z: {failed}\n"
        f"\U0001f4ca Ba\u015far\u0131 Oran\u0131: %{rate:.1f}\n"
        f"\n"
        f"\U0001f916 Crypto Signal Bot"
    )
    return send_message(text)
