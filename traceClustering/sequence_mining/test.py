from mine_fsp_closed import mine_fsp_closed
from sequenceDB import SequenceDB

# test for mining closed frequences
# will make it a proper unittest later, this was just for quick fiddling during implementation, tests both ways of pruning
tracelist = [
    ['a', 'b', 'c', 'd'],
    ['a', 'b', 'c'],
    ['b', 'c']
]

sdb = SequenceDB()
sdb.initialise_db(tracelist)

print(sdb.activity_to_idx)
fsp1, fspc = mine_fsp_closed(sdb, 2)
print(fsp1)
print(fspc)