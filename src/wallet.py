from web3 import Web3
from eth_account import Account
import os
from dotenv import load_dotenv
import logging
from colorama import Fore, Style

class Wallet:
    def __init__(self):
        # .env dosyasını doğru yoldan yükle
        dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.env')
        load_dotenv(dotenv_path)
        
        # RPC bağlantısını kur
        self.rpc_url = os.getenv('RPC_URL')
        if not self.rpc_url:
            raise ValueError("RPC_URL not found in config.env")
            
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Private key'i al ve hesabı oluştur
        private_key = os.getenv('PRIVATE_KEY')
        if not private_key:
            raise ValueError("PRIVATE_KEY not found in config.env")
            
        if not private_key.startswith('0x'):
            private_key = '0x' + private_key
            
        self.account = Account.from_key(private_key)
        self.w3.eth.default_account = self.account.address
        
        # Chain ID'yi ayarla
        self.chain_id = int(os.getenv('CHAIN_ID', '75338'))
        
        logging.info(f"{Fore.GREEN}🔑 Cüzdan başlatıldı: {self.account.address}{Style.RESET_ALL}")
        
        # Başlangıç bakiyesini kontrol et
        self.check_initial_balance()
    
    def check_initial_balance(self):
        """Başlangıç bakiyesini kontrol et"""
        try:
            balance = self.w3.eth.get_balance(self.account.address)
            balance_in_eth = self.w3.from_wei(balance, 'ether')
            logging.info(f"{Fore.GREEN}💰 Güncel bakiye: {balance_in_eth} APPL{Style.RESET_ALL}")
        except Exception as e:
            logging.error(f"{Fore.RED}❌ Bakiye kontrolü başarısız: {str(e)}{Style.RESET_ALL}")
    
    def get_balance(self):
        """Cüzdan bakiyesini döndür"""
        try:
            balance = self.w3.eth.get_balance(self.account.address)
            return self.w3.from_wei(balance, 'ether')
        except Exception as e:
            logging.error(f"{Fore.RED}❌ Bakiye alma hatası: {str(e)}{Style.RESET_ALL}")
            return 0
    
    def sign_and_send_transaction(self, transaction):
        """İşlemi imzala ve gönder"""
        try:
            # Nonce'u al
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            # İşlem detaylarını hazırla
            tx = {
                'chainId': self.chain_id,
                'gas': transaction['gas'],
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
                'from': self.account.address,
                'to': transaction['to'],
                'data': transaction['data']
            }
            
            # İşlemi imzala
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            
            # İmzalı işlemi gönder
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # İşlem onayını bekle ve döndür
            return self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
        except Exception as e:
            logging.error(f"{Fore.RED}❌ İşlem gönderme hatası: {str(e)}{Style.RESET_ALL}")
            return None