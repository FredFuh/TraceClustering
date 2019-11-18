from sequenceDB import log_to_sdb
from mine_fsp_closed import mine_fsp_closed

def mine_fsp(log, min_sup):
    ''' 
    Mines the frequent sequent patterns (fsp's) of length 1,2 and the closed fsp's for the given event log and minimum support.
    The respective fsp's are organized in lists of tuples, where the first entry is the fsp and the second is its absolute support.
    
    input: pm4py EventLog object, min_sup (absolute)
    
    output: (fsp_1, fsp_2, fsp_c)
    '''
    
    sdb = log_to_sdb(log)

    # As a byproduct, frequent subsequences of length 1 are computed during the computation of closed fsp's
    fsp_1, fsp_c = mine_fsp_closed(sdb, min_sup)
    fsp_2 = mine_fsp_2(sdb, min_sup)

    return fsp_1, fsp_2, fsp_c

# stub
def mine_fsp_2(sdb, min_sup):
    return []

#stub
def mine_fsp_from_sample(log, min_sup, training_set_fraction=0.5):
    pass