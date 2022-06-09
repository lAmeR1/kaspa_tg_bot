# encoding: utf-8
import re

from constants import DEFLATIONARY_TABLE


def hashrate_to_int(str_hashrate: str):
    val, suffix = extract_hashrate(str_hashrate)
    if suffix == 'KH':
        return val * 1_000
    elif suffix == 'MH':
        return val * 1_000_000
    elif suffix == 'GH':
        return val * 1_000_000_000
    elif suffix == 'TH':
        return val * 1_000_000_000_000
    elif suffix == 'PH':
        return val * 1_000_000_000_000_000
    elif suffix == 'EH':
        return val * 1_000_000_000_000_000_000
    elif suffix == 'H':
        return val


def extract_hashrate(str_hashrate):
    val = float(re.findall(r'\d+(?:\.\d+)?', str_hashrate)[0])
    for suf in ['KH', 'MH', 'GH', 'TH', 'PH', 'EH', 'H']:
        if suf.lower() in str_hashrate.lower():
            suffix = suf
            break
    return val, suffix


def percent_of_network(miner_hashrate, network_hashrate):
    if miner_hashrate <= network_hashrate:
        return miner_hashrate / network_hashrate
    else:
        return (miner_hashrate) / (miner_hashrate + network_hashrate)


def rewards_in_range(daa_start, daa_end):
    if daa_start >= list(DEFLATIONARY_TABLE.values())[-1]['daa_range'].start:
        return 0
    mining_rewards = 0
    for i, def_phase in enumerate(DEFLATIONARY_TABLE.values()):
        if daa_start >= def_phase['daa_range'].start:
            start_phase = i
    for def_phase in list(DEFLATIONARY_TABLE.values())[start_phase:]:
        if def_phase['daa_range'].start <= daa_end < def_phase['daa_range'].stop and def_phase[
            'daa_range'].start <= daa_start < def_phase['daa_range'].stop:
            mining_rewards = (daa_end - daa_start) * def_phase['reward_per_daa']
            break
        elif def_phase['daa_range'].start <= daa_start < def_phase['daa_range'].stop:
            mining_rewards += (def_phase['daa_range'].stop - daa_start - 1) * def_phase['reward_per_daa']
        elif def_phase['daa_range'].start <= daa_end < def_phase['daa_range'].stop:
            mining_rewards += (daa_end - def_phase['daa_range'].start) * def_phase['reward_per_daa']
            break
        else:
            mining_rewards += (def_phase['daa_range'].stop - def_phase['daa_range'].start - 1) * def_phase[
                'reward_per_daa']
    return mining_rewards


def get_mining_rewards(current_daa_score, percent_of_network):
    rewards = dict()
    rewards['secound'] = rewards_in_range(current_daa_score, current_daa_score + 1) * percent_of_network
    rewards['minute'] = rewards_in_range(current_daa_score, current_daa_score + 60) * percent_of_network
    rewards['hour'] = rewards_in_range(current_daa_score, current_daa_score + 60 * 60) * percent_of_network
    rewards['day'] = rewards_in_range(current_daa_score, current_daa_score + 60 * 60 * 24) * percent_of_network
    rewards['week'] = rewards_in_range(current_daa_score, current_daa_score + 60 * 60 * 24 * 7) * percent_of_network
    rewards['month'] = rewards_in_range(current_daa_score,
                                        current_daa_score + 60 * 60 * 24 * (365.25 / 12)) * percent_of_network
    rewards['year'] = rewards_in_range(current_daa_score,
                                       current_daa_score + 60 * 60 * 24 * (365.25)) * percent_of_network
    return rewards


MINING_CALC = lambda rewards: f'''
  KAS / sec   :  {rewards['secound']:,}
  KAS / min   :  {round(rewards['minute']):,}
  KAS / hour  :  {round(rewards['hour']):,}
  KAS / day   :  {round(rewards['day']):,}
  KAS / week  :  {round(rewards['week']):,}
  KAS / month :  {round(rewards['month']):,}
  KAS / year  :  {round(rewards['year']):,}'''
