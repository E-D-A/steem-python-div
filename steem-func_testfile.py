from steem.account import Account
import steem_func

account = Account('danielsaori')

SP = steem_func.calculateSP(account)
print('Steem Power:', int(SP), 'SP')
VP = steem_func.getactiveVP(account)
print('Voting Power:', int(VP), '%')
VoteValue = steem_func.getvotevalue(SP, VP, 100)
print('Max vote value with Steem Power and Voting Power above:', round(VoteValue,3), 'SBD')
VotingWeight = steem_func.getvoteweight(SP, VoteValue, VP)
print('Voting Weight needed:', int(round(VotingWeight,0)), '%')
