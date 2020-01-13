# example import
# from traceClustering.sequence_mining.mine_fsp_closed import mine_fsp_closed
import csv
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.log.exporter.xes import factory as xes_exporter
from pm4py.objects.log.log import EventLog
from copy import deepcopy
from collections import defaultdict

def read_sample_list(log_path, csv_path):
    """
    Reads the log and csv file containing clustering information, then checks if all the given cases exist in the log and creates a dictionary mapping cluster labels to a list of case ids.
    CSV file format:
                file[][0] = case id 
                file[][1] = cluster

    Parameters
    -----------
    log_path
        Path to the XES log file
    csv_path
        Path to the csv file containing clustering information for the sample sets

    Returns
    -----------
    clus_dict : dict
        Dictionary using the cluster labels as keys and the corresponding list of case ids as values.
    cluster_labels : list
        The labels of the clusters used in the csv file
    missing_cases : list
        Case ids which are contained in the csv file but not in the log
    log
        EventLog object
    """

    log = xes_importer.import_log(log_path)

    clus_dict = defaultdict(list)
    missing_cases = []
    case_ids = [trace.attributes['concept:name'] for trace in log]
        
    with open(csv_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if len(row) != 2:
                raise Exception()
            elif row[0] in case_ids:
                clus_dict[row[1]].append(row[0])
            else:
                missing_cases.append(row[0])

    cluster_labels = list(clus_dict.keys())

    return clus_dict, cluster_labels, missing_cases, log


def write_sample_logs_to_fs(clus_dict, filepath):
    """
    Build separate logs with traces corresponding to each cluster and write them to the filesystem.

    Parameters
    -----------
    clus_dict : dict
        Dictionary using the cluster labels as keys and the corresponding list of case ids as values.
    filepath
        Path to the XES log file
    """
    log = xes_importer.import_log(filepath)

    for key,value in clus_dict.items():
        args = {'attributes': log.attributes, 'extensions': log.extensions, 'omni_present': log.omni_present, 'classifiers': log.classifiers}
        samplelog = EventLog(**args)
        goalpath = filepath[:-4] + "_" + key + ".xes"
        for trace in log:
            if trace.attributes['concept:name'] in value:
                samplelog.append(deepcopy(trace))
        xes_exporter.export_log(samplelog, goalpath)

def create_sample_logs(clus_dict, cluster_labels, log):
    """
    Build separate logs with traces corresponding to each cluster
    
    Input: Dictionary output of check_sample_list(), EventLog object
    
    Output: List of sample logs as EventLog objects
    """
    """
    Computes the sample logs from the full log given a dictionary mapping cluster labels to case ids.

    Parameters
    -----------
    clus_dict : dict
        Dictionary using the cluster labels as keys and the corresponding list of case ids as values.
    cluster_labels : list
        The labels of the clusters to be discovered
    log
        EventLog object

    Returns
    -----------
    sample_logs : list
        List of EventLog objects
    """
    sample_logs = []

    for cluster_label in cluster_labels:
        caseids = clus_dict[cluster_label]
        args = {'attributes': log.attributes, 'extensions': log.extensions, 'omni_present': log.omni_present, 'classifiers': log.classifiers}
        samplelog = EventLog(**args)
        for idx in range(len(log)):
            if log[idx].attributes['concept:name'] in caseids:
                samplelog.append(deepcopy(log[idx]))
                #samplelog[-1].attributes['original_log_idx'] = idx
        sample_logs.append(samplelog)

    return sample_logs