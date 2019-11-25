from traceClustering.sequence_mining.mine_fsp import get_first_larger_element_or_none
from traceClustering.sequence_mining.sequenceDB import SequenceDB
from traceClustering.clustering.cluster import get_sequence_scores, longest_common_prefix_length, cluster_log
from traceClustering.evaluation.quality_measures import compute_cluster_quality_measures

from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.log.log import EventLog

from copy import deepcopy

db = [
    [0,1,6,5,2],
    [0,3,2,5],
    [0,4,5,6]
]

num_activities = 7
fsp_1 = [((0,),3), ((2,),2)]
fsp_2 = [((0,2),1)]
fsp_c = [((0,), 3),((0,2,5), 3)] # not really closed frequent item sets, just for testing purposes
print(longest_common_prefix_length((0,),(0,2,5)))

s1, s2, s3 = get_sequence_scores(db, num_activities, fsp_1, fsp_2, fsp_c)
print(s1)
print(s2)
print(s3)

########

log = xes_importer.import_log('C:\\Users\\Daniel\\Uni\\TraceClustering\\traceClustering\\test_data\\test2.xes') # for some reason I cannot import with a relative path
print(len(log))
sample_logs = [EventLog(deepcopy(log[:10])), EventLog(deepcopy(log[10:20]))]
for i in range(0,10):
    sample_logs[0][i].attributes['original_log_idx'] = i
for i in range(10,20):
    sample_logs[1][i-10].attributes['original_log_idx'] = i
min_sup = 0.5

clustered_log, _ = cluster_log(log, sample_logs, min_sup, [0.5, 0.5], [0.5, 0.5], [0.5, 0.5], auto_thresh=True)
print('finished computation')
print(clustered_log)
print(len(clustered_log))
print('quality measures: ', compute_cluster_quality_measures(clustered_log, sample_logs))