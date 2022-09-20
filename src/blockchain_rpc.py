import json
from pathlib import Path

from web3 import Web3

from src.constants import PATH_TO_PASSWORDS, PATH_TO_DATA


class BlockchainRpcApi:
    def __init__(self, blockchain, liquidity_pool, wallet):
        self.liquidity_pool_contract = None
        self.liquidity_provider_contract = None
        self.w3 = None
        self.url = None
        self.blockchain = blockchain
        self.liquidity_pool = liquidity_pool
        self.wallet = wallet
        self.key = Path(PATH_TO_PASSWORDS + 'POKT_KEY.txt').read_text().replace('\n', '')
        self.liquidity_pool_abi = json.load(open(PATH_TO_DATA + 'liquidity_pool_abi.json'))
        self.liquidity_provider_abi = json.load(open(PATH_TO_DATA + 'liquidity_provider_abi.json'))
        self.init_w3()
        self.create_liquidity_pool_contract()
        self.create_liquidity_provider_contract()

    def init_w3(self):
        if self.blockchain == 'Arbitrum':
            self.url = self.get_alchemy_gateway()
        else:
            self.url = self.get_pocket_gateway()
        w3 = Web3(Web3.HTTPProvider(self.url))
        self.w3 = w3

    def get_alchemy_gateway(self):
        if self.blockchain == 'Arbitrum':
            return 'https://arb-mainnet.g.alchemy.com/v2/HEW23KYOv2NUQP8HWR6DtoKSL74bSgwb'
        else:
            raise Exception('Blockchain not supported:', self.blockchain)

    def get_pocket_gateway(self):
        if self.blockchain == 'Polygon':
            blockchain_gateway = 'poly'
        elif self.blockchain == 'Avalanche':
            blockchain_gateway = 'avax'
        elif self.blockchain == 'Fantom':
            blockchain_gateway = 'fantom'
        elif self.blockchain == 'Moonbeam':
            blockchain_gateway = 'moonbeam'
        elif self.blockchain == 'Moonriver':
            blockchain_gateway = 'moonriver'
        elif self.blockchain == 'BSC':
            blockchain_gateway = 'bsc'
        elif self.blockchain == 'Fuse':
            blockchain_gateway = 'fuse'
        elif self.blockchain == 'Ethereum':
            blockchain_gateway = 'eth'
        elif self.blockchain == 'Optimism':
            blockchain_gateway = 'optimism'
        else:
            raise Exception('Blockchain not supported:', self.blockchain)
        return 'https://' + blockchain_gateway + '-mainnet.gateway.pokt.network/v1/lb/' + self.key

    def create_liquidity_pool_contract(self):
        self.liquidity_pool_contract = self.w3.eth.contract(address=self.liquidity_pool, abi=self.liquidity_pool_abi)

    def get_current_liquidity(self, asset_address):
        return self.liquidity_pool_contract.functions.getCurrentLiquidity(asset_address).call()

    def get_rewards(self, asset_address):
        return self.liquidity_pool_contract.functions.incentivePool(asset_address).call()

    def get_liquidity_provider(self):
        return self.liquidity_pool_contract.functions.liquidityProviders().call()

    def create_liquidity_provider_contract(self):
        self.liquidity_provider_contract = self.w3.eth.contract(address=self.get_liquidity_provider(),
                                                                abi=self.liquidity_provider_abi)

    def get_equilibrium_liquidity(self, asset_address):
        return self.liquidity_provider_contract.functions.getSuppliedLiquidityByToken(asset_address).call()

