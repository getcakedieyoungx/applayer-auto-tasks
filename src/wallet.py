from web3 import Web3
from eth_account import Account
import os
from dotenv import load_dotenv
import logging

class Wallet:
    def __init__(self):
        # .env dosyasını doğru yoldan yükle
        dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.env')
        load_dotenv(dotenv_path)
        
        self.private_key = os.getenv('PRIVATE_KEY')
        if not self.private_key:
            raise ValueError("Private key not found in config.env")
            
        self.rpc_url = os.getenv('RPC_URL')
        if not self.rpc_url:
            raise ValueError("RPC URL not found in config.env")
            
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.account = Account.from_key(self.private_key)
        
        logging.info(f'🔑 Cüzdan başlatıldı: {self.account.address}')
        
    def get_balance(self):
        try:
            balance = self.w3.eth.get_balance(self.account.address)
            balance_eth = self.w3.from_wei(balance, "ether")
            logging.info(f'💰 Güncel bakiye: {balance_eth} APPL')
            return balance_eth
        except Exception as e:
            logging.error(f'❌ Bakiye sorgulama hatası: {str(e)}')
            return 0
    
    def send_transaction(self, to, value, data=None):
        try:
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            tx = {
                'nonce': nonce,
                'to': to,
                'value': value,
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price,
                'chainId': int(os.getenv('CHAIN_ID', 75338)),
                'data': data if data else b''
            }
            
            logging.info(f'📤 İşlem hazırlanıyor: {to}')
            signed = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
            
            logging.info(f'⏳ İşlem gönderildi: {tx_hash.hex()}')
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            logging.info(f'✅ İşlem onaylandı: Blok {receipt["blockNumber"]}')
            
            return receipt
        except Exception as e:
            logging.error(f'❌ İşlem hatası: {str(e)}')
            return None