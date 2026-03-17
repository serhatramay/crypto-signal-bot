import json
import os
import time
from src.config import (
    RSI_LONG_THRESHOLD, RSI_SHORT_THRESHOLD,
    VOLUME_MULTIPLIER, MIN_SCORE, MAX_SCORE,
    TP_MIN, TP_MAX, STOP_LOSS, DUPLICATE_WINDOW,
    MOMENTUM_5M_THRESHOLD, MOMENTUM_10M_THRESHOLD,
    MOMENTUM_VOLUME_SPIKE, MOMENTUM_DUPLICATE_WINDOW,
)

SIGNALS_FILE = os.path.join(os.path.dirname(__file__), "..", "signals_history.json")


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


def is_duplicate(symbol: str, direction: str, history: list, signal_type: str = "technical") -> bool:
    """Son belirli sure icinde ayni coin+yon icin sinyal var mi kontrol eder."""
    now = time.time()
    window = MOMENTUM_DUPLICATE_WINDOW if signal_type == "momentum" else DUPLICATE_WINDOW
    for sig in history:
        if (sig["symbol"] == symbol
                and sig["direction"] == direction
                and sig.get("type", "technical") == signal_type
                and now - sig["timestamp"] < window):
            return True
    return False


def evaluate_long(indicators: dict, trend: dict) -> dict:
    """LONG sinyal icin gostergeleri degerlendirir."""
    score = 0
    details = {}

    if indicators["rsi"] < RSI_LONG_THRESHOLD:
        score += 1
        details["RSI"] = True
    else:
        details["RSI"] = False

    if indicators["macd_cross_up"]:
        score += 1
        details["MACD"] = True
    else:
        details["MACD"] = False

    bb_lower = indicators["bb_lower"]
    close = indicators["close"]
    if close <= bb_lower * 1.005:
        score += 1
        details["BB"] = True
    else:
        details["BB"] = False

    if indicators["ema_cross_up"]:
        score += 1
        details["EMA"] = True
    else:
        details["EMA"] = False

    if indicators["volume"] > indicators["avg_volume"] * VOLUME_MULTIPLIER:
        score += 1
        details["VOL"] = True
    else:
        details["VOL"] = False

    if trend["above_trend"]:
        score += 1
        details["TREND"] = True
    else:
        details["TREND"] = False

    # RSI-Fiyat Diverjans (bullish: fiyat dusuyor ama RSI yukseliyor)
    if indicators["bullish_divergence"]:
        score += 1
        details["DIV"] = True
    else:
        details["DIV"] = False

    return {"score": score, "details": details}


def evaluate_short(indicators: dict, trend: dict) -> dict:
    """SHORT sinyal icin gostergeleri degerlendirir."""
    score = 0
    details = {}

    if indicators["rsi"] > RSI_SHORT_THRESHOLD:
        score += 1
        details["RSI"] = True
    else:
        details["RSI"] = False

    if indicators["macd_cross_down"]:
        score += 1
        details["MACD"] = True
    else:
        details["MACD"] = False

    bb_upper = indicators["bb_upper"]
    close = indicators["close"]
    if close >= bb_upper * 0.995:
        score += 1
        details["BB"] = True
    else:
        details["BB"] = False

    if indicators["ema_cross_down"]:
        score += 1
        details["EMA"] = True
    else:
        details["EMA"] = False

    if indicators["volume"] > indicators["avg_volume"] * VOLUME_MULTIPLIER:
        score += 1
        details["VOL"] = True
    else:
        details["VOL"] = False

    if not trend["above_trend"]:
        score += 1
        details["TREND"] = True
    else:
        details["TREND"] = False

    # RSI-Fiyat Diverjans (bearish: fiyat yukseliyor ama RSI dusuyor)
    if indicators["bearish_divergence"]:
        score += 1
        details["DIV"] = True
    else:
        details["DIV"] = False

    return {"score": score, "details": details}


def calculate_tp_sl(price: float, direction: str, score: int) -> dict:
    """Guven skoruna gore TP/SL hesaplar."""
    tp_pct = TP_MIN + (TP_MAX - TP_MIN) * ((score - MIN_SCORE) / (MAX_SCORE - MIN_SCORE))
    sl_pct = STOP_LOSS

    if direction == "LONG":
        tp_price = price * (1 + tp_pct / 100)
        sl_price = price * (1 - sl_pct / 100)
    else:
        tp_price = price * (1 - tp_pct / 100)
        sl_price = price * (1 + sl_pct / 100)

    return {
        "tp_price": tp_price,
        "sl_price": sl_price,
        "tp_pct": tp_pct,
        "sl_pct": sl_pct,
    }


def detect_momentum(symbol: str, df_1m) -> list:
    """1m mumlardan ani fiyat hareketi tespit eder. PUMP=LONG, DUMP=SHORT sinyal uretir."""
    if len(df_1m) < 10:
        return []

    history = load_signal_history()
    signals = []
    current_price = df_1m["close"].iloc[-1]

    # Son 5 dakikadaki degisim
    price_5m_ago = df_1m["close"].iloc[-6] if len(df_1m) >= 6 else df_1m["close"].iloc[0]
    change_5m = ((current_price - price_5m_ago) / price_5m_ago) * 100

    # Son 10 dakikadaki degisim
    price_10m_ago = df_1m["close"].iloc[-11] if len(df_1m) >= 11 else df_1m["close"].iloc[0]
    change_10m = ((current_price - price_10m_ago) / price_10m_ago) * 100

    # Hacim spike kontrolu
    avg_vol = df_1m["volume"].mean()
    recent_vol = df_1m["volume"].iloc[-3:].mean()  # Son 3 dakika ortalama hacim
    vol_spike = recent_vol > avg_vol * MOMENTUM_VOLUME_SPIKE

    # Yukari momentum -> LONG sinyal
    is_pump = (abs(change_5m) >= MOMENTUM_5M_THRESHOLD or abs(change_10m) >= MOMENTUM_10M_THRESHOLD)

    if is_pump and change_5m > 0 or change_10m > MOMENTUM_10M_THRESHOLD:
        if not is_duplicate(symbol, "LONG", history, "momentum"):
            tp_sl = calculate_tp_sl(current_price, "LONG", MIN_SCORE)
            signal = {
                "symbol": symbol,
                "type": "momentum",
                "direction": "LONG",
                "entry_price": current_price,
                "change_5m": change_5m,
                "change_10m": change_10m,
                "vol_spike": vol_spike,
                "price_before": price_10m_ago,
                "timestamp": time.time(),
                **tp_sl,
            }
            signals.append(signal)
            history.append({
                "symbol": symbol,
                "direction": "LONG",
                "type": "momentum",
                "timestamp": time.time(),
                "entry_price": current_price,
                "tp_price": tp_sl["tp_price"],
                "sl_price": tp_sl["sl_price"],
            })

    # Asagi momentum -> SHORT sinyal
    if is_pump and change_5m < 0 or change_10m < -MOMENTUM_10M_THRESHOLD:
        if not is_duplicate(symbol, "SHORT", history, "momentum"):
            tp_sl = calculate_tp_sl(current_price, "SHORT", MIN_SCORE)
            signal = {
                "symbol": symbol,
                "type": "momentum",
                "direction": "SHORT",
                "entry_price": current_price,
                "change_5m": change_5m,
                "change_10m": change_10m,
                "vol_spike": vol_spike,
                "price_before": price_10m_ago,
                "timestamp": time.time(),
                **tp_sl,
            }
            signals.append(signal)
            history.append({
                "symbol": symbol,
                "direction": "SHORT",
                "type": "momentum",
                "timestamp": time.time(),
                "entry_price": current_price,
                "tp_price": tp_sl["tp_price"],
                "sl_price": tp_sl["sl_price"],
            })

    if signals:
        save_signal_history(history)
    return signals


def generate_signals(symbol: str, indicators: dict, trend: dict) -> list:
    """Bir coin icin teknik sinyal uretir."""
    history = load_signal_history()
    signals = []

    # LONG degerlendirmesi
    long_eval = evaluate_long(indicators, trend)
    if long_eval["score"] >= MIN_SCORE and not is_duplicate(symbol, "LONG", history):
        tp_sl = calculate_tp_sl(indicators["close"], "LONG", long_eval["score"])
        signal = {
            "symbol": symbol,
            "type": "technical",
            "direction": "LONG",
            "entry_price": indicators["close"],
            "score": long_eval["score"],
            "details": long_eval["details"],
            "rsi": indicators["rsi"],
            "timestamp": time.time(),
            **tp_sl,
        }
        signals.append(signal)
        history.append({
            "symbol": symbol,
            "direction": "LONG",
            "type": "technical",
            "timestamp": time.time(),
            "entry_price": indicators["close"],
            "tp_price": tp_sl["tp_price"],
            "sl_price": tp_sl["sl_price"],
        })

    # SHORT degerlendirmesi
    short_eval = evaluate_short(indicators, trend)
    if short_eval["score"] >= MIN_SCORE and not is_duplicate(symbol, "SHORT", history):
        tp_sl = calculate_tp_sl(indicators["close"], "SHORT", short_eval["score"])
        signal = {
            "symbol": symbol,
            "type": "technical",
            "direction": "SHORT",
            "entry_price": indicators["close"],
            "score": short_eval["score"],
            "details": short_eval["details"],
            "rsi": indicators["rsi"],
            "timestamp": time.time(),
            **tp_sl,
        }
        signals.append(signal)
        history.append({
            "symbol": symbol,
            "direction": "SHORT",
            "type": "technical",
            "timestamp": time.time(),
            "entry_price": indicators["close"],
            "tp_price": tp_sl["tp_price"],
            "sl_price": tp_sl["sl_price"],
        })

    save_signal_history(history)
    return signals
