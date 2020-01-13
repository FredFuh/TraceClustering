from traceClustering.sequence_mining.sequenceDB import log_to_sdb
from traceClustering.sequence_mining.mine_fsp_closed import mine_fsp_closed, get_first_item_or_none, build_sils, vil_compute_support
from pm4py.objects.log.log import EventLog
from math import ceil

def mine_fsp(log, min_sup):
    """
    Mines the frequent sequent patterns (fsp's) of length 1,2 and the closed fsp's for the given event log and minimum support.
    The respective fsp's are organized in lists of tuples, where the first entry is the fsp and the second is its absolute support.

    Parameters
    -----------
    log
        EventLog object
    min_sup : int
        Absolute minimum support value

    Returns
    -----------
    fsp_1 : [((int), int)]
        Fsp's of length 1
    fsp_2 : [((int), int)]
        Fsp's of length 2
    fsp_c : [((int), int)]
        Closed fsp's
    sdb
        SequenceDB object created during the mining
    """
    
    sdb = log_to_sdb(log)

    # As a byproduct, frequent subsequences of length 1 are computed during the computation of closed fsp's
    fsp_1, fsp_c = mine_fsp_closed(sdb, min_sup)
    fsp_2 = mine_fsp_2(sdb, min_sup)

    return fsp_1, fsp_2, fsp_c, sdb

def mine_fsp_2(sdb, min_sup):
    """
    Mines the frequent sequence patterns of length 2 given a log in sequence database representation and the absolute minimum support.

    Parameters
    -----------
    sdb
        SequenceDB object
    min_sup : int
        Absolute minimum support value

    Returns
    -----------
    fsp_2 : [((int), int)]
        Fsp's of length 2

    """
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
    """
    Returns the first element of a list that is larger then the given bound, or None if such an element does not exist.

    Parameters
    -----------
    lst : [int]
        List
    bound : int
        Minimum bound value

    Returns
    -----------
    item : int
        The first larger element to be found, or None
    
    """
    if lst is None:
        return None
    else:
        for item in lst:
            if item > bound:
                return item
    return None

def mine_fsp_from_sample(log, min_sup, training_set_fraction=0.5):
    """
    Mines the frequent sequent patterns (fsp's) of length 1,2 and the closed fsp's for the given sample log and minimum support.
    The fsp's are computed on the first traces of a fraction of the given log, which can be set as a parameter.
    The respective fsp's are organized in lists of tuples, where the first entry is the fsp and the second is its absolute support.

    Parameters
    -----------
    log
        EventLog object
    min_sup : int
        Relative minimum support value between 0 and 1 used for sequence mining
    training_set_fraction (float
        Fraction of the number of traces to be used for sequence mining

    Returns
    -----------
    fsp_1 : [((int), int)]
        Fsp's of length 1
    fsp_2 : [((int), int)]
        Fsp's of length 2
    fsp_c : [((int), int)]
        Closed fsp's
    sdb
        SequenceDB object created during the mining

    Examples
    -----------
    >>> mine_fsp_from_sample(log, 0.7, training_set_fraction=0.5)
    >>> print(sdb.db[:5]) # prints first 5 sequences in their integer representation
    >>> print('cluster 1 fsp_1: ', cluster_fsps[cluster_label][0][:3]) # first 3 fsps of length 1 for cluster with name 'cluster_label'
    >>> print('cluster 1 fsp_2: ', cluster_fsps[cluster_label][1][:3]) # first 3 fsps of length 2 for cluster with name 'cluster_label'
    >>> print('cluster 1 fsp_c: ', cluster_fsps[cluster_label][2][:3]) # first 3 fsps of length 2 for cluster with name 'cluster_label'
    """
    training_set_size = ceil(len(log)*training_set_fraction)
    min_sup_abs = ceil(training_set_size * min_sup)
    training_log = EventLog(log[:training_set_size])

    return mine_fsp(training_log, min_sup_abs)