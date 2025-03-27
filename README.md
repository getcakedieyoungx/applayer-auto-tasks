# AppLayer Otomatik Görev Botu

Bu bot, AppLayer Testnet üzerinde otomatik görevleri gerçekleştirmek için tasarlanmıştır.

## Özellikler

- ERC20 kontrat dağıtımı
- Günlük 3-4 arası otomatik token deployment
- Akıllı zamanlama (4-8 saat arası)
- Renkli konsol çıktısı ve detaylı loglama
- TX hash ve kontrat adresi takibi
- Hata yönetimi

## Kurulum

1. Depoyu klonlayın:
```bash
git clone https://github.com/getcakedieyoungx/applayer-auto-tasks.git
cd applayer-auto-tasks
```

2. Python sanal ortamı oluşturun ve aktifleştirin:
```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Gerekli Python paketlerini yükleyin:
```bash
pip install -r requirements.txt
```

4. Konfigürasyon dosyasını oluşturun:
```bash
cp config.env.example config.env
```

5. `config.env` dosyasını düzenleyerek gerekli değişkenleri ayarlayın:
```env
# Cüzdan ayarları
PRIVATE_KEY=your_private_key_here  # Private key'iniz (0x ile başlamalı)

# AppLayer Testnet ayarları
RPC_URL=https://testnet-api.applayer.com/  # RPC URL
CHAIN_ID=75338  # AppLayer Testnet Chain ID
CONTRACT_MANAGER=0x0001cb47ea6d8b55fe44fdd6b1bdb579efb43e61  # Kontrat yöneticisi adresi

# Bot ayarları
TASK_INTERVAL=24  # Görev kontrol aralığı (saat)
```

## Kullanım

1. Sanal ortamı aktifleştirin (eğer aktif değilse):
```bash
# Linux/macOS
source venv/bin/activate

# Windows
.\venv\Scripts\activate
```

2. Botu başlatın:
```bash
python src/main.py
```

## Çıktı Örnekleri

Bot çalıştığında şu tür çıktılar göreceksiniz:

```
🤖 AppLayer Otomatik Görev Botu Başlatılıyor...
✅ Bot ayarları başarıyla yüklendi
🔑 Cüzdan başlatıldı: 0x8d43...8d3d
💰 Güncel bakiye: 1 APPL
ℹ️ Bugün 3 adet token deploy edilecek

// Token deployment örneği:
🚀 Yeni ERC20 kontratı deploy ediliyor: TestToken_1743096662 (TT6662)
✅ Yeni token başarıyla oluşturuldu:
📝 Token Adı: TestToken_1743096662
🏷️ Sembol: TT6662
📍 Kontrat Adresi: 0x123...abc
🔗 TX Hash: 0x3ad...ac7
```

##  Join tg, I will post bots there too.
T.me/getcakedieyoungx


## For donations and buying me a coffee:
EVM: 0xE065339713A8D9BF897d595ED89150da521a7d09

SOLANA: CcBPMkpMbZ4TWE8HeUWyv9CkEVqPLJ5gYe163g5SR4Vf

## Lisans

MIT

## İletişim

Telegram: [t.me/getcakedieyoungx](https://t.me/getcakedieyoungx)
