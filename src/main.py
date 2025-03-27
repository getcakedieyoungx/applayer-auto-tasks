import os
import sys
import time
import logging
import subprocess
from datetime import datetime
from colorama import init, Fore, Back, Style
import threading
from queue import Queue
import signal
import curses
from tasks import TaskManager

# Colorama başlat
init()

class ColoredFormatter(logging.Formatter):
    """Renkli log formatlayıcı"""
    
    COLORS = {
        'WARNING': Fore.YELLOW,
        'INFO': Fore.GREEN,
        'DEBUG': Fore.BLUE,
        'CRITICAL': Fore.RED,
        'ERROR': Fore.RED
    }

    EMOJI = {
        'WARNING': '⚠️ ',
        'INFO': '📝 ',
        'DEBUG': '🔍 ',
        'CRITICAL': '🔥 ',
        'ERROR': '❌ '
    }

    def format(self, record):
        # Renk ve emoji ekle
        color = self.COLORS.get(record.levelname, Fore.WHITE)
        emoji = self.EMOJI.get(record.levelname, '')
        
        # Zaman damgası formatı
        time_str = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Log mesajını formatla
        msg = f"{color}{time_str} {emoji}{record.levelname}: {record.getMessage()}{Style.RESET_ALL}"
        return msg

class DashboardUI:
    """Terminal tabanlı dashboard"""
    
    def __init__(self):
        self.stdscr = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_RED, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        self.log_queue = Queue()
        self.running = True

    def setup_windows(self):
        """Ekranı bölümlere ayır"""
        height, width = self.stdscr.getmaxyx()
        
        # Log penceresi (sol taraf, tam yükseklik)
        self.log_win = curses.newwin(height, width // 2, 0, 0)
        self.log_win.scrollok(True)
        
        # Durum penceresi (sağ üst)
        self.status_win = curses.newwin(height // 2, width // 2, 0, width // 2)
        
        # İstatistik penceresi (sağ alt)
        self.stats_win = curses.newwin(height // 2, width // 2, height // 2, width // 2)
        
        # Başlıkları ekle
        self.log_win.addstr(0, 0, "📝 LOGS", curses.A_BOLD)
        self.status_win.addstr(0, 0, "📊 STATUS", curses.A_BOLD)
        self.stats_win.addstr(0, 0, "📈 STATISTICS", curses.A_BOLD)
        
        self.refresh_all()

    def refresh_all(self):
        """Tüm pencereleri yenile"""
        self.log_win.refresh()
        self.status_win.refresh()
        self.stats_win.refresh()

    def update_log(self, message):
        """Log penceresini güncelle"""
        self.log_win.scroll()
        height, width = self.log_win.getmaxyx()
        self.log_win.addstr(height-1, 0, message[:width-1])
        self.log_win.refresh()

    def update_status(self, wallet_address, balance, last_action):
        """Durum penceresini güncelle"""
        self.status_win.clear()
        self.status_win.addstr(0, 0, "📊 STATUS", curses.A_BOLD)
        self.status_win.addstr(2, 0, f"🔑 Wallet: {wallet_address}")
        self.status_win.addstr(3, 0, f"💰 Balance: {balance} APPL")
        self.status_win.addstr(4, 0, f"🔄 Last Action: {last_action}")
        self.status_win.refresh()

    def update_stats(self, stats):
        """İstatistik penceresini güncelle"""
        self.stats_win.clear()
        self.stats_win.addstr(0, 0, "📈 STATISTICS", curses.A_BOLD)
        row = 2
        for key, value in stats.items():
            self.stats_win.addstr(row, 0, f"{key}: {value}")
            row += 1
        self.stats_win.refresh()

    def cleanup(self):
        """Curses temizle"""
        curses.endwin()

class AppLayerBot:
    """Ana bot sınıfı"""
    
    def __init__(self):
        self.setup_logging()
        self.ui = DashboardUI()
        self.stats = {
            "Tokens Claimed": 0,
            "Contracts Deployed": 0,
            "Errors": 0,
            "Uptime": "0:00:00"
        }
        self.start_time = datetime.now()
        signal.signal(signal.SIGINT, self.signal_handler)

    def setup_logging(self):
        """Logging ayarlarını yapılandır"""
        self.log_queue = Queue()
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(ColoredFormatter())
        logging.root.addHandler(handler)
        logging.root.setLevel(logging.INFO)

    def setup_environment(self):
        """Çalışma ortamını hazırla"""
        try:
            # Gerekli dizinleri oluştur
            os.makedirs('logs', exist_ok=True)
            os.makedirs('src', exist_ok=True)

            # Bağımlılıkları kontrol et ve yükle
            requirements = [
                'web3==6.15.1',
                'python-dotenv==1.0.0',
                'schedule==1.2.0',
                'requests==2.31.0',
                'cryptography==42.0.5',
                'colorama==0.4.6'
            ]
            
            for req in requirements:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', req])

            logging.info("✅ Ortam hazırlığı tamamlandı")
            return True
        except Exception as e:
            logging.error(f"❌ Ortam hazırlığı başarısız: {str(e)}")
            return False

    def update_stats(self):
        """İstatistikleri güncelle"""
        while self.running:
            self.stats["Uptime"] = str(datetime.now() - self.start_time).split('.')[0]
            self.ui.update_stats(self.stats)
            time.sleep(1)

    def run(self):
        """Bot'u başlat"""
        try:
            self.running = True
            self.ui.setup_windows()
            
            # İstatistik güncelleyici thread'i başlat
            stats_thread = threading.Thread(target=self.update_stats)
            stats_thread.daemon = True
            stats_thread.start()
            
            # TaskManager'ı başlat
            task_manager = TaskManager()
            
            # UI güncellemelerini başlat
            while self.running:
                try:
                    # Durum bilgisini güncelle
                    self.ui.update_status(
                        task_manager.wallet.account.address,
                        task_manager.wallet.get_balance(),
                        "Running"
                    )
                    
                    # TaskManager'ı çalıştır
                    task_manager.run()
                    
                except Exception as e:
                    logging.error(f"Runtime error: {str(e)}")
                    self.stats["Errors"] += 1
                    time.sleep(60)
                
        except KeyboardInterrupt:
            self.cleanup()
        except Exception as e:
            logging.error(f"Fatal error: {str(e)}")
            self.cleanup()

    def signal_handler(self, signum, frame):
        """Ctrl+C sinyalini yakala"""
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        """Temizlik işlemleri"""
        self.running = False
        self.ui.cleanup()
        logging.info("Bot durduruldu")

if __name__ == "__main__":
    bot = AppLayerBot()
    if bot.setup_environment():
        bot.run()