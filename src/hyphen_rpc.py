import requests

HYPHEN_RPC_BASE_URL = 'https://hyphen-v2-api.biconomy.io/api/v1/data/'


class HyphenRpcApi:
    def __init__(self, from_chain, to_chain, asset_from, amount):
        self.url = None
        self.from_chain = from_chain
        self.to_chain = to_chain
        self.asset_from = asset_from
        self.amount = amount
        self.base_url = HYPHEN_RPC_BASE_URL
        self.build_url()

    def set_from_chain(self, from_chain):
        self.from_chain = from_chain
        self.build_url()

    def set_to_chain(self, to_chain):
        self.to_chain = to_chain
        self.build_url()

    def set_asset(self, asset):
        self.asset_from = asset
        self.build_url()

    def set_amount(self, amount):
        self.amount = amount
        self.build_url()

    def build_url(self):
        url = self.base_url + 'transferFee?fromChainId=' + \
              str(self.from_chain) + '&toChainId=' + str(self.to_chain) + \
              '&amount=' + str(int(self.amount)) + \
              '&tokenAddress=' + self.asset_from
        self.url = url

    def request_transfer_information(self):
        result = requests.get(self.url)
        result = result.json()
        return result

    def get_reward(self):
        result = self.request_transfer_information()
        reward = float(result['reward'])
        return reward

    def get_transfer_fee(self):
        result = self.request_transfer_information()
        transfer_fee = float(result['transferFee'])
        return transfer_fee

    def get_gas_fee(self):
        result = self.request_transfer_information()
        gas_fee = float(result['gasFee'])
        return gas_fee

    def get_profit(self):
        result = self.request_transfer_information()
        received_amount = float(result['amountToGet'])
        return received_amount*1e18 - self.amount
