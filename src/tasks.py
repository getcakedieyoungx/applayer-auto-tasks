import schedule
import time
import logging
from wallet import Wallet
from contracts import ContractManager

class TaskManager:
    def __init__(self):
        self.wallet = Wallet()
        self.contract_manager = ContractManager(self.wallet)
        logging.basicConfig(
            filename='../logs/bot.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def claim_tokens(self):
        # TODO: Implement faucet interaction
        pass
    
    def deploy_test_contract(self):
        try:
            result = self.contract_manager.deploy_erc20(
                "TestToken",
                "TST",
                18,
                1000000000000000000000  # 1000 tokens
            )
            if result:
                logging.info(f'Contract deployed successfully: {result["contractAddress"]}')
            else:
                logging.error('Contract deployment failed')
        except Exception as e:
            logging.error(f'Task error: {str(e)}')
    
    def run(self):
        schedule.every().day.at("10:00").do(self.claim_tokens)
        schedule.every().day.at("10:30").do(self.deploy_test_contract)
        
        while True:
            schedule.run_pending()
            time.sleep(60)