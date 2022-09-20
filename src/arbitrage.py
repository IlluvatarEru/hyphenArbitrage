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

def check_arb(asset):
    eth = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    api = BlockchainRpcApi("Ethereum", "0x2A5c2568b10A0E826BfA892Cf21BA7218310180b", "0x")
    equilibrium_liquidity = api.get_equilibrium_liquidity(eth)
    liquidity = api.get_current_liquidity(eth)
    incentive_pool = api.get_rewards(eth)
    compute_profit(incentive_pool, liquidity, equilibrium_liquidity, 0)
    compute_imbalance(equilibrium_liquidity, liquidity) / 1e18
