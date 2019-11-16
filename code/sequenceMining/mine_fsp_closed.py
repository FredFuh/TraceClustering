from sequenceDB import *

# Mining closed frequent items sets using a slightly simplified version of the CloFAST algorithm, due to abusing the fact that our itemsets are always of cardinality 1.

# placeholder
def mine_fsp_closed(sdb, min_sup):
    ''' 
    Mines the frequent sequent patterns (fsp's) of length 1 and the closed fsp's for the given SequenceDB. A simplified version of the algorithm CloFAST is implemented,
    with the major simplification being that itemsets of sequences from the SequenceDB always have exactly one element. Similar nomenclature to in the paper is used.
    The respective output fsp's are organized in lists of tuples, where the first entry is the fsp and the second is its absolute support.
    
    Args: 
        sdb (SequenceDB): The SequenceDB object
        min_sup (int): The absolute minimum support of a frequent sequence pattern
    
    Returns:
        [([int], int)], [([int], int)]: Returns two list of tuples, representing the fsp's of length 1 and the closed ones. A tuple's first entry is the fsp, while the second is the absolute support.
    '''
    # First build up the sparse id lists (sil) for all 1-itemsets, organised as [[Int]] where an activity index serves as the index to its id list in the sil
    # In contrast to the paper, the sil's store indices of activities (0 indexed) and not positions which start at 1
    # The CIET is not explicitly constructed, because the closed frequent itemsets are exactly the frequent 1-itemsets, since itemsets in our sequences are always of size 1
    db = sdb.db
    sils = build_sils(db, sdb.num_activities)
            
    return [], []

def build_sils(db, num_activities):
    '''
    Constructs the sparse id lists for a given sequence database and the number of activities num_activities, assuming the activities in the database are 0,..,num_activities-1

    Args:


    '''

    return []