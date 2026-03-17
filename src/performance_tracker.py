import json
import os
import time
from src.data_fetcher import get_exchange
from src.telegram_notifier import send_daily_summary, send_signal_result

SIGNALS_FILE = os.path.join(os.path.dirname(__file__), "..", "signals_history.json")
PERFORMANCE_FILE = os.path.join(os.path.dirname(__file__), "..", "performance.json")


def load_signal_history() -> list:
    if os.path.exists(SIGNALS_FILE):
        try:
            with open(SIGNALS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_signal_history(history: list):
    with open(SIGNALS_FILE, "w") as f:
        json.dump(history, f, indent=2)


def load_performance() -> dict:
    if os.path.exists(PERFORMANCE_FILE):
        try:
            with open(PERFORMANCE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"total": 0, "successful": 0, "failed": 0}
    return {"total": 0, "successful": 0, "failed": 0}


def save_performance(perf: dict):
    with open(PERFORMANCE_FILE, "w") as f:
        json.dump(perf, f, indent=2)


def check_signals():
    """Gecmis sinyallerin TP veya SL'ye ulasip ulasmadigini kontrol eder."""
    history = load_signal_history()
    if not history:
        return

    exchange = get_exchange()
    perf = load_performance()
    updated_history = []

    for sig in history:
        # Zaten sonuclanmis sinyalleri atla
        if sig.get("result"):
            updated_history.append(sig)
            continue

        # Momentum sinyallerini atla (tp_price/sl_price yok)
        if sig.get("type") == "momentum":
            updated_history.append(sig)
            continue

        # 24 saatten eski sinyalleri suresi dolmus olarak isaretle
        if time.time() - sig["timestamp"] > 86400:
            sig["result"] = "expired"
            perf["total"] += 1
            perf["failed"] += 1
            updated_history.append(sig)
            print(f"  [EXPIRED] {sig['symbol']} {sig['direction']} - 24 saat icinde TP/SL'ye ulasamadi")
            continue

        # Guncel fiyati al
        try:
            ticker = exchange.fetch_ticker(sig["symbol"])
            current_price = ticker["last"]
        except Exception as e:
            print(f"[WARN] {sig['symbol']} fiyat alinamadi: {e}")
            updated_history.append(sig)
            continue

        result = None
        if sig["direction"] == "LONG":
            if current_price >= sig["tp_price"]:
                result = "tp_hit"
                perf["successful"] += 1
            elif current_price <= sig["sl_price"]:
                result = "sl_hit"
                perf["failed"] += 1
        else:  # SHORT
            if current_price <= sig["tp_price"]:
                result = "tp_hit"
                perf["successful"] += 1
            elif current_price >= sig["sl_price"]:
                result = "sl_hit"
                perf["failed"] += 1

        if result:
            sig["result"] = result
            perf["total"] += 1
            try:
                send_signal_result(sig, result, current_price)
                print(f"  [SONUC] {sig['symbol']} {sig['direction']} -> {result} | Giris: {sig['entry_price']:.4f} | Simdi: {current_price:.4f}")
            except Exception as e:
                print(f"  [WARN] Sonuc bildirimi gonderilemedi: {e}")

        updated_history.append(sig)

    save_signal_history(updated_history)
    save_performance(perf)
    return perf


def send_summary_if_needed():
    """Her gun sonu (UTC 23:45-23:59 arasi) gunluk ozet gonderir."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)

    # Sadece UTC 23:45-23:59 arasinda ozet gonder
    if now.hour == 23 and now.minute >= 45:
        perf = load_performance()
        if perf["total"] > 0:
            send_daily_summary(
                perf["total"],
                perf["successful"],
                perf["failed"],
            )
            # Gunluk sayaclari sifirla
            save_performance({"total": 0, "successful": 0, "failed": 0})

            # Eski sinyalleri temizle (24 saatten eski)
            history = load_signal_history()
            now_ts = time.time()
            history = [s for s in history if now_ts - s["timestamp"] < 86400]
            save_signal_history(history)
