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
    Checks if all the given cases exist in the log and creates a dictionary object for each cluster
        
    Input: CSV file path, Sequences seq
           CSV file - Format as below
                file[][0] = case id 
                file[][1] = cluster
           Sequences - Dictionary output of build_sequences()
               
    Output: Result - Dictionary with different clusters as key, and its values are list of caseids
            Missing cases - Case ids that do not exist in the log
            Log - The EventLog object from the log stored in log_path
    """

    # TODO: error handling?
    log = xes_importer.import_log(log_path)

    result = defaultdict(list)
    missing_cases = []
    case_ids = [trace.attributes['concept:name'] for trace in log]
        
    with open(csv_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        # TODO: error handling?
        for row in csv_reader:
            if row[0] in case_ids:
                result[row[1]].append(row[0])
            else:
                missing_cases.append(row[0])

    cluster_labels = list(result.keys())

    return result, cluster_labels, missing_cases, log


def write_sample_logs_to_fs(clus_dict, filepath):
    """
    Build separate logs with traces corresponding to each cluster
    
    Input: Dictionary output of check_sample_list(), XES log filepath
    
    Output: No return value
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