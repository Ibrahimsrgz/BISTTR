import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Gösterge Hesaplama Fonksiyonları ---
def calculate_macd(df):
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    return df

def calculate_rsi(df, window=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

# --- Strateji Simülasyonu ---
def backtest_strategy(df, initial_balance=10000, stop_loss=0.05, take_profit=0.10):
    balance = initial_balance
    trades = []

    for i in range(1, len(df) - 10):  # 10 gün ileri bakmak için sınır
        if (
            df['MACD'].iloc[i - 1] < df['Signal'].iloc[i - 1]
            and df['MACD'].iloc[i] > df['Signal'].iloc[i]
            and df['RSI'].iloc[i] < 40
        ):
            entry_price = df['Close'].iloc[i]
            entry_date = df.index[i]

            for j in range(i + 1, i + 11):
                future_price = df['Close'].iloc[j]
                change = float((future_price - entry_price) / entry_price)

                if change >= take_profit:
                    profit = balance * take_profit
                    balance += profit
                    trades.append((entry_date, df.index[j], 'TP', profit))
                    break
                elif change <= -stop_loss:
                    loss = balance * stop_loss
                    balance -= loss
                    trades.append((entry_date, df.index[j], 'SL', -loss))
                    break
            else:
                final_price = df['Close'].iloc[i + 10]
                change = float((final_price - entry_price) / entry_price)
                pnl = balance * change
                balance += pnl
                result = 'TP' if change > 0 else 'SL'
                trades.append((entry_date, df.index[i + 10], result, pnl))

    return balance, pd.DataFrame(trades, columns=['Entry', 'Exit', 'Result', 'PnL'])

# --- Ana Fonksiyon ---
def main():
    ticker = "AAPL"  
    df = yf.download(ticker, start="2016-01-01", end="2024-12-31", auto_adjust=True)
    
    df.dropna(inplace=True)  # Verideki boşlukları temizle
    df = calculate_macd(df)
    df = calculate_rsi(df)
    df.dropna(inplace=True)  # Göstergeler sonrası boşluklar

    final_balance, trades = backtest_strategy(df)

    print(f"\n--- Strateji Sonuçları: {ticker} ---")
    print(f"Başlangıç Bakiyesi: 10.000₺")
    print(f"Son Bakiye: {final_balance:,.2f}₺")
    print(f"Toplam İşlem: {len(trades)}")
    if len(trades) > 0:
        print(f"Başarı Oranı: {(trades['PnL'] > 0).mean() * 100:.2f}%\n")
    else:
        print("İşlem bulunamadı.\n")

    print(trades.head())

    # --- Grafik ---
    if len(trades) > 0:
        trades['Cumulative'] = trades['PnL'].cumsum() + 10000
        plt.figure(figsize=(10, 5))
        plt.plot(trades['Exit'], trades['Cumulative'], label="Bakiye")
        plt.title(f"{ticker} MACD+RSI Strateji Bakiye Gelişimi (TL)")
        plt.xlabel("Tarih")
        plt.ylabel("Bakiye (₺)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    main()
