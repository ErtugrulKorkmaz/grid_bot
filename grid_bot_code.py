import pandas as pd
import numpy as np
from binance.client import Client
from datetime import datetime, timedelta

class GridBotAnalyzer:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)
        
    def calculate_volatility(self, symbol, interval):
        """Volatilite hesaplama"""
        klines = self.client.futures_klines(symbol=symbol, interval=interval)
        closes = pd.DataFrame(klines)[4].astype(float)
        return np.std(np.log(closes/closes.shift(1))) * np.sqrt(len(closes)) * 100
        
    def get_volume(self, symbol):
        """24 saatlik işlem hacmini getir"""
        ticker = self.client.futures_ticker(symbol=symbol)
        return float(ticker['volume']) * float(ticker['lastPrice'])
        
    def get_funding_rate(self, symbol):
        """Funding oranını getir"""
        funding = self.client.futures_funding_rate(symbol=symbol, limit=1)[0]
        return float(funding['fundingRate']) * 100
        
    def get_price_range(self, symbol, days=14):
        """Fiyat aralığını hesapla"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        klines = self.client.futures_klines(
            symbol=symbol,
            interval='1d',
            startTime=int(start_time.timestamp() * 1000),
            endTime=int(end_time.timestamp() * 1000)
        )
        
        highs = [float(k[2]) for k in klines]
        lows = [float(k[3]) for k in klines]
        
        return max(highs), min(lows)
        
    def analyze_coin(self, symbol):
        """Coin analizi yap"""
        daily_vol = self.calculate_volatility(symbol, '1d')
        weekly_vol = self.calculate_volatility(symbol, '1w')
        volume = self.get_volume(symbol)
        funding = self.get_funding_rate(symbol)
        range_high, range_low = self.get_price_range(symbol)
        
        return {
            'coin': symbol,
            'daily_volatility': round(daily_vol, 2),
            'weekly_volatility': round(weekly_vol, 2),
            'volume': round(volume / 1_000_000, 2),  # milyon USD
            'funding_fee': round(funding, 4),
            'range_high': round(range_high, 2),
            'range_low': round(range_low, 2)
        }
        
    def calculate_grid_settings(self, analysis):
        """Grid bot ayarlarını hesapla"""
        price_range = analysis['range_high'] - analysis['range_low']
        grid_count = int(price_range / (analysis['range_low'] * 0.005))  # %0.50 minimum grid aralığı
        
        return {
            'leverage': 20,
            'price_range': f"${analysis['range_low']} - ${analysis['range_high']}",
            'grid_count': min(grid_count, 50),  # maksimum 50 grid
            'stop_loss': 20,
            'take_profit': 75,
            'bnb_commission': 'Evet'
        }
        
    def print_analysis(self, symbol):
        """Analiz sonuçlarını yazdır"""
        analysis = self.analyze_coin(symbol)
        settings = self.calculate_grid_settings(analysis)
        
        print("\n## Filtreleme Sonucu:")
        print(f"- Coin İsmi: {analysis['coin']}")
        print(f"- Günlük Volatilite: %{analysis['daily_volatility']}")
        print(f"- Haftalık Volatilite: %{analysis['weekly_volatility']}")
        print(f"- İşlem Hacmi: ${analysis['volume']} milyon")
        print(f"- Funding Fee: %{analysis['funding_fee']}")
        print(f"- Range High: ${analysis['range_high']}")
        print(f"- Range Low: ${analysis['range_low']}")
        
        print("\n## Grid Bot Ayarları:")
        print(f"- Kaldıraç: {settings['leverage']}x")
        print(f"- Fiyat Aralığı: {settings['price_range']}")
        print(f"- Grid Sayısı: {settings['grid_count']}")
        print(f"- Stop-Loss Seviyesi: %{settings['stop_loss']}")
        print(f"- Take-Profit Seviyesi: %{settings['take_profit']}")
        print(f"- Komisyon İndirimi: {settings['bnb_commission']}")

# Kullanım örneği:
if __name__ == "__main__":
    api_key = "your_api_key"
    api_secret = "your_api_secret"
    
    analyzer = GridBotAnalyzer(api_key, api_secret)
    analyzer.print_analysis("AVAXUSDT")