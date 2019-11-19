from pm4py.objects.log.importer.xes import factory as xes_importer

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
