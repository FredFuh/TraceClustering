# Represent sequences of traces as a list of integers, where the integers are indices 0,...,n of activities
# Introduce its own class mainly to bookkeep information about mapping from activities to indices
# the sequence database retains order of the traces from the log, thus no need to remember case id's

class SequenceDB:
    def __init__(self):
        """
        Constructor for the class, to represent a log as a list of sequence of integers.
        """
        self.db = []
        self.num_activities = 0
        self.activity_to_idx = dict()
        self.idx_to_activity = dict()

    # Assuming non empty tracelist
    def initialise_db(self, tracelist):
        """
        Initialises the sequence representation of a log with additional bookkeeping like mapping from activity names to integers.
    
        Parameters
        -----------
        tracelist ([[str]])
            List of traces, where a trace is a list of strings.
        """
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


def log_to_tracelist(log):
    """
    Converts the input EventLog into a list of list of activities corresponding to traces in the log.

    Parameters
    -----------
    log
        EventLog object

    Returns
    -----------
    tracelist ([[str]])
        List of traces, where a trace is a list of strings.
    """
    tracelist = [[event['concept:name'] for event in trace] for trace in log]
    
    return tracelist

def log_to_sdb(log):
    """
    Converts the input EventLog into a SequenceDB object, which stores the sequence database as [[int]].

    Parameters
    -----------
    log
        EventLog object

    Returns
    -----------
    sdb
        SequenceDB object
    """
    tracelist = log_to_tracelist(log)
    sdb = SequenceDB()
    sdb.initialise_db(tracelist)

    return sdb

def apply_sdb_mapping_to_log(log, sdb):
    """
    Applies the mapping from activities to indices of the given SequenceDB to an event log, and returns it as a list of sequences of activity indices.
    If the log contains an activity not known to the SequenceDB, it is assigned the index -1.

    Parameters
    -----------
    log
        EventLog object
    sdb
        SequenceDB object

    Returns
    -----------
    db ([[int]])
        List of sequences with activities in their integer representation.
    
    """
    tracelist = log_to_tracelist(log)
    db = [[sdb.activity_to_idx.get(act, -1) for act in trace] for trace in tracelist]
    # Maybe filter out -1 activities here

    return db