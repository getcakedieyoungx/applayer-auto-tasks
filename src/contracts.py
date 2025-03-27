import os
import json
import time
import logging
from web3 import Web3
from eth_account.messages import encode_defunct
from colorama import Fore, Style

class ContractManager:
    def __init__(self, wallet):
        self.wallet = wallet
        self.w3 = wallet.w3
        self.contract_manager_address = Web3.to_checksum_address("0x0001cb47ea6d8b55fe44fdd6b1bdb579efb43e61")
        
        # ContractManager ABI
        self.contract_manager_abi = [
            {"inputs":[],"name":"getDeployedContracts","outputs":[{"components":[{"internalType":"string","name":"name","type":"string"},{"internalType":"address","name":"addr","type":"address"}],"internalType":"struct ContractManager.Contract[]","name":"","type":"tuple[]"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"ticket","type":"string"},{"internalType":"uint8","name":"decimals","type":"uint8"},{"internalType":"uint256","name":"mintValue","type":"uint256"}],"name":"createNewERC20Contract","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"nonpayable","type":"function"}
        ]
        
        self.contract = self.w3.eth.contract(
            address=self.contract_manager_address,
            abi=self.contract_manager_abi
        )
    
    def get_deployed_contracts(self):
        """Deploy edilmiş kontratları listeler"""
        try:
            contracts = self.contract.functions.getDeployedContracts().call()
            return contracts
        except Exception as e:
            logging.error(f"{Fore.RED}❌ Deploy edilmiş kontratlar alınırken hata: {str(e)}{Style.RESET_ALL}")
            return []

    def deploy_erc20(self, name, symbol, decimals, initial_supply):
        """Yeni bir ERC20 token kontratı deploy eder"""
        try:
            logging.info(f"{Fore.CYAN}🚀 Yeni ERC20 kontratı deploy ediliyor: {name} ({symbol}){Style.RESET_ALL}")
            
            # Deploy işlemini başlat
            nonce = self.w3.eth.get_transaction_count(self.wallet.account.address)
            
            # Gas hesaplamaları
            base_fee = self.w3.eth.get_block('latest')['baseFeePerGas']
            priority_fee = 2_000_000_000  # 2 Gwei
            max_fee = int(base_fee * 1.1) + priority_fee
            
            contract_txn = self.contract.functions.createNewERC20Contract(
                name,
                symbol,
                decimals,
                initial_supply
            ).build_transaction({
                'chainId': int(os.getenv('CHAIN_ID')),
                'gas': 100000,  # Precompile deploy gas cost
                'maxFeePerGas': max_fee,
                'maxPriorityFeePerGas': priority_fee,
                'nonce': nonce,
                'type': 2  # EIP-1559
            })
            
            # İşlemi imzala ve gönder
            signed_txn = self.wallet.account.sign_transaction(contract_txn)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # İşlem makbuzunu al
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # İşlem başarılı mı kontrol et
            if receipt['status'] == 1:
                # Deploy edilen kontratları al
                contracts = self.get_deployed_contracts()
                # En son deploy edilen kontratı bul
                if contracts:
                    latest_contract = contracts[-1]  # Son kontratı al
                    contract_address = latest_contract[1]  # addr ikinci eleman (index 1)
                    logging.info(f"{Fore.GREEN}✅ Token kontratı başarıyla deploy edildi: {contract_address}{Style.RESET_ALL}")
                    return receipt, contract_address
            
            logging.error(f"{Fore.RED}❌ Token kontratı deploy edilemedi!{Style.RESET_ALL}")
            return None, None
            
        except Exception as e:
            logging.error(f"{Fore.RED}❌ ERC20 kontratı deploy edilirken hata: {str(e)}{Style.RESET_ALL}")
            return None, None