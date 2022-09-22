from pycoingecko import CoinGeckoAPI

coingecko_id_mapping = {
    'BICO': 'biconomy',
    'USDC': 'usd-coin',
    'USDT': 'tether',
    'ETH': 'ethereum',
    'DAI': 'dai'}


def get_prices(assets):
    """

    :param assets: list of str
    :return:
    """
    coingecko_ids = []
    for asset in assets:
        coingecko_ids.append(coingecko_id_mapping[asset])
    coingecko_id_mapping_reverse = {v: k for k, v in coingecko_id_mapping.items()}
    prices_with_coingecko_ids = get_price_from_coingecko_ids(",".join(coingecko_ids))
    prices = {}
    for k, v in prices_with_coingecko_ids.items():
        prices[coingecko_id_mapping_reverse[k]] = v
    return prices


def get_price_from_coingecko_id(asset_id):
    cg = CoinGeckoAPI()
    api_result = cg.get_price(ids=asset_id, vs_currencies='usd')
    return api_result[asset_id]['usd']


def get_price(asset):
    coingecko_id = coingecko_id_mapping[asset]
    return get_price_from_coingecko_id(coingecko_id)


def get_price_from_coingecko_ids(asset_ids):
    cg = CoinGeckoAPI()
    api_result = cg.get_price(ids=asset_ids, vs_currencies='usd')
    prices = {}
    for k, v in api_result.items():
        prices[k] = v['usd']
    return prices
