#!/usr/bin/env python3
"""Crypto Signal Bot - Surekli calisma modlu ana giris noktasi."""

import sys
import time
import traceback
from datetime import datetime, timezone

from src.config import (
    COINS, TIMEFRAME_SIGNAL, TIMEFRAME_TREND,
    SCAN_INTERVAL, MAX_RUNTIME,
)
from src.data_fetcher import get_exchange, fetch_ohlcv, fetch_momentum_data
from src.indicators import calculate_all, calculate_trend
from src.signal_engine import generate_signals, detect_momentum
from src.telegram_notifier import send_signal
from src.performance_tracker import check_signals, send_summary_if_needed


def scan_once(exchange) -> int:
    """Tek bir tarama dongusu. Uretilen sinyal sayisini doner."""
    total_signals = 0

    # Onceki sinyallerin durumunu kontrol et
    try:
        check_signals()
    except Exception as e:
        print(f"[WARN] Performans kontrolu hatasi: {e}")

    for symbol in COINS:
        try:
            # --- Momentum tespiti (1m mumlar, hizli) ---
            df_1m = fetch_momentum_data(exchange, symbol)
            momentum_signals = detect_momentum(symbol, df_1m)
            for sig in momentum_signals:
                print(f"  >>> {symbol} {sig['direction']}! "
                      f"5dk: {sig['change_5m']:+.2f}% | 10dk: {sig['change_10m']:+.2f}%")
                send_signal(sig)
                total_signals += 1

            # --- Teknik analiz (15m + 1h, her 5. turda) ---
            # Teknik gostergeler daha yavas degisir, her turda gerek yok
            # Ama basitlik icin her turda kontrol ediyoruz
            df_15m = fetch_ohlcv(exchange, symbol, TIMEFRAME_SIGNAL)
            df_1h = fetch_ohlcv(exchange, symbol, TIMEFRAME_TREND)

            indicators = calculate_all(df_15m)
            trend = calculate_trend(df_1h)

            signals = generate_signals(symbol, indicators, trend)
            for sig in signals:
                print(f"  >>> {symbol} {sig['direction']} SINYAL! Skor: {sig['score']}/6")
                send_signal(sig)
                total_signals += 1

        except Exception as e:
            print(f"[ERROR] {symbol}: {e}")
            continue

    return total_signals


def main():
    """Surekli calisma modu: MAX_RUNTIME suresince SCAN_INTERVAL aralikla tarama yapar."""
    print("=== Crypto Signal Bot - Surekli Mod ===")
    print(f"    Tarama araligi: {SCAN_INTERVAL}s | Max calisma: {MAX_RUNTIME}s")

    exchange = get_exchange()
    start_time = time.time()
    scan_count = 0
    total_signals = 0

    while True:
        elapsed = time.time() - start_time
        if elapsed >= MAX_RUNTIME:
            print(f"\n[INFO] Max calisma suresi doldu ({MAX_RUNTIME}s). Cikiliyor.")
            break

        scan_count += 1
        now = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
        remaining = int(MAX_RUNTIME - elapsed)
        print(f"\n--- Tarama #{scan_count} | {now} | Kalan: {remaining}s ---")

        try:
            signals = scan_once(exchange)
            total_signals += signals
            if signals:
                print(f"  {signals} sinyal uretildi!")
            else:
                print(f"  Sinyal yok.")
        except Exception as e:
            print(f"[ERROR] Tarama hatasi: {e}")
            traceback.print_exc()

        # Gunluk ozet kontrolu
        try:
            send_summary_if_needed()
        except Exception as e:
            print(f"[WARN] Gunluk ozet hatasi: {e}")

        # Sonraki taramaya kadar bekle
        elapsed_after = time.time() - start_time
        if elapsed_after + SCAN_INTERVAL >= MAX_RUNTIME:
            break
        time.sleep(SCAN_INTERVAL)

    print(f"\n=== Bot durdu. {scan_count} tarama, {total_signals} sinyal. ===")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Bot kullanici tarafindan durduruldu.")
    except Exception as e:
        print(f"[FATAL] Bot hatasi: {e}")
        traceback.print_exc()
        sys.exit(1)
