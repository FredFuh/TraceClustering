from sequenceDB import SequenceDB
from enum import Enum

# Mining closed frequent items sets using a slightly simplified version of the CloFAST algorithm, due to abusing the fact that our itemsets are always of cardinality 1.
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
    num_activities = sdb.num_activities
    sils = build_sils(db, num_activities)

    # Determine frequent 1-itemsets, which are also automatically the closed 1-itemsets as explained above
    cfi = []
    for act in range(num_activities):
        # count the number of sequences where the list of id's is not None
        sup = sum(1 for k in range(len(sils[act])) if sils[act][k])
        if sup >= min_sup:
            cfi.append(([act], sup))
    
    cset_root = Node([], [])   # root node does not need a meaningful vertical id list

    # A vertical id list (vil) is of type [int], indexed by sequence indices
    # No data structure to remember all vil's, just saved in each node
    # Initialise the cset tree here with its first level
    for seq, _ in cfi:
        act = seq[0]
        vil = [get_first_item_or_none(idlist) for idlist in sils[act]]
        node = Node(seq, vil)
        node.set_label(Label.CLOSED)
        node.set_parent(cset_root)
        cset_root.add_child(node)
    
    for child in cset_root.get_children():
        sequence_extension(child, min_sup, sils)

    cfsp = []
    get_closed_fsp_from_cset(cset_root, cfsp)
    # possible optimisation: don't traverse the whole tree to get cfsp's, but add them during the computation of the cset at the end of sequence_extension
    # remember that the dfs traversal in 'preorder' might be used in other modules
            
    return cfi, cfsp

def build_sils(db, num_activities):
    '''
    Constructs the sparse id lists (sil's) of every 1-itemset for a given sequence database and the number of activities num_activities, assuming the activities in the database are 0,..,num_activities-1

    Args:
        db ([[int]]): Sequence database in the form of the list of sequences
        num_activities (int): Number of different activities in the sequence database
    
    Returns:
        [[[int]]]: List of sil's for each 1-itemset. A sil of type [[int]] is the list of indices of an activity, indexed by the sequence index in the sequence database

    '''
    # In contrast to the paper, the sil's store indices of activities (0 indexed) and not positions which start at 1
    # Initialise the id-list for every activity as a list of None for each sequence (referred to as null in the paper), not using [] instead of None to save memory if the sil is sparse
    sils = [[None for i in range(len(db))] for act in range(num_activities)]
    for idx_seq in range(len(db)):
        seq = db[idx_seq]
        for idx_act in range(len(seq)):
            act = seq[idx_act]
            if not sils[act][idx_seq]: # check if the list of id's is None
                sils[act][idx_seq] = []
            sils[act][idx_seq].append(idx_act) 

    return sils

class Node:
    def __init__(self, seq, vil):
        self.seq = seq
        self.vil = vil
        self.label = None
        self.children = []
        self.parent = None
    
    def set_label(self, label):
        self.label = label
    
    def add_child(self, node):
        self.children.append(node)

    def set_parent(self, parent_node):
        self.parent = parent_node

    def get_children(self):
        return self.children

class Label(Enum):
    CLOSED = 0
    NONCLOSED = 1
    PRUNED = 2

def get_first_item_or_none(lst):
    if lst:
        return lst[0]
    else:
        return None

def vil_compute_support(vil):
    # generator to save memory, if slow change to list comprehension
    return sum(1 for id in vil if id is not None)

def get_closed_fsp_from_cset(node, lst):
    if node.label is Label.CLOSED:
        lst.append((node.seq, vil_compute_support(node.vil)))
    for child in node.get_children():
        get_closed_fsp_from_cset(child, lst)

def sequence_extension(node, min_sup, sils):
    check_closure_and_prune(node, sils)
    if node.label is Label.PRUNED:
        return

    vil_node = node.vil
    siblings = node.parent.get_children()   # I think siblings should also include the node itself, word might be misleading
    for u in siblings:
        vil_u = u.vil
        last_act = u.seq[-1]
        vil_new = [None] * len(vil_node)

        # S-Step
        for j in range(len(vil_node)):
            if (vil_node[j] is not None) and (vil_u[j] is not None):
                # If id lists in the sils are long (i.e. same activities appear often in one trace), index() might be inefficient
                sil_idx = sils[last_act][j].index(vil_u[j])   # that index must exist
                new_id = None
                for id in sils[last_act][j][sil_idx:]:
                    if id > vil_node[j]:
                        new_id = id
                        break
                vil_new[j] = new_id
            # else: vil_new[j] = None, i.e. do nothing because pre initialised with None
        
        # Possible optimisation: compute support during S-Step, not done to increase readability
        supp = vil_compute_support(vil_new)
        if supp >= min_sup:
            if supp == vil_compute_support(vil_node):
                node.set_label(Label.NONCLOSED)
            # create new cset node
            seq_new = node.seq[:]
            seq_new.append(last_act)
            node_new = Node(seq_new, vil_new)
            node_new.set_label(Label.CLOSED)
            node_new.parent = node
            node.children.append(node_new)
    
    for child in node.children:
        sequence_extension(child, min_sup, sils)
    
    # Possible optimisation: add self to output list of closed fsp's if the label is still closed

#stub
def check_closure_and_prune(node, sils):
    # Note that itemset closure does not need to be checked in our case, since all itemsets are of size 1 in the sequences and thus there are no proper supersets
    vils = []
    vils.insert(0,node.vil)
    n_p = node.parent
    while n_p is not None:   # iterate up to the root node, then in that iteration the parent of root is None
        vil_p = n_p.vil
        children = n_p.children
        for u in children:   # I think siblings without node itself should be fine here, but following paper
            vil_u = u.vil
            pred, virt_shift = sequence_closure(vil_u, vils, sils, node.seq)
            if pred:
                if virt_shift:
                    node.set_label(Label.PRUNED)
                else:
                    node.set_label(Label.NONCLOSED)
                return
        vils.insert(0,vil_p)
        n_p = n_p.parent
    return


def sequence_closure(vil, vil_list, sils, alpha):
    pred = True
    virt_shift = False
    vil_alpha = vil_list[-1]
    a_i_idx = len(alpha) - len(vil_list)
    # Compute the suffix starting from the i-th activity a_i of alpha for the shiftSC predicate check to always have a_i available
    alpha_suffix = alpha[a_i_idx:]
    for j in range(len(vil_alpha)):
        if vil_alpha[j] is None:
            continue
        else:
            pred_j, shifted = shiftSC(vil[j], [vil_l[j] for vil_l in vil_list], sils, alpha_suffix, j)
            if not pred_j:
                pred = False
                break
            virt_shift = max(virt_shift, shifted)   # if virt_shift was True already then keep it True

    return pred, virt_shift

def shiftSC(vilj, vilj_list, sils, alpha_suffix, j):
    shifted = False
    if (vilj is None) or (len(vilj_list) == 0):
        return False, shifted
    elif (vilj_list[0] is not None) and (vilj < vilj_list[0]):
        return True, shifted
    else:
        shifted = True
        vilj_delta = vilj_list[0]
        a_i = alpha_suffix[0]
        # Since vilj >= vilj_delta holds here, we can start looking in the sil of a_i starting from after the number saved in vilj_delta, don't need to check all sil entries
        sil_idx = sils[a_i][j].index(vilj_delta)
        for t_a_i in sils[a_i][j][sil_idx+1:]:
            # look for t_a_i larger than vilj (gamma)
            if (t_a_i > vilj):
                sub_pred, _ = shiftSC(t_a_i, vilj_list[1:], sils, alpha_suffix[1:], j)
                if sub_pred:
                    return True, shifted
        # If loop finished without returning true, then no t_a_i was found, thus predj is false; Also note that the shifted boolean value is not of importance if the predicate is false
        return False, False