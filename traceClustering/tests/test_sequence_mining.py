from traceClustering.sequence_mining.mine_fsp_closed import mine_fsp_closed
from traceClustering.sequence_mining.sequenceDB import SequenceDB

# test for mining closed frequences
# will make it a proper unittest later, this was just for quick fiddling during implementation, tests both ways of pruning

'''
tracelist = [
    ['a', 'b', 'c', 'd'],
    ['a', 'b', 'c'],
    ['b', 'c']
]
'''

'''
tracelist = [
    ['a','b','c','d','e'],
    ['a','b','c','d','e'],
    ['a','b','c','d','e'],
    ['a','b','c','d','e'],
    ['a','b','c','d','e'],
    ['a','b','d'],
    ['a','b','d'],
    ['a','b','d'],
    ['a','b','d'],
    ['a','b','d'],
    ['l','m','n','o','p','q','r','d','e','s','t','u'],
    ['l','m','n','o','p','q','r','d','e','s','t','u'],
    ['l','m','n','o','p','q','r','d','e','s','t','u'],
    ['l','m','n','o','p','q','r','d','e','s','t','u'],
    ['l','m','n','o','p','q','r','d','e','s','t','u'],
    ['l','m','n','o','p','q','r','t','s'],
    ['l','m','n','o','p','q','r','t','s'],
    ['l','m','n','o','p','q','r','t','s'],
    ['l','m','n','o','p','q','r','t','s'],
    ['l','m','n','o','p','q','r','t','s']
]
'''


tracelist = [
    ['a','b','c','d','e','f','g','h','i','j','k'],
    ['a','b','c','d','e','f','g','h','i','j','k'],
    ['a','b','c','d','e','f','g','h','i','j','k'],
    ['a','b','c','d','e','f','g','h','i','j','k'],
    ['a','b','c','d','e','f','g','h','i','j','k'],
    ['a','b','c','d','e','f','g','h','i','j'],
    ['a','b','c','d','e','f','g','h','i','j'],
    ['a','b','c','d','e','f','g','h','i','j'],
    ['a','b','c','d','e','f','g','h','i','j'],
    ['a','b','c','d','e','f','g','h','i','j'],
    ['l','m','n','o','p','q','r','s','t','u'],
    ['l','m','n','o','p','q','r','s','t','u'],
    ['l','m','n','o','p','q','r','s','t','u'],
    ['l','m','n','o','p','q','r','s','t','u'],
    ['l','m','n','o','p','q','r','s','t','u'],
    ['l','m','n','o','p','q','r','s','t'],
    ['l','m','n','o','p','q','r','s','t'],
    ['l','m','n','o','p','q','r','s','t'],
    ['l','m','n','o','p','q','r','s','t'],
    ['l','m','n','o','p','q','r','s','t']
]

sdb = SequenceDB()
sdb.initialise_db(tracelist)

print(sdb.activity_to_idx)
fsp1, fspc = mine_fsp_closed(sdb, 10)
print(fsp1)
print(fspc)