#!/usr/bin/env python3
"""Crypto Signal Bot - Ana giris noktasi."""

import sys
import traceback
from src.config import COINS, TIMEFRAME_SIGNAL, TIMEFRAME_TREND
from src.data_fetcher import get_exchange, fetch_ohlcv
from src.indicators import calculate_all, calculate_trend
from src.signal_engine import generate_signals
from src.telegram_notifier import send_signal
from src.performance_tracker import check_signals, send_summary_if_needed


def main():
    print("=== Crypto Signal Bot Baslatiliyor ===")

    exchange = get_exchange()
    total_signals = 0

    # Onceki sinyallerin durumunu kontrol et
    try:
        check_signals()
    except Exception as e:
        print(f"[WARN] Performans kontrolu hatasi: {e}")

    # Her coin icin analiz yap
    for symbol in COINS:
        try:
            print(f"\n[{symbol}] Analiz ediliyor...")

            # Veri cek
            df_15m = fetch_ohlcv(exchange, symbol, TIMEFRAME_SIGNAL)
            df_1h = fetch_ohlcv(exchange, symbol, TIMEFRAME_TREND)

            # Gosterge hesapla
            indicators = calculate_all(df_15m)
            trend = calculate_trend(df_1h)

            print(f"  RSI: {indicators['rsi']:.1f} | "
                  f"MACD Cross Up: {indicators['macd_cross_up']} | "
                  f"MACD Cross Down: {indicators['macd_cross_down']} | "
                  f"Trend: {'UP' if trend['above_trend'] else 'DOWN'}")

            # Sinyal uret
            signals = generate_signals(symbol, indicators, trend)

            for signal in signals:
                print(f"  >>> {signal['direction']} SINYAL! Skor: {signal['score']}/6")
                send_signal(signal)
                total_signals += 1

            if not signals:
                print(f"  Sinyal yok.")

        except Exception as e:
            print(f"[ERROR] {symbol} isleme hatasi: {e}")
            traceback.print_exc()
            continue

    print(f"\n=== Toplam {total_signals} sinyal uretildi ===")

    # Gunluk ozet kontrolu
    try:
        send_summary_if_needed()
    except Exception as e:
        print(f"[WARN] Gunluk ozet hatasi: {e}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[FATAL] Bot hatasi: {e}")
        traceback.print_exc()
        sys.exit(1)
