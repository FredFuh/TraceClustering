# URGENT: can't get imports to work, even with solutions to this from googling
# problem: importing a module from a "sibling" folder in the project

from ..sequence_mining.mine_fsp import get_first_larger_element_or_none
from cluster import get_sequence_scores, longest_common_prefix_length

db = [
    [0,1,6,5,2],
    [0,3,2,5],
    [0,4,5,6]
]

num_activities = 7
fsp_1 = [((0,),3), ((2,),2)]
fsp_2 = [((0,2),1)]
fsp_c = [((0,), 3),((0,2,5), 3)]
print(longest_common_prefix_length((0,),(0,2,5)))

s1, s2, s3 = get_sequence_scores(db, num_activities, fsp_1, fsp_2, fsp_c)
print(s1)
print(s2)
print(s3)