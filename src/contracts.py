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
        self.contract_manager_address = Web3.to_checksum_address(os.getenv('CONTRACT_MANAGER'))
        
        # ContractManager ABI
        self.contract_manager_abi = [
            {"inputs":[],"name":"getDeployedContracts","outputs":[{"internalType":"address[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"},
            {"inputs":[{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"symbol","type":"string"},{"internalType":"uint8","name":"decimals","type":"uint8"},{"internalType":"uint256","name":"initialSupply","type":"uint256"}],"name":"deployERC20","outputs":[],"stateMutability":"nonpayable","type":"function"}
        ]
        
        # ERC20 ABI
        self.erc20_abi = [
            {"inputs":[{"internalType":"string","name":"name_","type":"string"},{"internalType":"string","name":"symbol_","type":"string"},{"internalType":"uint8","name":"decimals_","type":"uint8"},{"internalType":"uint256","name":"initialSupply_","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},
            {"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
            {"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
            {"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},
            {"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}
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

    def get_contract_address_from_receipt(self, receipt):
        """İşlem makbuzundan kontrat adresini çıkarır"""
        try:
            # Debug logları
            logging.debug(f"İşlem makbuzu detayları:")
            logging.debug(json.dumps(dict(receipt), indent=2, default=str))
            
            # Kontrat adresi çıkarma yöntemleri
            contract_address = None
            
            # 1. Logs'lardan kontrol
            if receipt.get('logs'):
                for log in receipt['logs']:
                    if log.get('address'):
                        contract_address = log['address']
                        logging.debug(f"Kontrat adresi log kayıtlarından bulundu: {contract_address}")
                        break
            
            # 2. contractAddress alanından kontrol
            if not contract_address and receipt.get('contractAddress'):
                contract_address = receipt['contractAddress']
                logging.debug(f"Kontrat adresi 'contractAddress' alanından bulundu: {contract_address}")
            
            # 3. to alanından kontrol
            if not contract_address and receipt.get('to'):
                contract_address = receipt['to']
                logging.debug(f"Kontrat adresi 'to' alanından bulundu: {contract_address}")
            
            if contract_address:
                # Adresi checksum formatına çevir
                contract_address = Web3.to_checksum_address(contract_address)
                logging.info(f"{Fore.GREEN}✅ Kontrat adresi başarıyla çıkarıldı: {contract_address}{Style.RESET_ALL}")
                return contract_address
            else:
                logging.warning(f"{Fore.YELLOW}⚠️ Kontrat adresi bulunamadı. İşlem beklemede olabilir.{Style.RESET_ALL}")
                return None
                
        except Exception as e:
            logging.error(f"{Fore.RED}❌ Kontrat adresi çıkarılırken hata: {str(e)}{Style.RESET_ALL}")
            return None

    def deploy_erc20(self, name, symbol, decimals, initial_supply):
        """Yeni bir ERC20 token kontratı deploy eder"""
        try:
            logging.info(f"{Fore.CYAN}🚀 Yeni ERC20 kontratı deploy ediliyor: {name} ({symbol}){Style.RESET_ALL}")
            
            # Deploy işlemini başlat
            nonce = self.w3.eth.get_transaction_count(self.wallet.account.address)
            
            # Gas hesaplamaları
            base_fee = self.w3.eth.get_block('latest')['baseFeePerGas']
            priority_fee = 2_000_000_000  # 2 Gwei
            max_fee = base_fee + priority_fee
            
            # %10 buffer ekle
            max_fee = int(max_fee * 1.1)
            
            contract_txn = self.contract.functions.deployERC20(
                name,
                symbol,
                decimals,
                initial_supply
            ).build_transaction({
                'chainId': int(os.getenv('CHAIN_ID')),
                'gas': 3000000,
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
            
            # Kontrat adresini çıkar
            contract_address = self.get_contract_address_from_receipt(receipt)
            
            # İşlem başarılı oldu mu?
            if receipt['status'] == 1:  # status kontrolü düzeltildi
                logging.info(f"{Fore.GREEN}✅ Token kontratı başarıyla deploy edildi!{Style.RESET_ALL}")
                logging.info(f"{Fore.GREEN}🔗 TX Hash: {receipt['transactionHash'].hex()}{Style.RESET_ALL}")
                return receipt, contract_address
            else:
                logging.error(f"{Fore.RED}❌ Token kontratı deploy edilemedi!{Style.RESET_ALL}")
                return None, None
            
        except Exception as e:
            logging.error(f"{Fore.RED}❌ ERC20 kontratı deploy edilirken hata: {str(e)}{Style.RESET_ALL}")
            return None, None