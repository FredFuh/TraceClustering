from traceClustering.sample_log.sample import read_sample_list, create_sample_logs
from traceClustering.clustering.cluster import cluster_log
from traceClustering.evaluation.quality_measures import compute_cluster_quality_measures

from pm4py.objects.log.exporter.xes import factory as xes_exporter
import csv

def check_sample_list(csv_path, log_path):
    success = True
    error_str = ""

    try:
        clus_dict, cluster_labels, missing_cases, log = read_sample_list(csv_path, log_path)
    except:
        success = False
        error_str = "Could not read log or csv file"
        return success, error_str, None, None, None

    if missing_cases:
        success = False
        error_str = "Sample csv file contained unknown case ids"

    # check length of sample logs here? If we want to enforce minimum length

    return success, error_str, clus_dict, cluster_labels, log


def traceclustering_main(log, clus_dict, cluster_labels, min_sup, lthresh_1, lthresh_2, lthresh_clo, auto_thresh, output_log_path, output_csv_path):
    sample_logs = create_sample_logs(clus_dict, cluster_labels, log)
    clustered_log, clustercsvlist, cluster_fsps = cluster_log(log, sample_logs, cluster_labels, min_sup, lthresh_1, lthresh_2, lthresh_clo, auto_thresh)
    measures = compute_cluster_quality_measures(clustered_log, sample_logs, cluster_labels)

    # warning if bad quality measures for some clusters, or check that in front end?

    with open(output_csv_path, 'w+', newline='') as csv_output:
        writer = csv.writer(csv_output)
        for row in clustercsvlist:
            writer.writerow(row)
    
    xes_exporter.export_log(clustered_log, output_log_path)

    return cluster_fsps, measures