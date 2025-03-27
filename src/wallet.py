from web3 import Web3
from eth_account import Account
import os
from dotenv import load_dotenv
import logging

class Wallet:
    def __init__(self):
        load_dotenv('../config.env')
        self.private_key = os.getenv('PRIVATE_KEY')
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('RPC_URL')))
        self.account = Account.from_key(self.private_key)
        
    def get_balance(self):
        return self.w3.eth.get_balance(self.account.address)
    
    def send_transaction(self, to, value, data=None):
        try:
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            tx = {
                'nonce': nonce,
                'to': to,
                'value': value,
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price,
                'data': data if data else b''
            }
            signed = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
            return self.w3.eth.wait_for_transaction_receipt(tx_hash)
        except Exception as e:
            logging.error(f'Transaction error: {str(e)}')
            return None