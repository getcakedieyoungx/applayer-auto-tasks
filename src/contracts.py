from web3 import Web3
import json
import os
from dotenv import load_dotenv

class ContractManager:
    def __init__(self, wallet):
        load_dotenv('../config.env')
        self.wallet = wallet
        self.contract_manager_address = os.getenv('CONTRACT_MANAGER')
        
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
            }
        ]
        
        self.contract = self.wallet.w3.eth.contract(
            address=self.contract_manager_address,
            abi=self.abi
        )
    
    def deploy_erc20(self, name, symbol, decimals, initial_supply):
        try:
            tx_hash = self.contract.functions.createNewERC20Contract(
                name, symbol, decimals, initial_supply
            ).transact({'from': self.wallet.account.address})
            receipt = self.wallet.w3.eth.wait_for_transaction_receipt(tx_hash)
            return receipt
        except Exception as e:
            print(f'Error deploying ERC20: {str(e)}')
            return None