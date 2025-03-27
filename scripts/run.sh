#!/bin/bash

# Sanal ortamı aktive et
source venv/bin/activate

# Screen oturumu oluştur
screen -dmS applayer-bot bash -c 'cd src && python3 -c "from tasks import TaskManager; TaskManager().run()"'

echo "Bot başlatıldı! Logları kontrol etmek için:
tail -f logs/bot.log"