import asyncio
from web3 import Web3
from eth_account import Account
import json
import time
from typing import List, Dict

class BatchTransferTool:
    def __init__(self, rpc_url: str, private_key: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = Account.from_key(private_key)
        self.address = self.account.address
    
    async def batch_eth_transfer(self, recipients: List[Dict], gas_price_gwei: int = 20):
        """批量转账ETH"""
        nonce = self.w3.eth.get_transaction_count(self.address)
        gas_price = self.w3.to_wei(gas_price_gwei, 'gwei')
        
        transactions = []
        for i, recipient in enumerate(recipients):
            tx = {
                'to': recipient['address'],
                'value': self.w3.to_wei(recipient['amount'], 'ether'),
                'gas': 21000,
                'gasPrice': gas_price,
                'nonce': nonce + i,
            }
            
            signed_tx = self.account.sign_transaction(tx)
            transactions.append(signed_tx)
        
        # 发送交易
        tx_hashes = []
        for signed_tx in transactions:
            try:
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                tx_hashes.append(tx_hash.hex())
                print(f"Transaction sent: {tx_hash.hex()}")
                time.sleep(1)  # 避免nonce冲突
            except Exception as e:
                print(f"Error sending transaction: {e}")
        
        return tx_hashes
    
    async def batch_erc20_transfer(self, token_address: str, recipients: List[Dict]):
        """批量转账ERC20代币"""
        # ERC20 ABI (简化版)
        erc20_abi = [
            {
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]
        
        contract = self.w3.eth.contract(address=token_address, abi=erc20_abi)
        decimals = contract.functions.decimals().call()
        
        nonce = self.w3.eth.get_transaction_count(self.address)
        
        for i, recipient in enumerate(recipients):
            amount = int(recipient['amount'] * (10 ** decimals))
            
            tx = contract.functions.transfer(
                recipient['address'],
                amount
            ).build_transaction({
                'from': self.address,
                'gas': 100000,
                'gasPrice': self.w3.to_wei(20, 'gwei'),
                'nonce': nonce + i
            })
            
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(f"ERC20 transfer sent: {tx_hash.hex()}")
            time.sleep(1)
