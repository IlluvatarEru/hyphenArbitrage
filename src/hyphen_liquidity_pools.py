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
            return incentive_pool
        else:
            return amount * incentive_pool / imbalance
    else:
        return 0


def compute_transfer_fee(amount, liquidity, equilibrium_liquidity, max_fee, equilibrium_fee, depth):
    """

    :param amount:
    :param liquidity:
    :param equilibrium_liquidity:
    :param max_fee:
    :param equilibrium_fee:
    :param depth:
    :return:
    """
    resulting_liquidity = liquidity - amount
    return (max_fee * equilibrium_fee * equilibrium_liquidity ** depth) / \
           (equilibrium_fee * equilibrium_liquidity ** depth +
            (max_fee - equilibrium_fee) * resulting_liquidity ** depth)


def compute_imbalance(equilibrium_liquidity, liquidity):
    return equilibrium_liquidity - liquidity
