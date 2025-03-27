from web3 import Web3
import json
import os
from dotenv import load_dotenv
import logging
from colorama import Fore, Style
import time

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
    
    def get_contract_address_from_receipt(self, receipt, token_name):
        """İşlem makbuzundan kontrat adresini çıkar"""
        try:
            # İlk olarak son deploy edilen kontratları kontrol et
            before_contracts = set(c[1] for c in self.get_deployed_contracts())
            time.sleep(2)  # Blockchain'in güncellemesi için kısa bir bekleme
            after_contracts = set(c[1] for c in self.get_deployed_contracts())
            
            # Yeni eklenen kontratı bul
            new_contracts = after_contracts - before_contracts
            if len(new_contracts) == 1:
                new_contract = list(new_contracts)[0]
                logging.info(f"{Fore.GREEN}✨ Yeni kontrat adresi bulundu (liste karşılaştırma): {new_contract}{Style.RESET_ALL}")
                return new_contract
            
            # Eğer direkt kontrat adresi varsa
            if receipt.get('contractAddress'):
                addr = receipt['contractAddress']
                logging.info(f"{Fore.GREEN}✨ Yeni kontrat adresi bulundu (receipt): {addr}{Style.RESET_ALL}")
                return addr
            
            # Olayları kontrol et
            for log in receipt.get('logs', []):
                # Debug: Her log'u göster
                logging.debug(f"Log inceleniyor: {log}")
                
                # Kontrat oluşturma olayını bul
                if log.get('address', '').lower() == self.contract_manager_address.lower():
                    topics = log.get('topics', [])
                    if len(topics) > 0:
                        # Son topic'ten adresi çıkar
                        address_bytes = topics[-1][-40:]
                        addr = f"0x{address_bytes}"
                        logging.info(f"{Fore.GREEN}✨ Yeni kontrat adresi bulundu (log): {addr}{Style.RESET_ALL}")
                        return addr
                
                # Data'dan kontrat adresini çıkarmayı dene
                data = log.get('data', '')
                if len(data) >= 42:  # En az bir adres uzunluğunda
                    potential_addresses = [data[i:i+42] for i in range(0, len(data)-40, 2) if data[i:i+2] == '0x']
                    for addr in potential_addresses:
                        if Web3.is_address(addr):
                            logging.info(f"{Fore.GREEN}✨ Yeni kontrat adresi bulundu (data): {addr}{Style.RESET_ALL}")
                            return addr
            
            # Son çare: Tüm kontratları tara
            all_contracts = self.get_deployed_contracts()
            for contract in all_contracts:
                if contract[0] == token_name:  # İsim eşleşmesi
                    logging.info(f"{Fore.GREEN}✨ Yeni kontrat adresi bulundu (isim eşleşmesi): {contract[1]}{Style.RESET_ALL}")
                    return contract[1]
            
            logging.warning(f"{Fore.YELLOW}⚠️ Kontrat adresi bulunamadı{Style.RESET_ALL}")
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
                contract_address = self.get_contract_address_from_receipt(receipt, name)
                if contract_address:
                    logging.info(f"{Fore.GREEN}✅ ERC20 kontratı başarıyla deploy edildi: {contract_address}{Style.RESET_ALL}")
                else:
                    logging.warning(f"{Fore.YELLOW}⚠️ Kontrat deploy edildi fakat adres bulunamadı{Style.RESET_ALL}")
            else:
                logging.error(f"{Fore.RED}❌ ERC20 kontrat deployment başarısız{Style.RESET_ALL}")
                
            return receipt, contract_address
            
        except Exception as e:
            logging.error(f"{Fore.RED}❌ ERC20 kontrat deployment hatası: {str(e)}{Style.RESET_ALL}")
            return None, None
    
    def get_deployed_contracts(self):
        try:
            contracts = self.contract.functions.getDeployedContracts().call()
            logging.info(f"{Fore.CYAN}📋 {len(contracts)} adet deploy edilmiş kontrat bulundu{Style.RESET_ALL}")
            return contracts
        except Exception as e:
            logging.error(f"{Fore.RED}❌ Deploy edilmiş kontratları alma hatası: {str(e)}{Style.RESET_ALL}")
            return []