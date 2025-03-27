import schedule
import time
import logging
import os
from wallet import Wallet
from contracts import ContractManager

class TaskManager:
    def __init__(self):
        self.wallet = Wallet()
        self.contract_manager = ContractManager(self.wallet)
        self.stats = {
            "tokens_claimed": 0,
            "contracts_deployed": 0,
            "errors": 0
        }
        
    def claim_tokens(self):
        try:
            logging.info('🎁 Faucet\'ten token talep ediliyor...')
            # TODO: Faucet API entegrasyonu
            self.stats["tokens_claimed"] += 1
            logging.info('✅ Token talebi başarılı!')
        except Exception as e:
            logging.error(f'❌ Token talep hatası: {str(e)}')
            self.stats["errors"] += 1
    
    def deploy_test_contract(self):
        try:
            logging.info('🚀 Test kontratı deploy ediliyor...')
            result = self.contract_manager.deploy_erc20(
                "TestToken",
                "TST",
                18,
                1000000000000000000000  # 1000 tokens
            )
            if result:
                self.stats["contracts_deployed"] += 1
                logging.info(f'✅ Kontrat başarıyla deploy edildi: {result.get("contractAddress")}')
            else:
                logging.error('❌ Kontrat deployment başarısız')
                self.stats["errors"] += 1
        except Exception as e:
            logging.error(f'❌ Görev hatası: {str(e)}')
            self.stats["errors"] += 1
    
    def run(self):
        logging.info('🤖 Bot başlatıldı...')
        
        # Görevleri zamanla
        schedule.every().day.at("10:00").do(self.claim_tokens)
        schedule.every().day.at("10:30").do(self.deploy_test_contract)
        
        # İlk çalıştırmada hemen başlat
        self.claim_tokens()
        self.deploy_test_contract()
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)
            except Exception as e:
                logging.error(f'❌ Runtime hatası: {str(e)}')
                self.stats["errors"] += 1
                time.sleep(60)  # Hata durumunda 1 dakika bekle