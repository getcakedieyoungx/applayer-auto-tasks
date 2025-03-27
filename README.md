# AppLayer Otomatik Görev Botu

Bu bot, AppLayer Testnet üzerinde otomatik görevleri gerçekleştirmek için tasarlanmıştır.

## Özellikler

- ERC20 kontrat dağıtımı
- Otomatik işlem gönderimi
- Renkli konsol çıktısı
- Hata yönetimi ve loglama

## Kurulum

1. Depoyu klonlayın:
```bash
git clone https://github.com/getcakedieyoungx/applayer-auto-tasks.git
cd applayer-auto-tasks
```

2. Gerekli Python paketlerini yükleyin:
```bash

pip install -r requirements.txt
```

3. Konfigürasyon dosyasını oluşturun:
```bash
cp config.env.example config.env
```

4. `config.env` dosyasını düzenleyerek gerekli değişkenleri ayarlayın:
- `PRIVATE_KEY`: Cüzdan özel anahtarınız
- `RPC_URL`: AppLayer Testnet RPC URL'i
- `CHAIN_ID`: Ağ ID'si (75338)
- `CONTRACT_MANAGER`: Kontrat yöneticisi adresi
- `TASK_INTERVAL`: Görev kontrol aralığı (saat cinsinden)

## Kullanım

Botu başlatmak için:
```bash
python src/main.py
```

 Join tg, I will post bots there too.
T.me/getcakedieyoungx

For donations:
EVM: 0xE065339713A8D9BF897d595ED89150da521a7d09

SOLANA: CcBPMkpMbZ4TWE8HeUWyv9CkEVqPLJ5gYe163g5SR4Vf

## Lisans

MIT
