import pandas as pd
import matplotlib.pyplot as plt

from src.blockchain_rpc import BlockchainRpcApi


def compute_amount_received(amount, transfer_fee, gas_fee):
    return amount - transfer_fee - gas_fee


def compute_received_reward(amount, incentive_pool, liquidity, equilibrium_liquidity):
    imbalance = equilibrium_liquidity - liquidity
    if imbalance > 0:
        if amount >= imbalance:
            return incentive_pool
        else:
            return amount * incentive_pool / imbalance
    else:
        return 0


def compute_transfer_fee(amount, liquidity, equilibrium_liquidity, max_fee, equilibrium_fee, depth):
    resulting_liquidity = liquidity - amount
    return (max_fee * equilibrium_fee * equilibrium_liquidity ** depth) / (
            equilibrium_fee * equilibrium_liquidity ** depth + (
            max_fee - equilibrium_fee) * resulting_liquidity ** depth)


def compute_bridged_back_amount(amount):
    return amount * (1 - 0.01 / 100)


def compute_imbalance(equilibrium_liquidity, liquidity):
    return equilibrium_liquidity - liquidity


def compute_profit(incentive_pool, liquidity, equilibrium_liquidity, gas_fee, max_fee=0.1, equilibrium_fee=0.001,
                   depth=2):
    amount = compute_imbalance(equilibrium_liquidity, liquidity)
    if amount > 0:
        # compute the reward
        reward = compute_received_reward(amount, incentive_pool, liquidity, equilibrium_liquidity)
        # compute the transfer fee
        transfer_fee = compute_transfer_fee(amount, liquidity, equilibrium_liquidity, max_fee, equilibrium_fee, depth)
        # compute the amount received on the toChain
        amount_received = compute_amount_received(amount + reward, transfer_fee, gas_fee)
        # compute what you would get by brdiging back to the fromChain using native bridges or others
        bridged_back_amount = compute_bridged_back_amount(amount_received)
        return bridged_back_amount - amount
    else:
        return 0


def read_liquidity_pools():
    return pd.read_csv("C:/dev/hyphenArbitrage/src/resources/supported_pools.csv")


def read_supported_assets():
    return pd.read_csv("C:/dev/hyphenArbitrage/src/resources/supported_assets.csv")


def get_rpcs(liquidity_pools):
    rpcs = {}
    for index, row in liquidity_pools.iterrows():
        rpcs[row["Blockchain"]] = BlockchainRpcApi(row["Blockchain"], row["PoolAddress"])
    return rpcs


def check_arbs():
    liquidity_pools = read_liquidity_pools()
    supported_assets = read_supported_assets()
    rpcs = get_rpcs(liquidity_pools)
    max_profit = -1
    best_opportunity_blockchain = ''
    best_opportunity_asset = ''
    for blockchain in rpcs.keys():
        api = rpcs[blockchain]
        for i, supported_assets_row in supported_assets.iterrows():
            asset = supported_assets_row["Address"]
            equilibrium_liquidity = api.get_equilibrium_liquidity(asset)
            liquidity = api.get_current_liquidity(asset)
            incentive_pool = api.get_rewards(asset)
            profit = compute_profit(incentive_pool, liquidity, equilibrium_liquidity, 0)
            # TODO: get price to fiat to compare profits
            profit_in_usd = profit
            if profit_in_usd > max_profit:
                max_profit = profit
                best_opportunity_blockchain = blockchain
                best_opportunity_asset = asset
                print("Arbitrage detected for", supported_assets_row["Asset"], "on", blockchain, "- Profit=$",
                      round(profit_in_usd / 1e18, 4))
    return max_profit, best_opportunity_blockchain, best_opportunity_asset


def check_arb(asset):
    eth = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    api = BlockchainRpcApi("Ethereum", "0x2A5c2568b10A0E826BfA892Cf21BA7218310180b", "0x")
    equilibrium_liquidity = api.get_equilibrium_liquidity(eth)
    liquidity = api.get_current_liquidity(eth)
    incentive_pool = api.get_rewards(eth)
    compute_profit(incentive_pool, liquidity, equilibrium_liquidity, 0)
    compute_imbalance(equilibrium_liquidity, liquidity) / 1e18
