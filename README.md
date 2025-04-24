# 📈 Aylık BIST Yatırımı Simülatörü

Bu Streamlit uygulaması, belirli bir hisse senedine aylık bazda yapılan yatırımların USD bazında getirisini simüle eder. Kullanıcıdan alınan girişlere göre geçmiş fiyatlar ve döviz kurları kullanılarak kâr hesaplaması yapılır ve Excel dosyası olarak indirilebilir.

## 🚀 Özellikler

- Belirli bir hisse senedine (örnek: `THYAO.IS`) ait geçmiş fiyat verileri ile yatırım simülasyonu
- Her ay sabit bir miktar TL ile yapılan yatırımın toplam getirisi
- USD/TRY kuru dikkate alınarak USD bazında kâr hesaplaması
- Güncel borsa ve döviz kuru verileri ile değerlendirme
- Sonuçları içeren bir Excel dosyası oluşturma ve indirme

## 🛠 Kullanılan Teknolojiler

- **Python**
- **Streamlit** – Web arayüzü için
- **yfinance** – Borsa ve döviz verilerini almak için
- **pandas** – Veri işleme
- **openpyxl** – Excel dosyası oluşturma

## 🔧 Kurulum

### Gereksinimler

- Python 3.8 veya üzeri
- Paketler: `streamlit`, `pandas`, `yfinance`, `openpyxl`

### Sanal Ortam (isteğe bağlı)

```bash
python -m venv venv
source venv/bin/activate  # (Windows için: venv\Scripts\activate)
