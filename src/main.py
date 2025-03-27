import os
import time
import logging
import random
from datetime import datetime, timedelta
from colorama import Fore, Style, init
from dotenv import load_dotenv
from wallet import Wallet
from contracts import ContractManager

# ASCII Banner
banner = '''
 ██████╗ ███████╗████████╗ ██████╗ █████╗ ██╗  ██╗███████╗       
██╔════╝ ██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║ ██╔╝██╔════╝       
██║  ███╗█████╗     ██║   ██║     ███████║█████╔╝ █████╗         
██║   ██║██╔══╝     ██║   ██║     ██╔══██║██╔═██╗ ██╔══╝         
╚██████╔╝███████╗   ██║   ╚██████╗██║  ██║██║  ██╗███████╗       
 ╚═════╝ ╚══════╝   ╚═╝    ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝       
██████╗ ██╗███████╗██╗   ██╗ ██████╗ ██╗   ██╗███╗   ██╗ ██████╗ 
██╔══██╗██║██╔════╝╚██╗ ██╔╝██╔═══██╗██║   ██║████╗  ██║██╔════╝ 
██║  ██║██║█████╗   ╚████╔╝ ██║   ██║██║   ██║██╔██╗ ██║██║  ███╗
██║  ██║██║██╔══╝    ╚██╔╝  ██║   ██║██║   ██║██║╚██╗██║██║   ██║
██████╔╝██║███████╗   ██║   ╚██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝
╚═════╝ ╚═╝╚══════╝   ╚═╝    ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ 
       GETCAKE DIEYOUNGX - t.me/getcakedieyoungx
'''

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

def get_random_deployment_count():
    """24 saatlik periyotta kaç deployment yapılacağını belirle"""
    return random.randint(3, 4)

def get_next_deployment_time(last_deployment):
    """Bir sonraki deployment zamanını hesapla"""
    hours_until_next = random.uniform(4, 8)  # 4-8 saat arası
    return last_deployment + timedelta(hours=hours_until_next)

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
    print(f"\n{Fore.CYAN}{banner}{Style.RESET_ALL}\n")
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
        
        # Deployment değişkenlerini ayarla
        daily_deployments = get_random_deployment_count()
        deployments_today = 0
        last_deployment = datetime.now() - timedelta(hours=24)  # İlk deployment'ı hemen yap
        next_deployment = datetime.now()
        
        logging.info(f"{Fore.YELLOW}ℹ️ Bugün {daily_deployments} adet token deploy edilecek{Style.RESET_ALL}")
        
        while True:
            try:
                current_time = datetime.now()
                
                # Yeni gün kontrolü
                if current_time.date() > last_deployment.date():
                    daily_deployments = get_random_deployment_count()
                    deployments_today = 0
                    logging.info(f"{Fore.YELLOW}ℹ️ Yeni gün başladı. Bugün {daily_deployments} adet token deploy edilecek{Style.RESET_ALL}")
                
                # Deployment zamanı geldi mi ve günlük limit dolmadı mı?
                if current_time >= next_deployment and deployments_today < daily_deployments:
                    logging.info(f"{Fore.YELLOW}🔍 Görevler kontrol ediliyor...{Style.RESET_ALL}")
                    
                    # Deploy edilmiş kontratları listele
                    contracts = contract_manager.get_deployed_contracts()
                    logging.info(f"{Fore.CYAN}📋 Toplam {len(contracts)} kontrat bulundu{Style.RESET_ALL}")
                    
                    # Yeni ERC20 kontratı oluştur
                    timestamp = str(int(time.time()))
                    token_name = f"TestToken_{timestamp}"
                    token_symbol = f"TT{timestamp[-4:]}"
                    decimals = 18
                    initial_supply = 1000000 * (10 ** decimals)  # 1 milyon token
                    
                    receipt = contract_manager.deploy_erc20(
                        token_name,
                        token_symbol,
                        decimals,
                        initial_supply
                    )
                    
                    if receipt and receipt.get('status') == 1:
                        tx_hash = receipt.get('transactionHash', b'').hex()
                        contract_address = receipt.get('contractAddress', 'Bilinmiyor')
                        logging.info(f"{Fore.GREEN}✅ Yeni token başarıyla oluşturuldu:{Style.RESET_ALL}")
                        logging.info(f"{Fore.GREEN}📝 Token Adı: {token_name}{Style.RESET_ALL}")
                        logging.info(f"{Fore.GREEN}🏷️ Sembol: {token_symbol}{Style.RESET_ALL}")
                        logging.info(f"{Fore.GREEN}📍 Kontrat Adresi: {contract_address}{Style.RESET_ALL}")
                        logging.info(f"{Fore.GREEN}🔗 TX Hash: {tx_hash}{Style.RESET_ALL}")
                        
                        deployments_today += 1
                        last_deployment = current_time
                        next_deployment = get_next_deployment_time(last_deployment)
                        
                        remaining = daily_deployments - deployments_today
                        next_time = next_deployment.strftime('%H:%M:%S')
                        logging.info(f"{Fore.YELLOW}ℹ️ Bugün {remaining} deployment kaldı. Sonraki deployment: {next_time}{Style.RESET_ALL}")
                    else:
                        logging.error(f"{Fore.RED}❌ Token oluşturma başarısız{Style.RESET_ALL}")
                        next_deployment = current_time + timedelta(minutes=5)  # 5 dakika sonra tekrar dene
                
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