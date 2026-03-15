import numpy as np
import pandas as pd
import ta
from src.config import (
    RSI_PERIOD, MACD_FAST, MACD_SLOW, MACD_SIGNAL,
    BB_PERIOD, BB_STD, EMA_FAST, EMA_SLOW, EMA_TREND,
    DIVERGENCE_WINDOWS, DIVERGENCE_MIN_CONFIRM, DIVERGENCE_MIN_SLOPE,
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


def _linear_slope(values) -> float:
    """Bir serinin normalize edilmis egimini hesaplar."""
    n = len(values)
    if n < 2:
        return 0.0
    x = np.arange(n)
    y = np.array(values, dtype=float)
    # Normalize et (0-1 arasi) boylece farkli olcekleri karsilastirabiliriz
    y_range = y.max() - y.min()
    if y_range == 0:
        return 0.0
    y_norm = (y - y.min()) / y_range
    # Lineer regresyon (numpy ile, sklearn gereksiz)
    slope = np.polyfit(x, y_norm, 1)[0]
    return slope


def calculate_divergence(df: pd.DataFrame) -> dict:
    """RSI-Fiyat diverjansini tespit eder.

    Bullish diverjans: Fiyat dususte, RSI yukseliste -> yukari donus beklenir
    Bearish diverjans: Fiyat yukseliste, RSI dususte -> asagi donus beklenir

    4 farkli pencerede (10, 20, 30, 40 mum) kontrol edilir.
    Minimum 3/4 pencere ayni yonde onay vermeli.
    """
    rsi = calculate_rsi(df)
    close = df["close"]

    bullish_count = 0
    bearish_count = 0

    for window in DIVERGENCE_WINDOWS:
        if len(df) < window:
            continue

        price_slice = close.iloc[-window:].values
        rsi_slice = rsi.iloc[-window:].dropna().values

        if len(rsi_slice) < window // 2:
            continue

        price_slope = _linear_slope(price_slice)
        rsi_slope = _linear_slope(rsi_slice)

        # Bullish diverjans: fiyat dusuyor (negatif egim), RSI yukseliyor (pozitif egim)
        if price_slope < -DIVERGENCE_MIN_SLOPE and rsi_slope > DIVERGENCE_MIN_SLOPE:
            bullish_count += 1

        # Bearish diverjans: fiyat yukseliyor (pozitif egim), RSI dusuyor (negatif egim)
        if price_slope > DIVERGENCE_MIN_SLOPE and rsi_slope < -DIVERGENCE_MIN_SLOPE:
            bearish_count += 1

    return {
        "bullish_divergence": bullish_count >= DIVERGENCE_MIN_CONFIRM,
        "bearish_divergence": bearish_count >= DIVERGENCE_MIN_CONFIRM,
        "bullish_count": bullish_count,
        "bearish_count": bearish_count,
    }


def calculate_all(df: pd.DataFrame) -> dict:
    """Tum gostergeleri hesaplar ve son degerleri doner."""
    rsi = calculate_rsi(df)
    macd = calculate_macd(df)
    bb = calculate_bollinger(df)
    ema_fast = calculate_ema(df, EMA_FAST)
    ema_slow = calculate_ema(df, EMA_SLOW)
    divergence = calculate_divergence(df)

    close = df["close"].iloc[-1]
    volume = df["volume"].iloc[-1]
    avg_volume = df["volume"].rolling(20).mean().iloc[-1]

    # MACD kesisim kontrolu
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
        "bullish_divergence": divergence["bullish_divergence"],
        "bearish_divergence": divergence["bearish_divergence"],
    }


def calculate_trend(df_1h: pd.DataFrame) -> dict:
    """1h trend filtresi icin EMA50 hesaplar."""
    ema_trend = calculate_ema(df_1h, EMA_TREND)
    close = df_1h["close"].iloc[-1]
    return {
        "ema_trend": ema_trend.iloc[-1],
        "above_trend": close > ema_trend.iloc[-1],
    }
