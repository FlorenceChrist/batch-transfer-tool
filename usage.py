async def main():
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    tool = BatchTransferTool(config['rpc_url'], config['private_key'])
    
    # 批量转账ETH
    await tool.batch_eth_transfer(config['recipients'])
    
    # 批量转账ERC20
    # await tool.batch_erc20_transfer("0xA0b86a33E6441b0b5C4C1B89DfC2FbB4e0A0b26D", config['recipients'])

if __name__ == "__main__":
    asyncio.run(main())
