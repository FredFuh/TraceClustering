from traceClustering.sample_log.sample import read_sample_list, create_sample_logs
from traceClustering.clustering.cluster import cluster_log
from traceClustering.evaluation.quality_measures import compute_cluster_quality_measures

from pm4py.objects.log.exporter.xes import factory as xes_exporter
import csv

def check_sample_list(csv_path, log_path):
    """
    Given the file paths of a csv file and an xes log file, tries to read both and create a dictionary mapping cluster labels from the csv file to case ids.

    Parameters
    -----------
    csv_path
        File path to a CSV file with rows in the format "caseid,clusterlabel"
    log_path
        File path to an XES log file
    Returns
    -------
    success : bool
        Boolean value indicating whether reading the log and csv file was successful
    error_str : str
        String containing an error messsage if the returned success flag is False
    clus_dict : dict
        Dictionary from reading the csv file, having cluster labels as keys and the caseids belonging to it as values
    cluster_labels : list
        List of cluster labels found in the csv file
    log
        EventLog object read from the given log_path if successful
    
    Examples
    -----------
    >>> csv_path = os.path.join(os.path.dirname(__file__), 'sample_test2.csv').replace('\\', '/') # Use example data from test_date folder
    >>> log_path = os.path.join(os.path.dirname(__file__), 'test2.xes').replace('\\', '/')
    >>> success, error_str, clus_dict, cluster_labels, log = check_sample_list(log_path, csv_path)
    >>> if not success: print(error_str) # Also handle the error!
    >>> print('First trace of log: ', log[0])
    >>> print('Caseids belonging to cluster 1 in the sample file: ', clus_dict['1'])
    """
    success = True
    error_str = ""

    try:
        clus_dict, cluster_labels, missing_cases, log = read_sample_list(csv_path, log_path)
    except:
        success = False
        error_str = "Could not read the log or csv file. Please reupload them."
        return success, error_str, None, None, None

    if missing_cases:
        success = False
        error_str = "Sample csv file contained the following unknown case ids: " + ", ".join(missing_cases) + ". You might want to go back and reupload it."

    # check length of sample logs here? If we want to enforce minimum length

    return success, error_str, clus_dict, cluster_labels, log


def traceclustering_main(log, clus_dict, cluster_labels, min_sup, lthresh_1, lthresh_2, lthresh_clo, auto_thresh, output_log_path, output_csv_path):
    """
    Main function to compute the clustering of a log with respect to the sample lists given as a dictionary. Outputs the discovered frequent sequence patterns used for clustering
    and computes estimated cluster quality measures while writing a clustered xes log to the filesystem together with a csv file assigning case ids to clusters.

    Parameters
    -----------
    log
        EventLog object
    clus_dict : dict
        Dictionary of the sample lists having cluster labels as keys and the caseids belonging to it as values
    cluster_labels : list
        List of cluster labels found in the csv file
    min_sup
        Relative minimum support value between 0 and 1 used for sequence mining
    lthresh_1, lthresh_2, lthresh_clo : [float]
        Thresholds for each cluster for scoring the traces and assigning to clusters, fraction of sequence patterns a trace must contain. Ignored if auto_thresh flag is set to True
    auto_thresh : bool
        If set to True, automatically determines optimal threshold values for scoring and clustering traces. Can drastically increase computation time.
    output_log_path
        File path where the clustered log should be written to as an xes file
    output_csv_path
        File path to where the csv file associating caseids with clusters should be written to

    Returns
    -----------
    cluster_fsps : dict(cluster_label:([((str), int)], [((str), int)], [((str), int)]))
        Dictionary containing the fsp's for each cluster. The cluster name serves as the key. A corresponding value for a cluster is a tuple of length 3 where the
        first entry contains the fsp's of length 1, the second of length 2 and the third the closed ones. Each set of fsp's is a list containing tuples with the a sequence as the first element
        and its absolute support in the sample set as the second element. A sequence is a tuple with strings as its elements corresponding to activity names in the original log.
    measures : dict
        Dictionary mapping a cluster label to the tuple of measurements where
            recall -> Estimated recall
            precision -> Estimated precision
            f1_score -> Estimated F1 score

    Examples
    -----------
    >>> cluster_fsps, measures = traceclustering_main(log, clus_dict, cluster_labels, 0.99, [0.7, 0.7], [0.5, 0.5], [0.6, 0.6], False, output_log_path, output_csv_path)
    >>> # Not using automatic thresholds, but 0.7 for fsps of length 1, 0.5 for length 2, 0.6 for closed (for both clusters)
    >>> print('Quality measures for cluster 1: ', measures['1'])
    >>> print('cluster 1 fsp_1: ', cluster_fsps['1'][0][:3])
    >>> print('cluster 1 fsp_2: ', cluster_fsps['1'][1][:3])
    >>> print('cluster 1 fsp_c: ', cluster_fsps['1'][2][:3])
    """
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