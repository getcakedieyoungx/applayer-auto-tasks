# 🤖 AppLayer Otomatik Görev Botu

Bu bot, AppLayer testnet üzerinde günlük görevleri otomatik olarak tamamlar ve güzel bir arayüz ile durumu gösterir.

## ✨ Özellikler

- 🎨 Renkli ve modern terminal arayüzü
- 📊 Gerçek zamanlı durum takibi
- 📈 İstatistik paneli
- 🔄 Otomatik görev planlaması
- 🛡️ Hata yönetimi ve otomatik kurtarma
- 📝 Detaylı loglama

## 🚀 Kurulum

1. Repoyu klonlayın:
```bash
git clone https://github.com/getcakedieyoungx/applayer-auto-tasks.git
cd applayer-auto-tasks
```

2. Python sanal ortamı oluşturun:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux için
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

4. Konfigürasyon dosyasını düzenleyin:
```bash
cp config.env.example config.env
nano config.env  # Düzenlemek için
```

## 💫 Kullanım

Botu başlatmak için:
```bash
python src/main.py
```

## 📊 Arayüz

Bot başladığında terminal 3 bölüme ayrılır:

- 📝 **Loglar** (Sol panel)
  - Gerçek zamanlı log akışı
  - Renkli ve emojili mesajlar

- 📊 **Durum** (Sağ üst panel)
  - Cüzdan adresi
  - APPL bakiyesi
  - Son işlem

- 📈 **İstatistikler** (Sağ alt panel)
  - Talep edilen token sayısı
  - Deploy edilen kontrat sayısı
  - Hata sayısı
  - Çalışma süresi

## ⚙️ Konfigürasyon

`config.env` dosyasında şu ayarları yapmalısınız:

```env
# Cüzdan ayarları
PRIVATE_KEY=your_private_key_here

# AppLayer Testnet ayarları
RPC_URL=https://testnet-api.applayer.com/
CHAIN_ID=75338
CONTRACT_MANAGER=0x0001cb47ea6d8b55fe44fdd6b1bdb579efb43e61
```

## 📝 Lisans

MIT