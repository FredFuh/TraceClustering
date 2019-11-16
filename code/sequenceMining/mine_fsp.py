from pm4py.objects.log.importer.xes import factory as xes_importer
from sequenceDB import *
from mine_fsp_closed import mine_fsp_closed

def mine_fsp(log_path, min_sup):
    ''' 
    Mines the frequent sequent patterns (fsp's) of length 1,2 and the closed fsp's for the given event log and minimum support.
    The respective fsp's are organized in lists of tuples, where the first entry is the fsp and the second is its absolute support.
    
    input: XES log file path, min_sup (absolute)
    
    output: (fsp_1, fsp_2, fsp_c)
    '''
    
    sdb = log_to_sdb(log_path)

    # As a byproduct, frequent subsequences of length 1 are computed during the computation of closed fsp's
    fsp_1, fsp_c = mine_fsp_closed(sdb, min_sup)
    fsp_2 = mine_fsp_2(sdb, min_sup)

    return fsp_1, fsp_2, fsp_c

# placeholder
def mine_fsp_2(sdb, min_sup):
    return dict()