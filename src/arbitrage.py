from src.blockchain_rpc import BlockchainRpcApi
from src.coingecko import get_price
from src.hyphen_liquidity_pools import compute_amount_received, compute_received_reward, compute_transfer_fee, \
    compute_imbalance
from src.read import read_liquidity_pools, read_supported_assets


def compute_bridged_back_amount(amount):
    """
    TODO: How to estimate the bridged back amount via other bridges and how much it is going to cost
    :param amount:
    :return:
    """
    return amount * (1 - 0.01 / 100)


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
        # compute what you would get by bridging back to the fromChain using native bridges or others
        bridged_back_amount = compute_bridged_back_amount(amount_received)
        return (bridged_back_amount - amount) / 1e18, amount
    else:
        return 0, 0


def get_rpcs(liquidity_pools):
    """

    :param liquidity_pools: pd.DataFrame with 'Blockchain' and 'PoolAddress' columns
    :return:
    """
    rpcs = {}
    for index, row in liquidity_pools.iterrows():
        rpcs[row['Blockchain']] = BlockchainRpcApi(row['Blockchain'], row['PoolAddress'])
    return rpcs


def check_arbitrage_opportunities():
    """
    For all supported blockchains and assets, checks if there is an arbitrage opportunity and returns the best one
    :return:
    """
    liquidity_pools = read_liquidity_pools()
    supported_assets = read_supported_assets()
    rpcs = get_rpcs(liquidity_pools)
    max_profit = -1
    amountIn = 0.0
    best_opportunity_blockchain = ''
    best_opportunity_asset = ''
    for blockchain in rpcs.keys():
        api = rpcs[blockchain]
        for i, supported_assets_row in supported_assets.iterrows():
            asset = supported_assets_row['Address']
            asset_symbol = supported_assets_row['Asset']
            equilibrium_liquidity = api.get_equilibrium_liquidity(asset)
            liquidity = api.get_current_liquidity(asset)
            incentive_pool = api.get_rewards(asset)
            profit, amountIn = compute_profit(incentive_pool, liquidity, equilibrium_liquidity, 0)
            asset_price = get_price(asset_symbol)
            profit_in_usd = profit * asset_price
            if profit_in_usd > max_profit:
                max_profit = profit
                best_opportunity_blockchain = blockchain
                best_opportunity_asset = asset
                print('Arbitrage detected for', asset_symbol, 'on', blockchain,
                      '- Profit=$', round(profit_in_usd, 4), 'amountIn=', round(amountIn, 4))
    return max_profit, amountIn, best_opportunity_blockchain, best_opportunity_asset
