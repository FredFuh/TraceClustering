from collections import defaultdict

def compute_cluster_quality_measures(clustered_log, sample_logs, cluster_labels):
    """
    Compute estimated cluster quality measures (recall, precision, f1-score) given a clustered log where traces contain a cluster attribute and the sample logs; formulas as in the paper by X. Lu.

    Parameters
    -----------
    clustered_log
        EventLog object
    sample_logs (list)
        List of EventLog objects
    cluster_labels ([str])
        List of cluster labels.

    Returns
    -----------
    measures (dict)
        Dictionary mapping a cluster label to the tuple of measurements where
            recall -> Estimated recall
            precision -> Estimated precision
            f1_score -> Estimated F1 score
    """
    # Assuming the traces of the sample logs have an trace attribute 'original_log_idx' which is the index of said trace in the clustered_log
    # Assuming clustered_log contains a trace attribute 'cluster'
    #num_clusters = len(sample_logs)+1   # including 'dummy' cluster 0, which are the traces which were not assigned to a cluster
    measures = dict()
    cluster_sizes = defaultdict(lambda: 0)

    for trace in clustered_log:
        cluster_sizes[trace.attributes['cluster']] += 1

    for i, cluster_label in enumerate(cluster_labels):
        if cluster_sizes[cluster_label] == 0:
            recall, precision, f1_score = 0, 0, 0
        else:
            precision, recall = compute_precision_and_recall(clustered_log, sample_logs[i], cluster_sizes[cluster_label], cluster_label)
            f1_score = compute_f1_score(precision, recall)
        measures[cluster_label] = (recall, precision, f1_score)

    return measures

    
def compute_precision_and_recall(clustered_log, sample_log, cluster_size, cluster_label):
    """
    Compute estimated precision and recall for a specific cluster given a clustered log where traces contain a cluster attribute and the sample log; formulas as in the paper by X. Lu.

    Parameters
    -----------
    clustered_log
        EventLog object
    sample_log
        EventLog object
    cluster_size (int)
        Number of traces in the cluster.
    cluster_label
        Label of the cluster

    Returns
    -----------
    precision
        Estimated precision
    recall
        Estimated recall
    """
    len_sample = len(sample_log)
    # Compute the size of the intersection of the sample log and the cluster
    intersec_size = 0
    # Assume traces of sample log have trace attribute 'original_log_idx', providing the index of each trace in the full log
    #for trace in sample_log:
    #    trc_idx = trace.attributes['original_log_idx']
    #    if clustered_log[trc_idx].attributes['cluster'] == cluster_label:
    #        intersec_size += 1

    sample_ids = [trace.attributes['concept:name'] for trace in sample_log]
    intersec_size = sum(1 for j in range(len(clustered_log)) if (clustered_log[j].attributes['concept:name'] in sample_ids) and (clustered_log[j].attributes['cluster'] == cluster_label))

    precision = intersec_size / cluster_size
    recall = intersec_size / len_sample

    return precision, recall

def compute_f1_score(precision, recall):
    """
    Compute the F1 score given a precision and recall value.

    Parameters
    -----------
    precision
        Precision value.
    recall
        Recall value.

    Returns
    -----------
    score
        F! score.
    
    """
    score = 0
    if precision + recall != 0:
        score = 2 * (precision * recall) / (precision + recall)
    return score