

def check_sample_list(filepath):
    """ checks if the given list fulfills criteria
        - is big enoug (at least 20 ids)
        - only one cluster and counterpart
        - ids from cluster as well as from coutnerpart
        input: csv file: id, cluster
             where cluster =1 if in cluster, else 0

        output: dict:
            cluster: contains list of ids for this cluster"""
