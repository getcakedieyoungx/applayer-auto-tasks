from web3 import Web3
import json
import os
from dotenv import load_dotenv
import logging
from colorama import Fore, Style

class ContractManager:
    def __init__(self, wallet):
        # .env dosyasını doğru yoldan yükle
        dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.env')
        load_dotenv(dotenv_path)
        
        self.wallet = wallet
        contract_manager = os.getenv('CONTRACT_MANAGER')
        if not contract_manager:
            raise ValueError("CONTRACT_MANAGER address not found in config.env")
            
        # Adresi checksum formatına dönüştür
        self.contract_manager_address = Web3.to_checksum_address(contract_manager)
        
        # Contract Manager ABI
        self.abi = [
            {
                "inputs": [
                    {"internalType": "string", "name": "name", "type": "string"},
                    {"internalType": "string", "name": "ticket", "type": "string"},
                    {"internalType": "uint8", "name": "decimals", "type": "uint8"},
                    {"internalType": "uint256", "name": "mintValue", "type": "uint256"}
                ],
                "name": "createNewERC20Contract",
                "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "getDeployedContracts",
                "outputs": [{
                    "components": [
                        {"internalType": "string", "name": "name", "type": "string"},
                        {"internalType": "address", "name": "addr", "type": "address"}
                    ],
                    "internalType": "struct ContractManager.Contract[]",
                    "name": "",
                    "type": "tuple[]"
                }],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        self.contract = self.wallet.w3.eth.contract(
            address=self.contract_manager_address,
            abi=self.abi
        )
        
        logging.info(f"{Fore.GREEN}📄 Kontrat yöneticisi başlatıldı: {self.contract_manager_address}{Style.RESET_ALL}")
    
    def get_contract_address_from_receipt(self, receipt):
        """İşlem makbuzundan kontrat adresini çıkar"""
        try:
            # Olayları kontrol et
            for log in receipt.get('logs', []):
                # Kontrat oluşturma olayını bul
                if log.get('address', '').lower() == self.contract_manager_address.lower():
                    # Kontrat adresi genelde son 20 byte'ta bulunur
                    topics = log.get('topics', [])
                    if len(topics) > 0:
                        # Son topic'ten adresi çıkar
                        address_bytes = topics[-1][-40:]  # Son 20 byte
                        return f"0x{address_bytes}"
            
            # Eğer olaylardan bulunamazsa, direkt kontrat adresini dene
            if receipt.get('contractAddress'):
                return receipt['contractAddress']
                
            return None
        except Exception as e:
            logging.error(f"{Fore.RED}❌ Kontrat adresi çıkarma hatası: {str(e)}{Style.RESET_ALL}")
            return None
    
    def deploy_erc20(self, name, symbol, decimals, initial_supply):
        try:
            logging.info(f"{Fore.YELLOW}🚀 Yeni ERC20 kontratı deploy ediliyor: {name} ({symbol}){Style.RESET_ALL}")
            
            # Kontrat fonksiyonunu hazırla
            function = self.contract.functions.createNewERC20Contract(
                name, symbol, decimals, initial_supply
            )
            
            # Gas tahmini
            gas_estimate = function.estimate_gas({'from': self.wallet.account.address})
            
            # İşlem verilerini hazırla
            transaction = {
                'to': self.contract_manager_address,
                'data': function._encode_transaction_data(),
                'gas': gas_estimate
            }
            
            # İşlemi imzala ve gönder
            receipt = self.wallet.sign_and_send_transaction(transaction)
            
            if receipt and receipt.get('status') == 1:
                # Kontrat adresini bul
                contract_address = self.get_contract_address_from_receipt(receipt)
                if contract_address:
                    logging.info(f"{Fore.GREEN}✅ ERC20 kontratı başarıyla deploy edildi: {contract_address}{Style.RESET_ALL}")
                else:
                    logging.warning(f"{Fore.YELLOW}⚠️ Kontrat deploy edildi fakat adres bulunamadı{Style.RESET_ALL}")
            else:
                logging.error(f"{Fore.RED}❌ ERC20 kontrat deployment başarısız{Style.RESET_ALL}")
                
            return receipt
            
        except Exception as e:
            logging.error(f"{Fore.RED}❌ ERC20 kontrat deployment hatası: {str(e)}{Style.RESET_ALL}")
            return None
    
    def get_deployed_contracts(self):
        try:
            contracts = self.contract.functions.getDeployedContracts().call()
            logging.info(f"{Fore.CYAN}📋 {len(contracts)} adet deploy edilmiş kontrat bulundu{Style.RESET_ALL}")
            return contracts
        except Exception as e:
            logging.error(f"{Fore.RED}❌ Deploy edilmiş kontratları alma hatası: {str(e)}{Style.RESET_ALL}")
            return []