import csv


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
