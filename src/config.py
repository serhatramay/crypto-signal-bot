import os

# Telegram
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = "1176599927"

# Borsa
EXCHANGE_ID = "kucoin"

# Coin listesi (Top 10)
COINS = [
    "BTC/USDT",
    "ETH/USDT",
    "BNB/USDT",
    "SOL/USDT",
    "XRP/USDT",
    "DOGE/USDT",
    "ADA/USDT",
    "AVAX/USDT",
    "DOT/USDT",
    "POL/USDT",
]

# Timeframe
TIMEFRAME_SIGNAL = "15m"
TIMEFRAME_TREND = "1h"
TIMEFRAME_MOMENTUM = "1m"
CANDLE_LIMIT = 100
MOMENTUM_CANDLE_LIMIT = 15  # Son 15 dakikalik 1m mumlar

# Gosterge parametreleri
RSI_PERIOD = 14
RSI_LONG_THRESHOLD = 35
RSI_SHORT_THRESHOLD = 65

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

BB_PERIOD = 20
BB_STD = 2

EMA_FAST = 9
EMA_SLOW = 21
EMA_TREND = 50

VOLUME_MULTIPLIER = 1.5

# Diverjans parametreleri
DIVERGENCE_WINDOWS = [10, 20, 30, 40]  # Farkli lookback pencereleri
DIVERGENCE_MIN_CONFIRM = 3  # Minimum 3/4 pencere onayi
DIVERGENCE_MIN_SLOPE = 0.05  # Minimum egim farki (normalize edilmis)

# Sinyal esikleri
MIN_SCORE = 4  # Minimum 4/7 gosterge onayi
MAX_SCORE = 7

# Risk yonetimi
TP_MIN = 1.0   # %1.0
TP_MAX = 1.5   # %1.5
STOP_LOSS = 0.75  # %0.75

# Momentum (ani hareket) esikleri
MOMENTUM_5M_THRESHOLD = 1.5   # %1.5 hareket 5 dakikada
MOMENTUM_10M_THRESHOLD = 2.5  # %2.5 hareket 10 dakikada
MOMENTUM_VOLUME_SPIKE = 3.0   # 3x ortalama hacim = momentum onayi

# Duplicate sinyal kontrolu (saniye)
DUPLICATE_WINDOW = 3600       # Teknik sinyal: 1 saat
MOMENTUM_DUPLICATE_WINDOW = 1800  # Momentum alarmi: 30 dakika

# Surekli calisma modu
SCAN_INTERVAL = 120  # 2 dakikada bir tarama (saniye)
MAX_RUNTIME = 20700  # 5 saat 45 dakika (saniye) - workflow 6 saatten once bitsin
