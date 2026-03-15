import ccxt
import pandas as pd
from src.config import EXCHANGE_ID, CANDLE_LIMIT


def get_exchange():
    exchange = getattr(ccxt, EXCHANGE_ID)({
        "enableRateLimit": True,
    })
    return exchange


def fetch_ohlcv(exchange, symbol: str, timeframe: str, limit: int = CANDLE_LIMIT) -> pd.DataFrame:
    """Binance'den OHLCV mum verisi ceker."""
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df
