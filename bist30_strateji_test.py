import yfinance as yf
import pandas as pd

def run_all_strategies(ticker: str, start_date: str, end_date: str):
    df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)
    df = df[['Close']].copy()

    # Hareketli Ortalamalar (Golden Cross)
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()

    # RSI
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['SignalLine'] = df['MACD'].ewm(span=9, adjust=False).mean()

    results = {}

    # === Golden Cross Strategy ===
    def simulate_golden():
        position, returns = 0, []
        buy_price = 0
        for i in range(1, len(df)):
            if df['MA50'].iloc[i] > df['MA200'].iloc[i] and df['MA50'].iloc[i-1] <= df['MA200'].iloc[i-1]:
                if position == 0:
                    buy_price = df['Close'].iloc[i]
                    position = 1
            elif df['MA50'].iloc[i] < df['MA200'].iloc[i] and df['MA50'].iloc[i-1] >= df['MA200'].iloc[i-1]:
                if position == 1:
                    sell_price = df['Close'].iloc[i]
                    returns.append((sell_price - buy_price) / buy_price)
                    position = 0
        if position == 1:
            sell_price = df['Close'].iloc[-1]
            returns.append((sell_price - buy_price) / buy_price)
        rets = (pd.Series(returns) + 1).prod() - 1
        return float(rets.iloc[0] if isinstance(rets, pd.Series) else rets), len(returns)

    # === RSI Strategy ===
    def simulate_rsi():
        position, returns = 0, []
        buy_price = 0
        for i in range(1, len(df)):
            if df['RSI'].iloc[i-1] < 30 and df['RSI'].iloc[i] >= 30:
                if position == 0:
                    buy_price = df['Close'].iloc[i]
                    position = 1
            elif df['RSI'].iloc[i-1] > 70 and df['RSI'].iloc[i] <= 70:
                if position == 1:
                    sell_price = df['Close'].iloc[i]
                    returns.append((sell_price - buy_price) / buy_price)
                    position = 0
        if position == 1:
            sell_price = df['Close'].iloc[-1]
            returns.append((sell_price - buy_price) / buy_price)
        rets = (pd.Series(returns) + 1).prod() - 1
        return float(rets.iloc[0] if isinstance(rets, pd.Series) else rets), len(returns)

    # === MACD Strategy ===
    def simulate_macd():
        position, returns = 0, []
        buy_price = 0
        for i in range(1, len(df)):
            if df['MACD'].iloc[i-1] < df['SignalLine'].iloc[i-1] and df['MACD'].iloc[i] > df['SignalLine'].iloc[i]:
                if position == 0:
                    buy_price = df['Close'].iloc[i]
                    position = 1
            elif df['MACD'].iloc[i-1] > df['SignalLine'].iloc[i-1] and df['MACD'].iloc[i] < df['SignalLine'].iloc[i]:
                if position == 1:
                    sell_price = df['Close'].iloc[i]
                    returns.append((sell_price - buy_price) / buy_price)
                    position = 0
        if position == 1:
            sell_price = df['Close'].iloc[-1]
            returns.append((sell_price - buy_price) / buy_price)
        rets = (pd.Series(returns) + 1).prod() - 1
        return float(rets.iloc[0] if isinstance(rets, pd.Series) else rets), len(returns)

    # Stratejileri çalıştır
    results['Golden Cross'] = simulate_golden()
    results['RSI'] = simulate_rsi()
    results['MACD'] = simulate_macd()

    print(f"\n{ticker} - {start_date} ➝ {end_date} STRATEJİ KARŞILAŞTIRMASI:")
    for name, (ret, trades) in results.items():
        print(f"{name:<15} | Getiri: {ret*100:>6.2f}% | İşlem Sayısı: {trades}")

# ÖRNEK KULLANIM
run_all_strategies("ASELS.IS", "2024-01-01", "2025-04-01")
