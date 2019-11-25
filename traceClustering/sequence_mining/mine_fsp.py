from traceClustering.sequence_mining.sequenceDB import log_to_sdb
from traceClustering.sequence_mining.mine_fsp_closed import mine_fsp_closed, get_first_item_or_none, build_sils, vil_compute_support
from pm4py.objects.log.log import EventLog
from math import ceil

def mine_fsp(log, min_sup):
    ''' 
    Mines the frequent sequent patterns (fsp's) of length 1,2 and the closed fsp's for the given event log and minimum support.
    The respective fsp's are organized in lists of tuples, where the first entry is the fsp and the second is its absolute support.
    
    input: pm4py EventLog object, min_sup (absolute)
    
    output: (fsp_1, fsp_2, fsp_c, sdb)
    '''
    
    sdb = log_to_sdb(log)

    # As a byproduct, frequent subsequences of length 1 are computed during the computation of closed fsp's
    fsp_1, fsp_c = mine_fsp_closed(sdb, min_sup)
    fsp_2 = mine_fsp_2(sdb, min_sup)

    return fsp_1, fsp_2, fsp_c, sdb

def mine_fsp_2(sdb, min_sup):

    db = sdb.db
    num_activities = sdb.num_activities
    # Using sparse id lists and vertical id lists similar to the ones in the closed fsp algorithm
    sils = build_sils(db, num_activities)
    # Compute frequent 1-itemsets, store in a list
    freq_act = []
    for act in range(num_activities):
        # count the number of sequences where the list of id's is not None
        sup = sum(1 for k in range(len(sils[act])) if sils[act][k])
        if sup >= min_sup:
            freq_act.append(act)

    # Vil's for 1-itemsets are not explicitly built, just use first value of corresponding sil if it exists or None otherwise
    # Initialise vil's for sequences of length 2, as a dict of of lists, access vil by sequence as a key
    #vil_2 = [[[None]*len(db) for act2 in freq_act] for act in freq_act]
    vil_2 = {(act, act2):[None]*len(db) for act in freq_act for act2 in freq_act}

    # Build vil's
    for act in freq_act:
        for j in range(len(db)):
            act_idx = get_first_item_or_none(sils[act][j])
            if act_idx is None:
                for act2 in freq_act:
                    vil_2[(act, act2)][j] = None
            else:
                for act2 in freq_act:
                    vil_2[(act, act2)][j] = get_first_larger_element_or_none(sils[act2][j], act_idx)

    fsp_2 = []
    # Compute support of vil's and add corresponding sequence to result
    for act in freq_act:
        for act2 in freq_act:
            sup = vil_compute_support(vil_2[(act, act2)])
            if sup >= min_sup:
                fsp_2.append(((act, act2), sup))

    return fsp_2

def get_first_larger_element_or_none(lst, bound):
    if lst is None:
        return None
    else:
        for item in lst:
            if item > bound:
                return item
    return None

def mine_fsp_from_sample(log, min_sup, training_set_fraction=0.5):
    training_set_size = ceil(len(log)*training_set_fraction)
    training_log = EventLog(log[:training_set_size])

    return mine_fsp(training_log, min_sup)