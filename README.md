# AppLayer Otomatik Görev Botu

Bu bot, AppLayer testnet üzerinde günlük görevleri otomatik olarak tamamlar.

## Özellikler

- Otomatik cüzdan yönetimi
- AppLayer testnet bağlantısı
- Otomatik token talep etme
- Akıllı kontrat etkileşimleri
- Linux screen ile arka plan çalışması

## Kurulum

1. Repoyu klonlayın:
```bash
git clone https://github.com/getcakedieyoungx/applayer-auto-tasks.git
cd applayer-auto-tasks
```

2. Sanal ortam oluşturun:
```bash
python -m venv venv
source venv/bin/activate  # Linux
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

4. Konfigürasyon dosyasını oluşturun:
```bash
cp config.env.example config.env
```

5. config.env dosyasını düzenleyin ve gerekli bilgileri girin.

## Kullanım

1. Botu başlatın:
```bash
./scripts/run.sh
```

2. Logları kontrol edin:
```bash
tail -f logs/bot.log
```

## Lisans

MIT