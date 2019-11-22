# Provide functionality here, for a given pm4py EventLog object and set of frequent sequences in integer representation to compute the scores and finally cluster(s)
# Potentially handle multiple sample sets given by sample_log module
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.log.exporter.xes import factory as xes_exporter
import csv


def check_thresholds(scores, thresholds):
    if scores[0] >= thresholds[0] and scores[1] >= thresholds[1] and scores[2] >= thresholds[2]:
        return True
    return False


def group_traces(filepath, scores, thresholds, cluster):
    """ mark traces in the log if corresponding score is above threshold
    Input:
        -filepath: path to original log
        -scores: list of lists of scores as result of matching the patterns on the sequences
        -thresholds: thresholds for the different sequences
        -cluster: name of the cluster currently grouped (maybe extend to use multiple clusters at once)

    Output:
        -log with traces belonging to cluster marked
        """
    log = xes_importer.import_log(filepath)
    goalpath = filepath[:-4] + "_" + "result" + str(cluster) + ".xes"
    csvpath = filepath[:-4] + "_" + "result" + str(cluster) + ".csv"
    mapping = []
    for trace in log:
        if check_thresholds(scores[log.index(trace)], thresholds):
            attr = trace.attributes
            attr['cluster'] = cluster
            trace._set_attributes(attr)
            mapping.append([trace.attributes['concept:name'], cluster])
    xes_exporter.export_log(log, goalpath)
    with open(csvpath, 'wb') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in mapping:
            filewriter.writerow(row)


