'''
this is the entrance of the programs.
OBEM.py is the main method of the Optimal Binary Exchange Algorithms.
util.py is the tool method of this program 
loaddata.py is the is used the load the data
guro.py is the tool method of the gurobi
'''

from OBEM import *

import sys

# choose the name from a,b,c,d,e,olda,oldb

# problem_choose = 'a'
# problem_choose = 'b'
# problem_choose = 'c'
# problem_choose = 'd'
# problem_choose = 'e'
# problem_choose = 'olda'
problem_choose = 'oldb'

print("solute the problem: "+ problem_choose)

history_record = []
sort_ins_list = Loaddata(problem_choose)

# statistical needs 
for ins in Insts:
    cpuneed += Apps[Insts[ins][0]].cpu
    memneed += Apps[Insts[ins][0]].mem
    diskneed += Apps[Insts[ins][0]].disk


cut_machine  = 5000
if problem_choose == 'a':
    cut_machine = 8000

# if you first run this program use this 
# FindSatisfySolution()
# SaveSatisfySolution(text)

# else run this can save you so much time 
LoadSatisfySolution(problem_choose)


Optimization(history_record,cut_machine)

history_record = np.array(history_record)
np.savetxt("submit"+problem_choose+'.csv', history_record, delimiter=',')
np.savetxt('TY'+problem_choose+'rate.csv', allrate, delimiter=',')
print("the program is end, and the solution is saved in ./submit/"+problem_choose+'.csv')
