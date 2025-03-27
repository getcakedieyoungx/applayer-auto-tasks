#!/bin/bash

# Gerekli dizinleri oluştur
mkdir -p logs

# Python sanal ortamını oluştur
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Konfigürasyon dosyasını oluştur
if [ ! -f config.env ]; then
    cp config.env.example config.env
    echo "config.env oluşturuldu. Lütfen düzenleyin."
fi

echo "Kurulum tamamlandı!"