# Crypto Signal Bot

Binance verilerini analiz ederek Telegram'a kripto al-sat sinyalleri gonderen bot.

## Ozellikler
- Top 10 coin analizi (BTC, ETH, BNB, SOL, XRP, DOGE, ADA, AVAX, DOT, MATIC)
- 6 teknik gosterge ile coklu onay sistemi (RSI, MACD, Bollinger, EMA, Hacim, Trend)
- %1-1.5 kar hedefli, %0.75 stop loss
- GitHub Actions ile her 15 dakikada otomatik calisma
- Gunluk performans ozet raporu

## Kurulum

### 1. GitHub Secrets
Repo ayarlarindan asagidaki secret'i ekleyin:
- `TELEGRAM_BOT_TOKEN`: Telegram bot tokeniniz

### 2. Lokal Test
```bash
pip install -r requirements.txt
TELEGRAM_BOT_TOKEN=your_token python main.py
```

### 3. GitHub Actions
Repo'ya push ettikten sonra Actions otomatik olarak her 15 dakikada calisir.
Manuel tetiklemek icin Actions sekmesinden "Run workflow" butonunu kullanin.

## Sinyal Formati
```
🟢 LONG SİNYALİ - BTC/USDT

💰 Giriş: $67,450.00
🎯 Hedef: $68,124.50 (+1.0%)
🛑 Stop: $66,943.75 (-0.75%)

📊 Güven: ████░░ 4/6
📈 RSI: 32.5 | MACD: ✅ | BB: ✅
⏰ 15:30 UTC

⚠️ Bu finansal tavsiye değildir.
```

## Disclaimer
Bu bot yalnizca egitim amaclidir. Finansal tavsiye degildir.
