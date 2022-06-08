# encoding: utf-8

import os
from contextlib import contextmanager

from kaspy.kaspa_clients import RPCClient

from constants import DEFLATIONARY_TABLE, TOTAL_COIN_SUPPLY


class KaspaInterfaceException(Exception): pass


@contextmanager
def kaspa_connection():
    """

    :return:
    :rtype: RPCClient
    """
    cli = RPCClient()
    cli.connect(os.environ["KASPAD_HOST"], os.environ["KASPAD_PORT"])
    yield cli
    cli.close()


def get_stats():
    with kaspa_connection() as cli:
        stats = dict()
        blockdag_info = cli.request('getBlockDagInfoRequest', timeout=4)['getBlockDagInfoResponse']
        stats['block_count'] = blockdag_info['blockCount']
        stats['header_count'] = blockdag_info['headerCount']
        stats['pruning_point'] = blockdag_info['pruningPointHash']
        stats['parent_hashes'] = blockdag_info['virtualParentHashes']
        stats['tip_hashes'] = blockdag_info['tipHashes']
        stats['timestamp'] = blockdag_info['pastMedianTime']
        stats['difficulty'] = blockdag_info['difficulty']
        stats['hashrate'] = stats['difficulty'] * 2
        stats['daa_score'] = blockdag_info['virtualDaaScore']

    return stats


def get_balance(address):
    """
    Gets balance of a wallet
    :param address: kaspa address
    :return: balance in KAS
    """
    with kaspa_connection() as cli:  # type: RPCClient
        balance = cli.request("getBalanceByAddressRequest",
                              {'address': address},
                              timeout=4)

    try:
        response = balance["getBalanceByAddressResponse"]
        if "balance" in response:
            return int(response["balance"]) / 100000000
        elif not response:
            return 0
        else:
            raise KaspaInterfaceException(balance)

    except Exception:
        raise KaspaInterfaceException(balance)


def get_circulating_supply():
    stats = get_stats()
    coin_supply = _calc_circ_supply_from_daascore(int(stats["daa_score"]))
    return coin_supply


def _calc_circ_supply_from_daascore(target_daa_score):
    """
    source: https://github.com/kaspagang/kaspa_discord/blob/b8465ac8ae96dd7741aed557aaad94f0d2bd2a61/helpers.py#L40
    :param target_daa_score:
    :return:
    """
    if target_daa_score >= list(DEFLATIONARY_TABLE.values())[-1]['daa_range'].start:
        return TOTAL_COIN_SUPPLY
    coin_supply = 0
    for def_phase in DEFLATIONARY_TABLE.values():
        if target_daa_score in def_phase['daa_range']:
            coin_supply += def_phase['reward_per_daa'] * (target_daa_score - def_phase['daa_range'].start)
            break
        else:
            coin_supply += def_phase['reward_per_daa'] * (
                    def_phase['daa_range'].stop - def_phase['daa_range'].start - 1)
    return round(coin_supply)


if __name__ == '__main__':
    print(get_circulating_supply())
    # print(get_stats())
    # print(f'{get_balance("kaspa:qr7gx8g579ykhd36rvuv329fwapxv03g6myu5p4vcfzt020pzae828qp0ew8q")} KAS')
