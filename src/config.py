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
CANDLE_LIMIT = 100

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

# Sinyal esikleri
MIN_SCORE = 4  # Minimum 4/6 gosterge onayi
MAX_SCORE = 6

# Risk yonetimi
TP_MIN = 1.0   # %1.0
TP_MAX = 1.5   # %1.5
STOP_LOSS = 0.75  # %0.75

# Duplicate sinyal kontrolu (saniye)
DUPLICATE_WINDOW = 3600  # 1 saat
