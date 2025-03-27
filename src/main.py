import os
import time
import logging
from datetime import datetime
from colorama import Fore, Style, init
from dotenv import load_dotenv
from wallet import Wallet
from contracts import ContractManager

# Colorama'yı başlat
init(autoreset=True)

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)

def setup():
    """Bot başlangıç ayarlarını yapar"""
    try:
        # .env dosyasını yükle
        dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.env')
        if not os.path.exists(dotenv_path):
            raise FileNotFoundError("config.env dosyası bulunamadı!")
        load_dotenv(dotenv_path)
        
        # Gerekli çevre değişkenlerini kontrol et
        required_vars = ['PRIVATE_KEY', 'RPC_URL', 'CHAIN_ID', 'CONTRACT_MANAGER']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Eksik çevre değişkenleri: {', '.join(missing_vars)}")
        
        logging.info(f"{Fore.GREEN}✅ Bot ayarları başarıyla yüklendi{Style.RESET_ALL}")
        return True
        
    except Exception as e:
        logging.error(f"{Fore.RED}❌ Bot ayarları yüklenirken hata: {str(e)}{Style.RESET_ALL}")
        return False

def main():
    """Ana bot döngüsü"""
    print(f"\n{Fore.CYAN}🤖 AppLayer Otomatik Görev Botu Başlatılıyor...{Style.RESET_ALL}\n")
    
    # Bot ayarlarını yükle
    if not setup():
        logging.error(f"{Fore.RED}❌ Bot başlatılamadı. Lütfen config.env dosyasını kontrol edin.{Style.RESET_ALL}")
        return
    
    try:
        # Cüzdan ve kontrat yöneticisini başlat
        wallet = Wallet()
        contract_manager = ContractManager(wallet)
        
        # Bakiyeyi kontrol et
        balance = wallet.get_balance()
        logging.info(f"{Fore.GREEN}💰 Cüzdan bakiyesi: {balance} ETH{Style.RESET_ALL}")
        
        # Ana döngü
        task_interval = int(os.getenv('TASK_INTERVAL', '24')) * 3600  # Saat -> saniye
        last_check = 0
        
        while True:
            try:
                current_time = time.time()
                
                # Task aralığını kontrol et
                if current_time - last_check >= task_interval:
                    logging.info(f"{Fore.YELLOW}🔍 Görevler kontrol ediliyor...{Style.RESET_ALL}")
                    
                    # Deploy edilmiş kontratları listele
                    contracts = contract_manager.get_deployed_contracts()
                    logging.info(f"{Fore.CYAN}📋 Toplam {len(contracts)} kontrat bulundu{Style.RESET_ALL}")
                    
                    # Yeni ERC20 kontratı oluştur
                    timestamp = str(int(time.time()))
                    token_name = f"TestToken_{timestamp}"
                    token_symbol = f"TT{timestamp[-4:]}"  # Son 4 karakteri al
                    decimals = 18
                    initial_supply = 1000000 * (10 ** decimals)  # 1 milyon token
                    
                    receipt = contract_manager.deploy_erc20(
                        token_name,
                        token_symbol,
                        decimals,
                        initial_supply
                    )
                    
                    if receipt and receipt.get('status') == 1:
                        logging.info(f"{Fore.GREEN}✅ Yeni token başarıyla oluşturuldu: {token_name}{Style.RESET_ALL}")
                    else:
                        logging.error(f"{Fore.RED}❌ Token oluşturma başarısız{Style.RESET_ALL}")
                    
                    last_check = current_time
                
                # CPU kullanımını azaltmak için kısa bir bekleme
                time.sleep(5)
                
            except Exception as e:
                logging.error(f"{Fore.RED}❌ Görev döngüsünde hata: {str(e)}{Style.RESET_ALL}")
                time.sleep(60)  # Hata durumunda 1 dakika bekle
                
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Bot kapatılıyor...{Style.RESET_ALL}")
    except Exception as e:
        logging.error(f"{Fore.RED}❌ Kritik hata: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()