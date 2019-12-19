from traceClustering.main import check_sample_list, traceclustering_main
from pathlib import Path
import os
import csv
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.log.exporter.xes import factory as xes_exporter
from traceClustering.sample_log.sample import create_sample_logs

csv_path = os.path.join(os.path.dirname(__file__), 'sample_test2.csv').replace('\\', '/')
log_path = os.path.join(os.path.dirname(__file__), 'test2.xes').replace('\\', '/')

success, error_str, clus_dict, cluster_labels, log = check_sample_list(log_path, csv_path)

print(success)
if not success: print(error_str)
print(clus_dict)
print(cluster_labels)
print(log[0])

output_csv_path = os.path.join(os.path.dirname(__file__), '..', 'out/csvclustering.csv').replace('\\', '/')
output_log_path = os.path.join(os.path.dirname(__file__), '..', 'out/clustered.xes').replace('\\', '/')

cluster_fsps, measures = traceclustering_main(log, clus_dict, cluster_labels, 0.99, [], [], [], True, output_log_path, output_csv_path)

print(measures)
print('cluster 1 fsp_1: ', cluster_fsps['1'][0][:3])
print('cluster 1 fsp_2: ', cluster_fsps['1'][1][:3])
print('cluster 1 fsp_c: ', cluster_fsps['1'][2][:3])