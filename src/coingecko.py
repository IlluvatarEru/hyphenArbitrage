from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

coingecko_id_mapping = {
    'BICO': 'biconomy',
    'USDC': 'usd-coin',
    'USDT': 'tether',
    'ETH': 'ethereum',
    'DAI': 'dai'}


def get_price(asset):
    coingecko_id = coingecko_id_mapping[asset]
    return get_price_from_coingecko_id(coingecko_id)


def get_price_from_coingecko_id(asset_id):
    api_result = cg.get_price(ids=asset_id, vs_currencies='usd')
    return api_result[asset_id]['usd']
