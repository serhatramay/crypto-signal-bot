import ccxt
import pandas as pd
import ta
from src.config import (
    EXCHANGE_ID, CANDLE_LIMIT, MOMENTUM_CANDLE_LIMIT,
    EMA_FAST, EMA_SLOW, FUNDING_HIGH_THRESHOLD,
)


def get_exchange():
    exchange = getattr(ccxt, EXCHANGE_ID)({
        "enableRateLimit": True,
    })
    return exchange


def fetch_ohlcv(exchange, symbol: str, timeframe: str, limit: int = CANDLE_LIMIT) -> pd.DataFrame:
    """Borsadan OHLCV mum verisi ceker."""
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df


def fetch_momentum_data(exchange, symbol: str) -> pd.DataFrame:
    """1 dakikalik mum verileri ceker (momentum analizi icin)."""
    return fetch_ohlcv(exchange, symbol, "1m", limit=MOMENTUM_CANDLE_LIMIT)


def check_btc_macro(exchange) -> str:
    """BTC trendini kontrol eder. EMA + anlik momentum birlikte degerlendirilir."""
    try:
        df = fetch_ohlcv(exchange, "BTC/USDT", "1h", limit=50)
        ema9 = ta.trend.EMAIndicator(close=df["close"], window=EMA_FAST).ema_indicator().iloc[-1]
        ema21 = ta.trend.EMAIndicator(close=df["close"], window=EMA_SLOW).ema_indicator().iloc[-1]

        gap_pct = ((ema9 - ema21) / ema21) * 100

        # Anlik momentum: son 2 saatteki fiyat degisimi
        price_now = df["close"].iloc[-1]
        price_2h = df["close"].iloc[-3] if len(df) >= 3 else df["close"].iloc[0]
        momentum_pct = ((price_now - price_2h) / price_2h) * 100

        # Son 4 saatteki fiyat degisimi (daha genis pencere)
        price_4h = df["close"].iloc[-5] if len(df) >= 5 else df["close"].iloc[0]
        momentum_4h = ((price_now - price_4h) / price_4h) * 100

        # Karar: EMA trendi VEYA guclu momentum yeterli
        bearish_signals = 0
        bullish_signals = 0

        if gap_pct < -0.1:
            bearish_signals += 1
        elif gap_pct > 0.1:
            bullish_signals += 1

        if momentum_pct < -0.5:
            bearish_signals += 1
        elif momentum_pct > 0.5:
            bullish_signals += 1

        if momentum_4h < -1.0:
            bearish_signals += 1
        elif momentum_4h > 1.0:
            bullish_signals += 1

        print(f"    EMA gap: {gap_pct:+.3f}% | 2h mom: {momentum_pct:+.2f}% | 4h mom: {momentum_4h:+.2f}%")

        if bearish_signals >= 2:
            return "bearish"
        elif bullish_signals >= 2:
            return "bullish"
        elif momentum_pct < -0.8 or momentum_4h < -1.5:
            return "bearish"  # Guclu anlik dusus tek basina yeterli
        elif momentum_pct > 0.8 or momentum_4h > 1.5:
            return "bullish"  # Guclu anlik yukselis tek basina yeterli
        else:
            return "neutral"
    except Exception as e:
        print(f"[WARN] BTC makro kontrol hatasi: {e}")
        return "neutral"


def _classify_funding(rate: float) -> str:
    """Funding rate'ini siniflandirir."""
    if rate > FUNDING_HIGH_THRESHOLD:
        return "high_long"
    elif rate > 0.0001:
        return "mild_long"
    elif rate < -FUNDING_HIGH_THRESHOLD:
        return "high_short"
    elif rate < -0.0001:
        return "mild_short"
    else:
        return "neutral"


def check_funding_rate() -> dict:
    """BTC funding rate'ini kontrol eder. Tum piyasa icin proxy olarak kullanilir."""
    try:
        futures = ccxt.kucoinfutures({"enableRateLimit": True})
        fr = futures.fetch_funding_rate("BTC/USDT:USDT")
        rate = fr.get("fundingRate", 0) or 0
        return {"funding_rate": rate, "funding_status": _classify_funding(rate)}
    except Exception as e:
        print(f"[WARN] Funding rate alinamadi: {e}")
        return {"funding_rate": 0, "funding_status": "neutral"}
