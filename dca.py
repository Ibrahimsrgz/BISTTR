import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(page_title="Aylık BIST Yatırımı Simülatörü", layout="centered")
st.title("💰 Aylık Yatırım Kâr Hesaplama")

stock_code = st.text_input("Hisse Kodu (örnek: THYAO.IS)", value="THYAO.IS")
start_date = st.date_input("Başlangıç Tarihi", value=datetime(2023, 1, 1))
end_date = st.date_input("Bitiş Tarihi", value=datetime(2025, 1, 1))
monthly_investment = st.number_input("Aylık Yatırım Tutarı (TL)", min_value=100.0, value=10000.0, step=100.0)

if st.button("Excel Oluştur"):
    try:
        dates = pd.date_range(start=start_date, end=end_date, freq='MS')

        stock_data = yf.download(stock_code, start=start_date, end=end_date + timedelta(days=1))
        fx_data = yf.download("USDTRY=X", start=start_date, end=end_date + timedelta(days=1))

        # Güncel verileri çek
        latest_stock_data = yf.download(stock_code, period="1d", interval="1d")
        latest_fx_data = yf.download("USDTRY=X", period="1d", interval="1d")

        if stock_data.empty or fx_data.empty or latest_stock_data.empty or latest_fx_data.empty:
            st.warning("Veri alınamadı. Hisse kodu veya tarih aralığını kontrol edin.")
            st.stop()

        stock_prices = stock_data['Close'].resample('MS').first().reindex(dates).squeeze()
        exchange_rates = fx_data['Close'].resample('MS').first().reindex(dates).squeeze()

        df = pd.DataFrame({
            "Tarih": dates,
            "Hisse Fiyatı (TL)": stock_prices.values,
            "Kur (USD/TRY)": exchange_rates.values
        })

        df.dropna(inplace=True)

        if df.empty:
            st.warning("Yeterli veri bulunamadı. Lütfen tarih aralığını kontrol edin.")
            st.stop()

        # Güncel fiyatlar
        final_price = float(latest_stock_data["Close"].iloc[-1])
        final_rate = float(latest_fx_data["Close"].iloc[-1])

        df["Yatırım (TL)"] = monthly_investment
        df["Alınan Hisse"] = df["Yatırım (TL)"] / df["Hisse Fiyatı (TL)"]
        df["Harcanan USD"] = df["Yatırım (TL)"] / df["Kur (USD/TRY)"]
        df["Bugünkü Değer (TL)"] = df["Alınan Hisse"] * final_price
        df["Bugünkü Değer (USD)"] = df["Bugünkü Değer (TL)"] / final_rate

        # METRİKLER
        total_invested = df["Harcanan USD"].sum()
        total_now = df["Bugünkü Değer (USD)"].sum()
        total_profit = total_now - total_invested
        total_shares = df["Alınan Hisse"].sum()
        profit_percent = (total_profit / total_invested) * 100

        st.subheader("📊 Genel Özet")
        col1, col2, col3 = st.columns(3)
        col1.metric("Toplam Harcanan USD", f"{total_invested:,.2f} $")
        col2.metric("Toplam Hisse Adedi", f"{total_shares:,.2f}")
        col3.metric("Getiri Oranı Dolar Cinsinden", f"{profit_percent:.2f} %")

        st.success(f"Toplam USD kârı: {total_profit:.2f} $")

        file_name = f"bist_kar_{stock_code.replace('.', '_')}.xlsx"
        df.to_excel(file_name, index=False)

        with open(file_name, "rb") as f:
            st.download_button(
                label="Excel İndir",
                data=f,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Hata oluştu: {str(e)}")
