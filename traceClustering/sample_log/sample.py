# example import
# from traceClustering.sequence_mining.mine_fsp_closed import mine_fsp_closed
import csv
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.log.exporter.xes import factory as xes_exporter
from pm4py.objects.log.log import EventLog
# Provide functions here for input event log and csv file path to return a pm4py EventLog object which only contains traces from the sample list
# Potentially already implement to generate multiple sample sets if csv file contains information for multiple clusters

def build_sequences(filepath):
    """ 
    Converts the input log into a dictionary with case ids as key and list of events as its values. 

    Input: XES log filepath
    
    Output: Dictionary
    """
    sequence = {}
    log = xes_importer.import_log(filepath)
    
    for trace in log:
        sequence[trace.attributes['concept:name']] = [event['concept:name'] for event in trace]
    
    return sequence

'''
def check_sample_list(filepath):
    """ checks if the given list fulfills criteria
        - is big enoug (at least 20 ids)
        - only one cluster and counterpart
        - ids from cluster as well as from coutnerpart
        input: csv file: id, cluster
             where cluster =1 if in cluster, else 0

        output:
        boolean: indicate if check was successful

        dict: if successful
            "cluster": contains list of ids for this cluster
            "noncluster": contains list of the remaining ids
        """
    res = dict()
    res['cluster'] = list()
    res['noncluster'] = list()
    boolvalue = True
    with open(filepath) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        count = 0
        for row in csv_reader:
            if int(row[1]) == 1:
                res['cluster'].append(row[0])
            elif int(row[1]) == 0:
                res['noncluster'].append(row[0])
            else:
                boolvalue = False
            count += 1
        if count < 20 or len(res['cluster']) == 0:
            boolvalue = False
    if boolvalue:
        return boolvalue, res
    else:
        return boolvalue, None
'''

def check_sample_list(filepath, seq):
    """ 
    Checks if all the given cases exist in the log and creates a dictionary object for each cluster
        
    Input: CSV file path, Sequences seq
           CSV file - Format as below
                file[][0] = case id 
                file[][1] = cluster
           Sequences - Dictionary output of build_sequences()
               
    Output: Result, Missing Cases
            Result - Dictionary with different clusters as key, and its values are list of cases 
            Missing cases - Case ids that do not exist in the log
    """
    result = dict()
    complete_caseids = ""
    missing_cases = []
    
    for key,value in seq.items():
        complete_caseids = complete_caseids + " " + str(key)
        
    with open(filepath) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if row[0] in complete_caseids:
                if result.get(row[1]):
                    result[row[1]].append(row[0])
                else:
                    result[row[1]] = [row[0]]
            else:
                missing_cases.append(row[0])

    return result, missing_cases #use missing_cases in the calling code instead of boolvalue here.

'''
def create_sample_log(logpath, samplelist, goalpath):
    """ Stores the log sampled out of 'logpath' with the 'samplelist' at 'goalpath'
        uses 'check_sample_list' to validate samplelist"""
    success, sample = check_sample_list(samplelist)
    if success:
        log = xes_importer.import_log(logpath)
        print(log)
        print(type(log))
        args = {'attributes': log.attributes, 'extensions': log.extensions, 'omni_present': log.omni_present, 'classifiers': log.classifiers}

        samplelog = EventLog(**args)
        print(sample['cluster'])
        for trace in log:
            if trace.attributes['concept:name'] in sample['cluster']:
                samplelog.append(trace)
        xes_exporter.export_log(samplelog, goalpath)
'''
def create_sample_logs(clus_dict, filepath):
    """
    Build separate logs with traces corresponding to each cluster
    
    Input: Dictionary output of check_sample_list(), XES log filepath
    
    Output: No return value
    """
    log = xes_importer.import_log(filepath)

    for key,value in clus_dict.items():
        args = {'attributes': log.attributes, 'extensions': log.extensions, 'omni_present': log.omni_present, 'classifiers': log.classifiers}
        samplelog = TraceLog(**args)
        goalpath = filepath[:-4] + "_" + key + ".xes"
        for trace in log:
            if trace.attributes['concept:name'] in value:
                samplelog.append(trace)
        
        xes_exporter.export_log(samplelog, goalpath)
