BASE_DIVISOR = 10000000000


def compute_amount_received(amount, transfer_fee, gas_fee):
    return amount - transfer_fee - gas_fee


def compute_received_reward(amount, incentive_pool, liquidity, equilibrium_liquidity):
    """

    :param amount:
    :param incentive_pool:
    :param liquidity:
    :param equilibrium_liquidity:
    :return: given the incentive pool and the imbalance the reward depends on how much we are bridging
    """
    imbalance = compute_imbalance(equilibrium_liquidity, liquidity)
    if imbalance > 0:
        if amount >= imbalance:
            reward = incentive_pool
        else:
            reward = amount * incentive_pool / imbalance
    else:
        reward = 0
    return reward


def compute_transfer_fee(amount, liquidity, equilibrium_liquidity, max_fee, equilibrium_fee, excess_state_transfer_fee,
                         depth=2):
    """

    :param excess_state_transfer_fee:
    :param amount:
    :param liquidity:
    :param equilibrium_liquidity:
    :param max_fee:
    :param equilibrium_fee:
    :param depth:
    :return:
    """
    print("amount", amount)
    print("liquidity", liquidity)
    print("equilibrium_liquidity", equilibrium_liquidity)
    print("max_fee", max_fee)
    print("equilibrium_fee", equilibrium_fee)
    print("excess_state_transfer_fee", excess_state_transfer_fee)
    resulting_liquidity = liquidity - amount
    if resulting_liquidity > equilibrium_liquidity:
        transfer_fee_percentage = excess_state_transfer_fee
    else:
        n = equilibrium_fee * max_fee * equilibrium_liquidity ** 2
        d = equilibrium_fee * equilibrium_liquidity ** depth + \
            (max_fee - equilibrium_fee) * resulting_liquidity ** depth
        if d == 0:
            transfer_fee_percentage = 0
        else:
            transfer_fee_percentage = n / d
    transfer_fee = (amount * transfer_fee_percentage) / BASE_DIVISOR
    return transfer_fee


def compute_imbalance(equilibrium_liquidity, liquidity):
    return equilibrium_liquidity - liquidity
