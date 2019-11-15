import csv
from pm4py.objects.log.importer.xes import factory as xes_importer


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


def build_sequences(logfile):
    """
    Converts the input log into list of lists with trace id followed by list of activites.
    list[0] - Trace id
    list[1] - List of events
    
    input: XES log file path
    
    output: List
    """
    sequence = []
    log = xes_importer.import_log(logfile)
    
    for trace in log:
        sequence.append([trace.attributes['concept:name'],[event['concept:name'] for event in trace]])
    return sequence


def extract_sequences(sample_list, sequences):
    """ Given the sample list computed by check_sample_list and the sequences list computed by build_sequences,
    extracts the traces corresponding to the ids in the sample list from the sequence list
    input:
        - sample list:  ['cluster'] list of ids for cluster
                        ['nonlcuster'] list of ids not in cluster
        - sequences: list of lists:
            list[0]: list of ids
            list[1]: list of list of events corresponding to id

    output:
        -dict:  ['cluster']: list of list of events
                ['noncluster']: list of list of events """

    traces = []
    traces['cluster'] = list()
    for e in sample_list['cluster']:
        try:
            index = sequences[0].index(e)
            traces['cluster'].append(sequences[1][index])
        except ValueError:
            pass
    traces['noncluster'] = list()
    for e in sample_list['noncluster']:
        try:
            index = sequences[0].index(e)
            traces['noncluster'].append(sequences[1][index])
        except ValueError:
            pass
    return traces
