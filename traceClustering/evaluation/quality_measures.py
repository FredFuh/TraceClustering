# Compute estimated cluster quality measures (recall, precision, f1-score), formula found in the paper by X. Lu
def compute_cluster_quality_measures(clustered_log, sample_logs):
    # Assuming the traces of the sample logs have an trace attribute 'original_log_idx' which is the index of said trace in the clustered_log
    # Assuming clustered_log contains a trace attribute 'cluster'
    num_clusters = len(sample_logs)+1   # including 'dummy' cluster 0, which are the traces which were not assigned to a cluster
    measures = dict()
    cluster_sizes = [0] * num_clusters

    for trace in clustered_log:
        cluster_sizes[trace['cluster']] += 1

    for cluster in range(1,num_clusters):
        precision, recall = compute_precision_and_recall(clustered_log, sample_logs[cluster-1], cluster_sizes[cluster], cluster)
        f1_score = compute_f1_score(precision, recall)
        measures[cluster] = (recall, precision, f1_score)

    return measures

    
def compute_precision_and_recall(clustered_log, sample_log, cluster_size, cluster_label):
    len_sample = len(sample_log)
    # Compute the size of the intersection of the sample log and the cluster
    intersec_size = 0
    # Assume traces of sample log have trace attribute 'original_log_idx', providing the index of each trace in the full log
    for trace in sample_log:
        trc_idx = trace['original_log_idx']
        if clustered_log[trc_idx]['cluster'] == cluster_label:
            intersec_size += 1

    precision = intersec_size / cluster_size
    recall = intersec_size / len_sample

    return precision, recall

def compute_f1_score(precision, recall):
    return 2 * (precision * recall) / (precision + recall)