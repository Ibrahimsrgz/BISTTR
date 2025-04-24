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

Paketleri Yükleyin
pip install -r requirements.txt

Alternatif olarak:
pip install streamlit pandas yfinance openpyxl

Uygulamayı Başlatın
streamlit run dca.py

🧪 Kullanım
Hisse kodunu girin (örnek: THYAO.IS)

Başlangıç ve bitiş tarihlerini seçin

Aylık yatırım miktarını belirtin

Excel Oluştur butonuna tıklayın

Hesaplanan sonuçlar ekranda özetlenir, Excel dosyası indirilebilir

📦 Excel Çıktısı
Çıktı dosyası aşağıdaki sütunları içerir:

Tarih
Hisse Fiyatı (TL)
Kur (USD/TRY)
Yatırım (TL)
Alınan Hisse
Harcanan USD
Bugünkü Değer (TL)
Bugünkü Değer (USD)

⚠️ Notlar
Veri kaynakları yfinance ile Yahoo Finance üzerinden çekilmektedir. Hisse kodları bu formata uygun olmalıdır (.IS = Borsa İstanbul).

Veri eksikliği veya Yahoo API limiti nedeniyle veri alınamama durumları olabilir.
