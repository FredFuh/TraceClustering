# Provide functionality here, for a given pm4py EventLog object and set of frequent sequences in integer representation to compute the scores and finally cluster(s)
# Potentially handle multiple sample sets given by sample_log module
from copy import deepcopy
from math import ceil
from pm4py.objects.log.log import EventLog
from traceClustering.sequence_mining.sequenceDB import apply_sdb_mapping_to_log
from traceClustering.sequence_mining.mine_fsp import mine_fsp_from_sample
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
        thresh_1, thresh_2, thresh_clo (int): Thresholds for scoring the traces and assigning to clusters
    
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

    for cluster in range(1,num_clusters+1):
        clustering = compute_partial_clustering(unclustered_log, sample_logs[cluster-1], min_sup_abs, lthresh_1[cluster-1], lthresh_2[cluster-1], lthresh_clo[cluster-1])
        apply_clustering_to_log(log, clustering, cluster_label=cluster)
        sublog, unclustered_log = split_log_on_cluster_attribute(unclustered_log)
        clustered_sublogs.append(sublog)

    concat_logs(clustered_sublogs)
    return clustered_sublogs[0]

# Returns an array of 0-1 values, 1 means the trace at that index of the array is in the cluster
def compute_partial_clustering(log, sample_log, min_sup, thresh_1, thresh_2, thresh_clo):
    fsp_1, fsp_2, fsp_c, sdb = mine_fsp_from_sample(log, min_sup)
    db = apply_sdb_mapping_to_log(log, sdb)
    scores_1, scores_2, scores_clo = get_sequence_scores(db, sdb.num_activities, fsp_1, fsp_2, fsp_c)
    clustering = get_clustering_from_scores(scores_1, scores_2, scores_clo, thresh_1, thresh_2, thresh_clo)

    return clustering

def apply_clustering_to_log(log, clustering, cluster_label):
    for i in range(len(log)):
        if clustering[i]:
            log[i].attributes['cluster'] = cluster_label

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
    # vil's for sequences of length 1 not explicitly built, just get first item of corresponding sil

    return [], [], []

def get_clustering_from_scores(scores_1, scores_2, scores_clo, thresh_1, thresh_2, thresh_clo):
    return [int(s1>=thresh_1 and s2>=thresh_2 and s3>=thresh_clo) for s1, s2, s3 in zip(scores_1,scores_2,scores_clo)]