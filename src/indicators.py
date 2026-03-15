import pandas as pd
import ta
from src.config import (
    RSI_PERIOD, MACD_FAST, MACD_SLOW, MACD_SIGNAL,
    BB_PERIOD, BB_STD, EMA_FAST, EMA_SLOW, EMA_TREND,
)


def calculate_rsi(df: pd.DataFrame) -> pd.Series:
    return ta.momentum.RSIIndicator(close=df["close"], window=RSI_PERIOD).rsi()


def calculate_macd(df: pd.DataFrame) -> dict:
    macd = ta.trend.MACD(
        close=df["close"],
        window_slow=MACD_SLOW,
        window_fast=MACD_FAST,
        window_sign=MACD_SIGNAL,
    )
    return {
        "macd": macd.macd(),
        "signal": macd.macd_signal(),
        "diff": macd.macd_diff(),
    }


def calculate_bollinger(df: pd.DataFrame) -> dict:
    bb = ta.volatility.BollingerBands(
        close=df["close"],
        window=BB_PERIOD,
        window_dev=BB_STD,
    )
    return {
        "upper": bb.bollinger_hband(),
        "middle": bb.bollinger_mavg(),
        "lower": bb.bollinger_lband(),
    }


def calculate_ema(df: pd.DataFrame, period: int) -> pd.Series:
    return ta.trend.EMAIndicator(close=df["close"], window=period).ema_indicator()


def calculate_all(df: pd.DataFrame) -> dict:
    """Tum gostergeleri hesaplar ve son degerleri doner."""
    rsi = calculate_rsi(df)
    macd = calculate_macd(df)
    bb = calculate_bollinger(df)
    ema_fast = calculate_ema(df, EMA_FAST)
    ema_slow = calculate_ema(df, EMA_SLOW)

    close = df["close"].iloc[-1]
    volume = df["volume"].iloc[-1]
    avg_volume = df["volume"].rolling(20).mean().iloc[-1]

    # MACD kesisim kontrolu: onceki barda diff isareti degismis mi
    macd_diff = macd["diff"]
    macd_cross_up = macd_diff.iloc[-1] > 0 and macd_diff.iloc[-2] <= 0
    macd_cross_down = macd_diff.iloc[-1] < 0 and macd_diff.iloc[-2] >= 0

    # EMA kesisim kontrolu
    ema_cross_up = (ema_fast.iloc[-1] > ema_slow.iloc[-1]) and (ema_fast.iloc[-2] <= ema_slow.iloc[-2])
    ema_cross_down = (ema_fast.iloc[-1] < ema_slow.iloc[-1]) and (ema_fast.iloc[-2] >= ema_slow.iloc[-2])

    return {
        "close": close,
        "rsi": rsi.iloc[-1],
        "macd_diff": macd_diff.iloc[-1],
        "macd_cross_up": macd_cross_up,
        "macd_cross_down": macd_cross_down,
        "bb_upper": bb["upper"].iloc[-1],
        "bb_lower": bb["lower"].iloc[-1],
        "ema_fast": ema_fast.iloc[-1],
        "ema_slow": ema_slow.iloc[-1],
        "ema_cross_up": ema_cross_up,
        "ema_cross_down": ema_cross_down,
        "volume": volume,
        "avg_volume": avg_volume,
    }


def calculate_trend(df_1h: pd.DataFrame) -> dict:
    """1h trend filtresi icin EMA50 hesaplar."""
    ema_trend = calculate_ema(df_1h, EMA_TREND)
    close = df_1h["close"].iloc[-1]
    return {
        "ema_trend": ema_trend.iloc[-1],
        "above_trend": close > ema_trend.iloc[-1],
    }
