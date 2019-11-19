# example import
# from traceClustering.sequence_mining.mine_fsp_closed import mine_fsp_closed
import csv
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.log.exporter.xes import factory as xes_exporter
from pm4py.objects.log.log import EventLog
# Provide functions here for input event log and csv file path to return a pm4py EventLog object which only contains traces from the sample list
# Potentially already implement to generate multiple sample sets if csv file contains information for multiple clusters

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

