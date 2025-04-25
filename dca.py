import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from openpyxl import Workbook

st.set_page_config(page_title="Aylık BIST Yatırımı Simülatörü", layout="centered")
st.title("💰 Aylık Yatırım Kâr Hesaplama")

# Kullanıcı girişi
stock_code = st.text_input("Hisse Kodu (örnek: THYAO.IS)", value="THYAO.IS")
start_date = st.date_input("Başlangıç Tarihi", value=datetime(2023, 1, 1))
end_date = st.date_input("Bitiş Tarihi", value=datetime(2025, 1, 1))
monthly_investment = st.number_input("Aylık Yatırım Tutarı (TL)", min_value=100.0, value=10000.0, step=100.0)

if st.button("Excel Oluştur"):
    try:
        dates = pd.date_range(start=start_date, end=end_date, freq='MS')

        stock_data = yf.download(stock_code, start=start_date, end=end_date + timedelta(days=1))
        fx_data = yf.download("USDTRY=X", start=start_date, end=end_date + timedelta(days=1))
        latest_stock_data = yf.download(stock_code, period="1d", interval="1d")
        latest_fx_data = yf.download("USDTRY=X", period="1d", interval="1d")

        if stock_data.empty or fx_data.empty or latest_stock_data.empty or latest_fx_data.empty:
            st.warning("Veri alınamadı. Hisse kodu veya tarih aralığını kontrol edin.")
            st.stop()

        # 'Adj Close' varsa onu kullan, yoksa 'Close'
        price_column = "Adj Close" if "Adj Close" in stock_data.columns else "Close"
        latest_price_column = "Adj Close" if "Adj Close" in latest_stock_data.columns else "Close"

        stock_prices = stock_data[price_column].resample('MS').first().reindex(dates).squeeze()
        exchange_rates = fx_data['Close'].resample('MS').first().reindex(dates).squeeze()
        final_price = float(latest_stock_data[latest_price_column].iloc[-1])
        final_rate = float(latest_fx_data["Close"].iloc[-1])

        df = pd.DataFrame({
            "Tarih": dates,
            "Hisse Fiyatı (TL)": stock_prices.values,
            "Kur (USD/TRY)": exchange_rates.values,
            "Yatırım (TL)": monthly_investment
        })

        df.dropna(inplace=True)

        df["Alınan Hisse"] = df["Yatırım (TL)"] / df["Hisse Fiyatı (TL)"]
        df["Harcanan USD"] = df["Yatırım (TL)"] / df["Kur (USD/TRY)"]
        df["Bugünkü Değer (TL)"] = df["Alınan Hisse"] * final_price
        df["Bugünkü Değer (USD)"] = df["Bugünkü Değer (TL)"] / final_rate
        df["Aylık Ortalama Hisse"] = df["Alınan Hisse"].expanding().mean()

        # Temettü verisi
        dividends = yf.Ticker(stock_code).dividends
        temettu_yatirimi_usd = 0.0
        if not dividends.empty:
                dividends.index = dividends.index.tz_localize(None)
                dividends = dividends[(dividends.index >= pd.to_datetime(start_date)) & (dividends.index <= pd.to_datetime(end_date))]

                if not dividends.empty:
                    dividend_df = pd.DataFrame(dividends)
                    dividend_df.columns = ["Temettü"]
                    dividend_df["Tarih"] = dividend_df.index

                    dividend_df = pd.merge_asof(
                        dividend_df.sort_values("Tarih"),
                        df[["Tarih", "Aylık Ortalama Hisse", "Hisse Fiyatı (TL)", "Kur (USD/TRY)"]].sort_values("Tarih"),
                        on="Tarih"
                    )

                    dividend_df["Temettü Geliri (TL)"] = dividend_df["Temettü"] * dividend_df["Aylık Ortalama Hisse"]
                    dividend_df["Yeniden Alınan Hisse"] = dividend_df["Temettü Geliri (TL)"] / dividend_df["Hisse Fiyatı (TL)"]
                    dividend_df["Bugünkü Değer (TL)"] = dividend_df["Yeniden Alınan Hisse"] * final_price
                    dividend_df["Bugünkü Değer (USD)"] = dividend_df["Bugünkü Değer (TL)"] / final_rate
                    temettu_yatirimi_usd = dividend_df["Bugünkü Değer (USD)"].sum()
                else:
                    dividend_df = pd.DataFrame()
                    temettu_yatirimi_usd = 0.0
        else:
                dividend_df = pd.DataFrame()
                temettu_yatirimi_usd = 0.0

        # METRİKLER
        total_invested = df["Harcanan USD"].sum()
        total_now = df["Bugünkü Değer (USD)"].sum()
        total_profit = total_now - total_invested
        total_shares = df["Alınan Hisse"].sum()
        profit_percent = (total_profit / total_invested) * 100
        total_with_dividends = total_profit + temettu_yatirimi_usd

        # ANA EKRAN GÖRÜNTÜLEME
        st.subheader("📊 Genel Özet")
        col1, col2, col3 = st.columns(3)
        col1.metric("Toplam Harcanan USD", f"{total_invested:,.2f} $")
        col2.metric("Toplam Hisse Adedi", f"{total_shares:,.2f}")
        col3.metric("Getiri Oranı Dolar Cinsinden", f"{profit_percent:.2f} %")

        st.success(f"💵 Toplam USD Kar: {total_profit:.2f} $")
        st.info(f"📈 Temettü Yeniden Yatırılsaydı: +{temettu_yatirimi_usd:.2f} $")
        st.metric("🎯 Temettü Dahil Toplam USD Getiri", f"{total_with_dividends:.2f} $")

        # Excel dosyası
        file_name = f"bist_kar_{stock_code.replace('.', '_')}.xlsx"
        with pd.ExcelWriter(file_name, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Aylık Yatırımlar")
            if not dividend_df.empty:
                dividend_df.to_excel(writer, index=False, sheet_name="Temettüler")

        with open(file_name, "rb") as f:
            st.download_button(
                label="Excel İndir (2 Sayfa)",
                data=f,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Hata oluştu: {str(e)}")
