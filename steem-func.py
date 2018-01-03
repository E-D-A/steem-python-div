import time
from steem import Steem
from steem.account import Account
from steem.amount import Amount
from steem.converter import Converter

steem = Steem()
pattern = '%Y-%m-%dT%H:%M:%S'

def getrsharesvalue(rshares):
    """Converts a vote's rshares value to current SBD value.

    Args:
        rshares: the rshares value of an upvote.
    Returns:
        the current SBD upvote value.
    """
    conv = Converter()
    rew_bal = float(Amount(steem.steemd.get_reward_fund()['reward_balance']).amount)
    rec_claim = float(steem.steemd.get_reward_fund()['recent_claims'])
    steemvalue = rshares * rew_bal / rec_claim
    return conv.steem_to_sbd(steemvalue)

def calculateSP(account):
    """Calculates an account's active Steem Power.

    Args:
        account: A Steem Account object.
    Returns:
        the active SP.
    """
    allSP = float(account.get('vesting_shares').rstrip(' VESTS'))
    delSP = float(account.get('delegated_vesting_shares').rstrip(' VESTS'))
    recSP = float(account.get('received_vesting_shares').rstrip(' VESTS'))
    activeSP = account.converter.vests_to_sp(allSP - delSP + recSP)
    return activeSP

def getactiveVP(account):
    """Calculates an account's active Voting Power(VP).

    Args:
        account: A Steem Account object.
    Returns:
        the active VP.
    """
    for event in account.get_account_history(-1,1000,filter_by='vote'):
        if(event['type'] == "vote"):
            if(event['voter'] == account.name):
                epochlastvote = int(time.mktime(time.strptime(event['timestamp'], pattern)))
                break
    timesincevote = int(time.time()) - epochlastvote
    VP = account.voting_power() + ((int(time.time())-epochlastvote) * (2000/86400)) / 100
    # Make sure the voting power is max 100
    if(VP > 100):
        VP = 100
    return VP

def getvotevalue(SP, VotingPower, VotingWeight):
    """Calculates the SBD value of a vote.

    Args:
        SP: The Steem Power value.
        VotingPower: The Voting Power value, percentage from 0-100.
        VotingWeight: The Voting Weight, percentage from 0-100.
    Returns:
        the upvote value in SBD.
    """
    POWER = SP / (float(Amount(steem.steemd.get_dynamic_global_properties()['total_vesting_fund_steem']).amount) \
        / float(steem.steemd.get_dynamic_global_properties()['total_vesting_shares'].rstrip(' VESTS')))
    VOTING = ((100 * VotingPower * (100 * VotingWeight) / 10000) + 49) / 50
    REW = float(Amount(steem.steemd.get_reward_fund()['reward_balance']).amount) \
        / float(steem.steemd.get_reward_fund()['recent_claims'])
    PRICE = float(Amount(steem.steemd.get_current_median_history_price()['base']).amount) \
        / float(Amount(steem.steemd.get_current_median_history_price()['quote']).amount)
    VoteValue = (POWER * VOTING * 100) * REW * PRICE
    return VoteValue

def getvoteweight(SP, VoteValue, VotingPower):
    """Calculates the Vote Weight needed to achieve a specific upvote value.

    Args:
        SP: The Steem Power value.
        VotingValue: SBD value to achieve.
        VotingPower: The Voting Power value, percentage from 0-100.
    Returns:
        the Voting Weight, percentage from 0-100.
    """
    POWER = SP / (float(Amount(steem.steemd.get_dynamic_global_properties()['total_vesting_fund_steem']).amount) \
        / float(steem.steemd.get_dynamic_global_properties()['total_vesting_shares'].rstrip(' VESTS')))
    REW = float(Amount(steem.steemd.get_reward_fund()['reward_balance']).amount) \
        / float(steem.steemd.get_reward_fund()['recent_claims'])
    PRICE = float(Amount(steem.steemd.get_current_median_history_price()['base']).amount) \
        / float(Amount(steem.steemd.get_current_median_history_price()['quote']).amount)
    VOTING = VoteValue / (POWER * 100 * REW * PRICE)
    VotingWeight = ((VOTING * 50 - 49) * 10000) / (100 * 100 * VotingPower)
    return VotingWeight
    
