'''
this is the entrance of the programs.
OBEM.py is the main method of the Optimal Binary Exchange Algorithms.
util.py is the tool method of this program 
loaddata.py is the is used the load the data
guro.py is the tool method of the gurobi
'''

from OBEM import *

import sys

# text = sys.argv[1]
text = 'oldb'
print(text)
his = []
sort_ins_list = Loaddata(text)
for ins in Insts:
    cpuneed += Apps[Insts[ins][0]].cpu
    memneed += Apps[Insts[ins][0]].mem
    diskneed += Apps[Insts[ins][0]].disk

cutthre  = 5000
if text == 'a':
    cutthre = 8000

# FindSatisfySolution()
# SaveSatisfySolution(text)
LoadSatisfySolution(text)
Optimization(his,cutthre)

his = np.array(his)
np.savetxt(text+'.csv', his, delimiter=',')
np.savetxt('TY'+text+'rate.csv', allrate, delimiter=',')

