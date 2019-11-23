# Provide functionality here, for a given pm4py EventLog object and set of frequent sequences in integer representation to compute the scores and finally cluster(s)
# Potentially handle multiple sample sets given by sample_log module

from copy import deepcopy
from math import ceil
from pm4py.objects.log.log import EventLog
from traceClustering.sequence_mining.sequenceDB import apply_sdb_mapping_to_log
from traceClustering.sequence_mining.mine_fsp import mine_fsp_from_sample, get_first_larger_element_or_none
from traceClustering.sequence_mining.mine_fsp_closed import build_sils, get_first_item_or_none

def cluster_log(log, sample_logs, min_sup, lthresh_1, lthresh_2, lthresh_clo):
    ''' 
    Receives and event log and a list of (disjoint) sample logs which represent sample traces from clusters to be discovered and returns the input log containing the computed clustering information.
    The assigned cluster for each trace is stored as in the trace attribute 'cluster'. If the trace attribute existed before in the log, its values will be overwritten. The clusters names are
    1,...,len(sample_logs). Traces which could not be assigned to a cluster have the cluster value 0. The clusters are discovered in the order of the sample logs. For frequent sequence pattern discovery,
    min_sup describes the relative minimum support. The parameter lists lthresh_1, lthresh_2, lthresh_clo contain the thresholds to score the traces for each cluster.
    
    Args:
        log (EventLog): The EventLog object
        sample_logs ([EventLog]): The list of EventLog objects representing the sample lists
        min_sup (int): The relative minimum support for fsp discovery
        thresh_1, thresh_2, thresh_clo (float): Thresholds for scoring the traces and assigning to clusters, fraction of sequence patterns a trace must contain
    
    Returns:
        EventLog: The event log containing cluster information
    '''
    # Do not destroy input log
    unclustered_log = deepcopy(log)
    min_sup_abs = ceil(len(unclustered_log) * min_sup)
    # Initialise cluster attribute
    for trace in unclustered_log:
        trace.attributes['cluster'] = 0

    clustered_sublogs = []
    num_clusters = len(sample_logs)
    clustercsvlist = []


    for cluster in range(1,num_clusters+1):
        csvcluster = []
        clustering = compute_partial_clustering(unclustered_log, sample_logs[cluster-1], min_sup_abs, lthresh_1[cluster-1], lthresh_2[cluster-1], lthresh_clo[cluster-1])
        apply_clustering_to_log(log, clustering, csvcluster, cluster_label=cluster)
        sublog, unclustered_log = split_log_on_cluster_attribute(unclustered_log)
        clustered_sublogs.append(sublog)
        clustercsvlist[cluster] = csvcluster

    concat_logs(clustered_sublogs)
    return clustered_sublogs[0], csvcluster

# Returns an array of 0-1 values, 1 means the trace at that index of the array is in the cluster
def compute_partial_clustering(log, sample_log, min_sup, thresh_1, thresh_2, thresh_clo):
    fsp_1, fsp_2, fsp_c, sdb = mine_fsp_from_sample(log, min_sup)
    db = apply_sdb_mapping_to_log(log, sdb)
    # Convert relative thresholds to absolute values
    thresh_1 = ceil(thresh_1 * len(fsp_1))
    thresh_2 = ceil(thresh_1 * len(fsp_2))
    thresh_clo = ceil(thresh_1 * len(fsp_c))
    scores_1, scores_2, scores_clo = get_sequence_scores(db, sdb.num_activities, fsp_1, fsp_2, fsp_c)
    clustering = get_clustering_from_scores(scores_1, scores_2, scores_clo, thresh_1, thresh_2, thresh_clo)

    return clustering

def apply_clustering_to_log(log, clustering, csvcluster, cluster_label):

    for i in range(len(log)):
        if clustering[i]:
            log[i].attributes['cluster'] = cluster_label
            csvcluster.append([log[i].attributes['concept:name'], cluster_label])

def split_log_on_cluster_attribute(log):
    # Insert traces where cluster attribute is nonzero into log1, rest into log2
    log1 = EventLog()
    log2 = EventLog()
    for trace in log:
        if trace.attributes['cluster']:
            log1.append(trace)
        else:
            log2.append(trace)
    return log1, log2

def concat_logs(logs):
    res = logs[0]
    for log in logs[1:]:
        for trace in log:
            res.append(trace)
    return res

def get_sequence_scores(db, num_activities, fsp_1, fsp_2, fsp_c):
    # input db is of type [[int]]
    # Discard frequency information of the fsp's
    fsp_1 = [fsp[0] for fsp in fsp_1]
    fsp_2 = [fsp[0] for fsp in fsp_2]
    fsp_c = [fsp[0] for fsp in fsp_c]

    sils = build_sils(db, num_activities)
    # vils are stored in a dictionary, where the key is a fsp (tuple of ints) and the value is the corresponding vil
    vils = dict()

    for fsp in fsp_1:
        act = fsp[0]
        vil = [get_first_item_or_none(idlist) for idlist in sils[act]]
        vils[fsp] = vil

    for fsp in fsp_2:
        last_act = fsp[1]
        vil_first_act = vils[fsp[:1]]
        vil = [None] * len(db)
        for j in range(len(db)):
            val = vil_first_act[j]
            if val is not None:
                vil[j] = get_first_larger_element_or_none(sils[last_act][j], val)
            #else: vil[j] = None
        vils[fsp] = vil

    prev_fsp = ()
    # For computing the vil's for the closed fsp's, we abuse the fact that our fsp list is in lexicographical order, since that is how the discovery algorithm generated the fsp's
    # If two consecutive elements in the fsp list share a prefix, then the vil up to this prefix is used for the computation of the vil of the second fsp
    # Also use the fact that we computed vil's for all fsp's of length 1 and 2
    for fsp in fsp_c:
        if len(fsp) > 2:
            lcp_len = longest_common_prefix_length(prev_fsp, fsp)
            # In some cases, due to pruning, the length of the longest common prefix can be smaller than 2. In that case we still already have that vil computed because of fsp_2
            lcp_len = max(lcp_len, 2)
            compute_prefix_vils(fsp, lcp_len, sils, vils)
        # else: vil for fsp is already in the dict
        prev_fsp = fsp

    # Compute scores for fsp_1
    vil_list_1 = [vils[fsp] for fsp in fsp_1]
    scores_1 = [sum(1 for vil in vil_list_1 if vil[j] is not None) for j in range(len(db))]

    # Compute scores for fsp_1
    vil_list_2 = [vils[fsp] for fsp in fsp_2]
    scores_2 = [sum(1 for vil in vil_list_2 if vil[j] is not None) for j in range(len(db))]

    # Compute scores for fsp_1
    vil_list_c = [vils[fsp] for fsp in fsp_c]
    scores_c = [sum(1 for vil in vil_list_c if vil[j] is not None) for j in range(len(db))]

    return scores_1, scores_2, scores_c

# Computes longest common prefix of two tuples
def longest_common_prefix_length(tup1, tup2):
    min_len = min(len(tup1), len(tup2))
    count = 0
    for i in range(min_len):
        if tup1[i] == tup2[i]:
            count = count + 1
        else:
            break
    return count

# Compute vils of all prefixes of seq (including seq) with length at least n+1, assuming the vil for the prefix of length n has been computed
# Vil's read from and stored in vils_dict
def compute_prefix_vils(seq, n, sils, vils_dict):
    for i in range(n+1,len(seq)+1):
        vil = [None] * len(sils[0])
        prev_prefix = seq[:i-1]
        curr_prefix = seq[:i]
        last_act = curr_prefix[-1]
        for j in range(len(sils[0])):
            val = vils_dict[prev_prefix][j]
            if val is not None:
                vil[j] = get_first_larger_element_or_none(sils[last_act][j], val)
            #else: vil[j] = None
        vils_dict[curr_prefix] = vil


def get_clustering_from_scores(scores_1, scores_2, scores_clo, thresh_1, thresh_2, thresh_clo):
    return [int(s1>=thresh_1 and s2>=thresh_2 and s3>=thresh_clo) for s1, s2, s3 in zip(scores_1,scores_2,scores_clo)]
