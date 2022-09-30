import pandas as pd


def read_liquidity_pools():
    return pd.read_csv('C:/dev/hyphenArbitrage/src/resources/supported_pools.csv')


def read_supported_assets():
    return pd.read_csv('C:/dev/hyphenArbitrage/src/resources/supported_assets.csv')


def read_chain_ids():
    chain_ids = pd.read_csv('C:/dev/hyphenArbitrage/src/resources/chains.csv')
    return dict(chain_ids.values)
