import os

# Telegram
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = "1176599927"

# Borsa
EXCHANGE_ID = "kucoin"

# Coin listesi (Top 24 - yuksek hacim + volatilite, KuCoin & Binance'ta mevcut)
COINS = [
    # --- Majors ---
    "BTC/USDT",
    "ETH/USDT",
    "BNB/USDT",
    "SOL/USDT",
    "XRP/USDT",
    # --- Altcoins ---
    "DOGE/USDT",
    "ADA/USDT",
    "AVAX/USDT",
    "DOT/USDT",
    "POL/USDT",
    # --- Yeni eklenenler (yuksek hacim + volatilite) ---
    "LINK/USDT",
    "LTC/USDT",
    "UNI/USDT",
    "AAVE/USDT",
    "NEAR/USDT",
    "SUI/USDT",
    "TON/USDT",
    "TAO/USDT",
    "FET/USDT",
    "ZEC/USDT",
    "PEPE/USDT",
    "SHIB/USDT",
    "WIF/USDT",
    "TRUMP/USDT",
]

# Timeframe
TIMEFRAME_SIGNAL = "15m"
TIMEFRAME_TREND = "1h"
TIMEFRAME_MOMENTUM = "1m"
CANDLE_LIMIT = 100
MOMENTUM_CANDLE_LIMIT = 15  # Son 15 dakikalik 1m mumlar

# Gosterge parametreleri
RSI_PERIOD = 14
RSI_LONG_THRESHOLD = 48
RSI_SHORT_THRESHOLD = 52

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

BB_PERIOD = 20
BB_STD = 2

EMA_FAST = 9
EMA_SLOW = 21
EMA_TREND = 50

VOLUME_MULTIPLIER = 0.7

# Diverjans parametreleri
DIVERGENCE_WINDOWS = [10, 20, 30, 40]  # Farkli lookback pencereleri
DIVERGENCE_MIN_CONFIRM = 3  # Minimum 3/4 pencere onayi
DIVERGENCE_MIN_SLOPE = 0.05  # Minimum egim farki (normalize edilmis)

# Sinyal esikleri
MIN_SCORE = 4  # Minimum 4/7 gosterge onayi
MAX_SCORE = 7

# Risk yonetimi
TP_MIN = 2.0   # %2.0
TP_MAX = 3.0   # %3.0
STOP_LOSS = 1.5  # %1.5

# Momentum (ani hareket) esikleri
MOMENTUM_5M_THRESHOLD = 1.5   # %1.5 hareket 5 dakikada
MOMENTUM_10M_THRESHOLD = 2.5  # %2.5 hareket 10 dakikada
MOMENTUM_VOLUME_SPIKE = 3.0   # 3x ortalama hacim = momentum onayi

# Duplicate sinyal kontrolu (saniye)
DUPLICATE_WINDOW = 3600       # Teknik sinyal: 1 saat
MOMENTUM_DUPLICATE_WINDOW = 1800  # Momentum alarmi: 30 dakika

# Volatilite rejim esikleri (ATR% olarak)
VOL_REGIME_CALM = 0.5
VOL_REGIME_NORMAL = 1.0
VOL_REGIME_VOLATILE = 2.0
# >= 2.0 = extreme

# TP/SL carpanlari (rejime gore)
VOL_MULTIPLIERS = {
    "calm": 0.7,
    "normal": 1.0,
    "volatile": 1.4,
    "extreme": 1.8,
}

# Funding rate esikleri
FUNDING_HIGH_THRESHOLD = 0.0005    # %0.05 - kalabalik uyarisi
FUNDING_EXTREME_THRESHOLD = 0.001  # %0.1 - sinyal bastirma

# Drawdown devre kesici
DRAWDOWN_WINDOW = 21600      # 6 saat (saniye)
DRAWDOWN_MAX_STOPS = 3       # Maksimum ardisik stop sayisi

# Surekli calisma modu
SCAN_INTERVAL = 120  # 2 dakikada bir tarama (saniye)
MAX_RUNTIME = 20700  # 5 saat 45 dakika (saniye) - workflow 6 saatten once bitsin
