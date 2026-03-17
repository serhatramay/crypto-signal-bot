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
    """BTC 1h trendini kontrol eder. 'bullish', 'bearish' veya 'neutral' doner."""
    try:
        df = fetch_ohlcv(exchange, "BTC/USDT", "1h", limit=50)
        ema9 = ta.trend.EMAIndicator(close=df["close"], window=EMA_FAST).ema_indicator().iloc[-1]
        ema21 = ta.trend.EMAIndicator(close=df["close"], window=EMA_SLOW).ema_indicator().iloc[-1]

        gap_pct = ((ema9 - ema21) / ema21) * 100

        if gap_pct > 0.1:
            return "bullish"
        elif gap_pct < -0.1:
            return "bearish"
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
