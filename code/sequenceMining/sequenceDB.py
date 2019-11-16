# Represent sequences of traces as a list of integers, where the integers are indices 0,...,n of activities
# Introduce its own class mainly to bookkeep information about mapping from activities to indices
# the sequence database retains order of the traces from the log, thus no need to remember case id's

from pm4py.objects.log.importer.xes import factory as xes_importer

class SequenceDB:
    def __init__(self):
        self.db = []
        self.num_activities = 0
        self.activity_to_idx = dict()
        self.idx_to_activity = dict()

    # Assuming non empty tracelist
    def initialise_db(self, tracelist):
        # Determine the set of activities
        activity_set = set(tracelist[0])
        for trace in tracelist:
            activity_set.update(trace)
        
        # Assign activities an index, and update the dicts
        indexing = list(enumerate(activity_set))
        self.num_activities = len(activity_set)
        self.activity_to_idx = {act: idx for idx, act in indexing}
        self.idx_to_activity = {idx: act for idx, act in indexing}

        # Apply mapping to the tracelist
        self.db = [[self.activity_to_idx[act] for act in trace] for trace in tracelist]


def log_to_tracelist(log_path):
    ''' 
    Converts the input XES event log into a list of list of activities corresponding to traces in the log
    
    input: XES log file path
    
    output: [[String]]
    '''
    log = xes_importer.import_log(log_path)
    tracelist = [[event['concept:name'] for event in trace] for trace in log]
    
    return tracelist

def log_to_sdb(log_path):
    ''' 
    Converts the input XES event log into a SequenceDB object, which stores the sequence database as [[Int]]
    
    input: XES log file path
    
    output: SequenceDB object
    '''
    tracelist = log_to_tracelist(log_path)
    sdb = SequenceDB()
    sdb.initialise_db(tracelist)

    return sdb

def apply_sdb_mapping_to_log(log_path, sdb):
    '''
    Applies the mapping from activities to indices of the given SequenceDB to an event log.
    If the log contains an activity not known to the SequenceDB, it is assigned the index -1.

    input: XES log file path, SequenceDB object

    output: [[Int]]
    '''
    tracelist = log_to_tracelist(log_path)
    db = [[sdb.activity_to_idx.get(act, -1) for act in trace] for trace in tracelist]

    return db