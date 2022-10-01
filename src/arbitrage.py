from src.blockchain_rpc import BlockchainRpcApi
from src.coingecko import get_prices
from src.hyphen_liquidity_pools import compute_amount_received, compute_received_reward, compute_transfer_fee, \
    compute_imbalance
from src.hyphen_rpc import HyphenRpcApi
from src.read import read_liquidity_pools, read_supported_assets, read_chain_ids


def get_wallet_balance_eth():
    """

    :return: int, wallet balance in ETH
    """
    return int(1e18 * 10)


def compute_bridged_back_amount(amount):
    """
    TODO: How to estimate the bridged back amount via other bridges and how much it is going to cost
    :param amount:
    :return:
    """
    return amount * (1 - 0.0 / 100)


def compute_max_profit(incentive_pool,
                       liquidity_from, equilibrium_liquidity_from,
                       liquidity_to, equilibrium_liquidity_to,
                       gas_fee, max_fee=0,
                       equilibrium_fee=0,
                       excess_state_transfer_fee=0,
                       depth=2):
    amount = compute_imbalance(equilibrium_liquidity_from, liquidity_from)
    profit = compute_profit(amount, incentive_pool,
                            liquidity_from, equilibrium_liquidity_from,
                            liquidity_to, equilibrium_liquidity_to,
                            gas_fee, max_fee, equilibrium_fee,
                            excess_state_transfer_fee,
                            depth)
    return profit, amount


def compute_profit(amount, incentive_pool,
                   liquidity_from, equilibrium_liquidity_from,
                   liquidity_to, equilibrium_liquidity_to,
                   gas_fee, max_fee=0,
                   equilibrium_fee=0,
                   excess_state_transfer_fee=0,
                   depth=2):
    if amount > 0:
        # compute the reward
        reward = compute_received_reward(amount, incentive_pool, liquidity_from, equilibrium_liquidity_from)
        # compute the transfer fee from TO POOL
        transfer_fee = compute_transfer_fee(amount, liquidity_to, equilibrium_liquidity_to, max_fee, equilibrium_fee,
                                            excess_state_transfer_fee, depth)
        # print("reward", reward)
        # print("transfer_fee", '{:.20f}'.format(transfer_fee))
        # compute the amount received on the toChain
        amount_received = compute_amount_received(amount + reward, transfer_fee, gas_fee)
        # print("amount_received", amount_received)
        # compute what you would get by bridging back to the fromChain using native bridges or others
        bridged_back_amount = compute_bridged_back_amount(amount_received)
        return bridged_back_amount - amount
    else:
        return 0


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
    chain_ids = read_chain_ids()
    rpcs = get_rpcs(liquidity_pools)
    blockchains = list(rpcs.keys())
    max_profit = 0.0
    amount_in = 0.0
    best_opportunity_blockchain = ''
    best_opportunity_asset = ''
    assets = supported_assets['Asset'].tolist()
    asset_prices = get_prices(assets)
    wallet_balance_eth = get_wallet_balance_eth()
    wallet_balance_usdc = wallet_balance_eth * asset_prices["USDC"]
    for blockchain_from in blockchains:
        api_from = rpcs[blockchain_from]
        chain_id_from = chain_ids[blockchain_from]
        blockchains_to = [chain for chain in blockchains if chain != blockchain_from]
        supported_assets_from = supported_assets.loc[
            supported_assets['Blockchain'] == blockchain_from, 'Asset'].unique()
        for blockchain_to in blockchains_to:
            api_to = rpcs[blockchain_to]
            chain_id_to = chain_ids[blockchain_to]
            supported_assets_to = supported_assets.loc[
                supported_assets['Blockchain'] == blockchain_to, 'Asset'].unique()
            supported_assets_bridge = list(set(supported_assets_from) & set(supported_assets_to))
            for asset_symbol in supported_assets_bridge:
                supported_asset = supported_assets.loc[supported_assets['Asset'] == asset_symbol]
                asset_from = supported_asset.loc[supported_asset['Blockchain'] == blockchain_from, 'Address'].values[0]
                asset_to = supported_asset.loc[supported_asset['Blockchain'] == blockchain_to, 'Address'].values[0]
                asset_price = asset_prices[asset_symbol]
                # blockchain-from data
                equilibrium_liquidity_from = api_from.get_equilibrium_liquidity(asset_from)
                liquidity_from = api_from.get_current_liquidity(asset_from)
                incentive_pool = api_from.get_rewards(asset_from)

                # blockchain-to data
                equilibrium_liquidity_to = api_to.get_equilibrium_liquidity(asset_to)
                liquidity_to = api_to.get_current_liquidity(asset_to)
                tokens_info_to = api_to.get_tokens_info(asset_to)
                excess_state_transfer_fee_to = api_to.get_excess_state_transfer_fee(asset_to)
                # TODO: Estimate gas
                baseGas = api_to.get_base_gas()
                gas = tokens_info_to['transferOverhead'] + baseGas
                hypen_rpc = HyphenRpcApi(chain_id_from, chain_id_to, asset_from, 1)
                true_gas = hypen_rpc.get_gas_fee() * 1e18

                profit_for_max_amount_in, max_amount_in = compute_max_profit(incentive_pool,
                                                                             liquidity_from,
                                                                             equilibrium_liquidity_from,
                                                                             liquidity_to,
                                                                             equilibrium_liquidity_to,
                                                                             gas_fee=true_gas,
                                                                             max_fee=tokens_info_to['maxFee'],
                                                                             equilibrium_fee=tokens_info_to[
                                                                                 'equilibriumFee'],
                                                                             excess_state_transfer_fee=excess_state_transfer_fee_to)
                wallet_balance_asset = wallet_balance_usdc / asset_price
                if max_amount_in > wallet_balance_asset:
                    profit = compute_profit(wallet_balance_asset, incentive_pool,
                                            liquidity_from, equilibrium_liquidity_from,
                                            liquidity_to, equilibrium_liquidity_to,
                                            gas_fee=0,
                                            max_fee=tokens_info_to['maxFee'],
                                            equilibrium_fee=tokens_info_to['equilibriumFee'],
                                            excess_state_transfer_fee=excess_state_transfer_fee_to)
                    amount_in = wallet_balance_asset
                else:
                    profit = profit_for_max_amount_in
                    amount_in = max_amount_in
                profit /= 1e18
                amount_in /= 1e18
                profit_in_usd = profit * asset_price
                if profit_in_usd > max_profit:
                    max_profit = profit_in_usd
                    best_opportunity_blockchain = blockchain_from
                    best_opportunity_asset = asset_from
                    print('New best arbitrage detected for', asset_symbol, 'on', blockchain_from + ":",
                          '\n    - Profit=$', round(profit_in_usd, 4),
                          '\n    - Amount In=', round(amount_in, 4), asset_symbol,
                          "~$", round(amount_in * asset_price, 0))
    return max_profit, amount_in, best_opportunity_blockchain, best_opportunity_asset
