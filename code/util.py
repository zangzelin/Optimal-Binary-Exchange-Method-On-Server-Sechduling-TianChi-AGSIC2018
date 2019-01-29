import logging
import logging.handlers
import random
from functools import reduce
from math import exp, expm1

import numpy as np

# 设置log文件用于debug
LOG_FILE = './log/log1.log'
handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, maxBytes=1024*1024, backupCount=5)  # 实例化handler
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'

formatter = logging.Formatter(fmt)   # 实例化formatter
handler.setFormatter(formatter)      # 为handler添加formatter

logger = logging.getLogger('log')    # 获取名为tst的logger
logger.addHandler(handler)           # 为logger添加handler
logger.setLevel(logging.DEBUG)

numofloop = 10000
cpuneed = 0
memneed = 0
diskneed = 0
# Global variable, APP stores the object of the APP,
# the key is the id of the app,
# and the value is the instance of the APP object.
Apps = {}

# Global variables store each machine class key is the machine id,
# value is the machine object instance
Machines = {}

Jobs = {}
# Global Variables The Inferrence key between each app is appa+' 'appb,
# value is the constraint value
Inferrences = {}

# Global variables store each Insts instance class
Insts = {}

# The global variable stores the current deployment status.
# The key is the inst id,
# the value is the binary group [appid, machine_id],
# the app_id represents the corresponding app number,
# and the machine_id is empty.
Deployments = {}

# Global variables indicate insts that have been deployed in advance
PreDeploy = []

# Global variables indicate insts that are not deployed in advance
NonDeploy = []

# input file name
app_resources_file = "./../data/app_resources.csv"
app_interference_file = "./../data/app_interference.csv"

inst_deploy_file_a = "./../data/instance_deploy.a.csv"
inst_deploy_file_b = "./../data/instance_deploy.b.csv"
inst_deploy_file_c = "./../data/instance_deploy.c.csv"
inst_deploy_file_d = "./../data/instance_deploy.d.csv"
inst_deploy_file_e = "./../data/instance_deploy.e.csv"

machine_resources_file_a = "./../data/machine_resources.a.csv"
machine_resources_file_b = "./../data/machine_resources.b.csv"
machine_resources_file_c = "./../data/machine_resources.c.csv"
machine_resources_file_d = "./../data/machine_resources.d.csv"
machine_resources_file_e = "./../data/machine_resources.e.csv"

job_info_file_a = "outlineJobSort/time_A_job.csv"
job_info_file_b = "./../data/job_info.b.csv"
job_info_file_c = "./../data/job_info.c.csv"
job_info_file_d = "./../data/job_info.d.csv"
job_info_file_e = "./../data/job_info.e.csv"


# output file name
# zzl_solution_file_a = "./zzl/submit/solution_a.csv"
# zzl_solution_file_b = "./zzl/submit/solution_b.csv"
# zzl_solution_file_c = "./zzl/submit/solution_c.csv"
# zzl_solution_file_d = "./zzl/submit/solution_d.csv"
# zzl_solution_file_e = "./zzl/submit/solution_e.csv"

# # primary solution
# primarySolution_file = "./output/primarysolution.csv"

# # refined solution
refinedSolution_file = "./submit/refinedsolution.csv"


olddata_app_interference_file = 'data/olddata/scheduling_preliminary_app_interference_20180606.csv'

outfile = open(refinedSolution_file, 'w')

class App:

    def __init__(self, app_id, cpu, mem, disk, P, M, PM):
        self.id = app_id
        self.cpu = cpu
        self.mem = mem
        self.disk = disk
        self.P = P
        self.M = M
        self.PM = PM
        self.instance = []
        self.stability = np.std(self.cpu)
        self.avgCpu = np.mean(self.cpu)
        self.intimateApps = set([])

class Job:

    def __init__(self,job_id, cpu, mem, number_of_instance, execution_time, dependency_task_id, range_1, range_2 ):
        self.id = job_id
        self.cpu = cpu
        self.mem = mem
        self.number_of_instance = number_of_instance
        self.execution_time = execution_time
        self.dependency_task_id = dependency_task_id
        self.starttime = range_1
        self.endtime = range_2

'''
Machine class
- Member variables
    1. List of Inst placed on the machine: insts(set)
    2. The number of each deployed app on the machine: appCounter(dictionary)
    3. Machine id: id(string)
    4. Total amount of resources of cpu: cpu(1*1 numpy array)
    5. Total memory resources: mem(1*1 numpy array)
    6. Disk total resources: disk (scalar)
    7. P: P (scalar)
    8. M: M (scalar)
    9. PM: PM (scalar)
    10. cpu usage rate: cpurate(float)
    11. cpu usage cap (optional): cputhreshold(float)
    12. Remaining cpu resources: rcpu(1*98 numpy array)
    13. Remaining mem resources: rmem(1*98 numpy array)
    14. Remaining disk resources: rdisk (scalar)
    15. Remaining P resources: rP()
    16. Remaining M resources:
- member function
    1.init initialization
    2.available(self,inst_id): Check if inst_id(string) can be inserted into the current machine
    3.available(self,inst_id): Detect if inst_id(string) can be inserted into the current machine
    4.availableThreshold(self, inst_id): Check if the inst is added to the machine when the threshold is limited.
    5.add_inst(self, inst_id): add instance inst_id to the current machine
    6.remove(self, inst_id): Move out the instance inst_id
'''


class Machine:
    def __init__(self, machine_id, cpu, mem, disk, P, M, PM):
        self.insts = set([])
        self.appCounter = {}
        self.id = machine_id
        self.cpu = cpu
        self.mem = mem
        self.disk = disk
        self.P = P
        self.M = M
        self.PM = PM
        self.cputhreshold = 0.5
        self.cpurate = 0.0
        # Remaining resources
        self.rcpu = cpu
        self.rmem = mem
        self.rdisk = disk
        self.rP = P
        self.rM = M
        self.rPM = PM
        # Current machine score
        self.scorenew = 0.0
        self.score = 0.0
        self.alpha = 10
        self.beta = 0.5
        # Machine cpu stability
        self.stability = 0  # np.std(self.cpu-self.rcpu)
        # Mean value of cpu utilization
        self.avgCpurate = 0  # np.mean((self.cpu-self.rcpu)/self.cpu)
        self.use = 1

    def Available100(self, inst_id):

        # Check if the inst_id can be added to the current machine
        # under the condition of 100% utilization

        curApp = Apps[Insts[inst_id][0]]
        # check  cpu
        compare = np.greater_equal(self.rcpu, curApp.cpu)
        compare = reduce(lambda x, y: x & y, compare)
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate cpu on "+ self.id)
            return False

        # check  mem
        compare = np.greater_equal(self.rmem, curApp.mem)
        compare = reduce(lambda x, y: x & y, compare)
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate mem on "+ self.id)
            return False

        # check  disk
        compare = self.rdisk >= curApp.disk
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate disk on "+ self.id)
            return False

        # check  P
        compare = self.rP >= curApp.P
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate P on "+ self.id)
            return False

        # check  M
        compare = self.rM >= curApp.M
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate M on "+ self.id)
            return False

        # check  PM
        compare = self.rPM >= curApp.PM
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate PM on "+ self.id)
            return False

        # check inferrence
        try:
            for appa in self.appCounter:
                if appa+" "+curApp.id in Inferrences:
                    if curApp.id not in self.appCounter:
                        if 1 > Inferrences[appa+" "+curApp.id]:
                            logger.debug(
                                inst_id+" Inferrence0 between "+appa+" "+curApp.id+" broken "+"on " + self.id)
                            # logger.debug(inst_id,str(self.insts),self.id)
                            # print(Inferrences[appa+" "+curApp.id])
                            return False
                    elif self.appCounter[curApp.id]+1 > (Inferrences[appa+" "+curApp.id]+(appa == curApp.id)):
                        logger.debug(inst_id+"Inferrence2 between " +
                                     appa+" "+curApp.id+" broken "+"on " + self.id)
                        # logger.debug(inst_id,str(self.insts),self.id)
                        return False

                if curApp.id+" "+appa in Inferrences:
                    # if curApp.id not in self.appCounter:
                    if (self.appCounter[appa] + (appa == curApp.id)) > (Inferrences[curApp.id+" "+appa] + (appa == curApp.id)):
                        logger.debug(inst_id+" Inferrence3 between " +
                                     curApp.id+" "+appa+" broken "+"on " + self.id)
                        return False
        except:
            logger.debug("Bad error allocate " +
                         inst_id + " of App "+curApp.id)
        # constraint satisfy
        return True

    def AvailableEmpty(self, inst_id):

        # Check if the inst_id can be added to the current machine
        # under the condition of 100% utilization

        curApp = Apps[Insts[inst_id][0]]
        # check  cpu
        compare = np.greater_equal(self.cpu, curApp.cpu)
        compare = reduce(lambda x, y: x & y, compare)
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate cpu on "+ self.id)
            return False

        # check  mem
        compare = np.greater_equal(self.mem, curApp.mem)
        compare = reduce(lambda x, y: x & y, compare)
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate mem on "+ self.id)
            return False

        # check  disk
        compare = self.disk >= curApp.disk
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate disk on "+ self.id)
            return False

        # check  P
        compare = self.P >= curApp.P
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate P on "+ self.id)
            return False

        # check  M
        compare = self.M >= curApp.M
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate M on "+ self.id)
            return False

        # check  PM
        compare = self.PM >= curApp.PM
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate PM on "+ self.id)
            return False

        # check inferrence
        try:
            for appa in self.appCounter:
                if appa+" "+curApp.id in Inferrences:
                    if curApp.id not in self.appCounter:
                        if 1 > Inferrences[appa+" "+curApp.id]:
                            logger.debug(
                                inst_id+" Inferrence0 between "+appa+" "+curApp.id+" broken "+"on " + self.id)
                            # logger.debug(inst_id,str(self.insts),self.id)
                            # print(Inferrences[appa+" "+curApp.id])
                            return False
                    elif self.appCounter[curApp.id]+1 > (Inferrences[appa+" "+curApp.id]+(appa == curApp.id)):
                        logger.debug(inst_id+"Inferrence2 between " +
                                     appa+" "+curApp.id+" broken "+"on " + self.id)
                        # logger.debug(inst_id,str(self.insts),self.id)
                        return False

                if curApp.id+" "+appa in Inferrences:
                    # if curApp.id not in self.appCounter:
                    if (self.appCounter[appa] + (appa == curApp.id)) > (Inferrences[curApp.id+" "+appa] + (appa == curApp.id)):
                        logger.debug(inst_id+" Inferrence3 between " +
                                     curApp.id+" "+appa+" broken "+"on " + self.id)
                        return False
        except:
            logger.debug("Bad error allocate " +
                         inst_id + " of App "+curApp.id)
        # constraint satisfy
        return True

    def AvailableThreshold(self, inst_id):
        # Check if the inst_id can be added to the current machine
        # under the condition that the utilization is up to self.threshold

        curApp = Apps[Insts[inst_id][0]]
        # check  disk
        compare = self.rdisk >= curApp.disk
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate disk on "+ self.id)
            return False
        
        # check  cpu
        compare = np.greater_equal(self.rcpu, curApp.cpu)
        compare = reduce(lambda x, y: x & y, compare)
        if(not compare):
            logger.debug(inst_id+" fails to acllocate cpu on " + self.id)
            return False

        # check cpu threshold
        compare = self.cputhreshold >= np.max(
            (self.cpu - self.rcpu + curApp.cpu)/self.cpu)
        if(not compare):
            logger.debug(inst_id+" break the cpu threshold " + self.id)
            return False

        # check  memory
        compare = np.greater_equal(self.rmem, curApp.mem)
        compare = reduce(lambda x, y: x & y, compare)
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate mem on "+ self.id)
            return False



        # check  P
        compare = self.rP >= curApp.P
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate P on "+ self.id)
            return False

        # check  M
        compare = self.rM >= curApp.M
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate M on "+ self.id)
            return False

        # check  PM
        compare = self.rPM >= curApp.PM
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate PM on "+ self.id)
            return False

        # check inferrence
        try:
            for appa in self.appCounter:
                if appa+" "+curApp.id in Inferrences:
                    if curApp.id not in self.appCounter:
                        if 1 > Inferrences[appa+" "+curApp.id]:
                            # logger.debug(inst_id+" Inferrence0 between "+appa+" "+curApp.id+" broken "+"on "+ self.id)
                            # logger.debug(inst_id,str(self.insts),self.id)
                            # print(Inferrences[appa+" "+curApp.id])
                            return False
                    elif self.appCounter[curApp.id]+1 > (Inferrences[appa+" "+curApp.id]+(appa == curApp.id)):
                        # logger.debug (inst_id+"Inferrence2 between "+appa+" "+curApp.id+" broken "+"on "+ self.id)
                        # logger.debug(inst_id,str(self.insts),self.id)
                        return False

                if curApp.id+" "+appa in Inferrences:
                    # if curApp.id not in self.appCounter:
                    if (self.appCounter[appa] + (appa == curApp.id)) > (Inferrences[curApp.id+" "+appa] + (appa == curApp.id)):
                        # logger.debug(inst_id+" Inferrence3 between "+curApp.id+" "+appa+" broken "+"on "+ self.id)
                        return False
        except:
            logger.debug("Bad error allocate " +
                         inst_id + " of App "+curApp.id)

        # constraint satisfy
        return True

    def AddInst(self, inst_id):
        # Add instance inst to machine's list

        self.insts.add(inst_id)
        # Add the current app to the machine count
        if Insts[inst_id][0] not in self.appCounter:
            self.appCounter[Insts[inst_id][0]] = 1
        else:
            self.appCounter[Insts[inst_id][0]] += 1

        # Correct the current deployment location of Inst
        Insts[inst_id][1] = self.id
        # Calculate the remaining cpu resources
        self.rcpu = self.rcpu - Apps[Insts[inst_id][0]].cpu
        # Calculate cpu usage
        self.cpurate = max((self.cpu-self.rcpu)/self.cpu)

        # Calculate remaining mem resources
        self.rmem = self.rmem - Apps[Insts[inst_id][0]].mem

        # Calculate the remaining disk resources
        self.rdisk = self.rdisk - Apps[Insts[inst_id][0]].disk

        # Calculate the remaining P resources
        self.rP = self.rP - Apps[Insts[inst_id][0]].P

        # Calculate the remaining P resources
        self.rM = self.rM - Apps[Insts[inst_id][0]].M

        # Calculate the remaining PM resources
        self.rPM = self.rPM - Apps[Insts[inst_id][0]].PM

        # Update stability value
        self.UpdateStatus()
        return True

    def RemoveIns(self, inst_id):
        # Remove inst_id from machine
        self.insts.remove(inst_id)

        # Add the current app to the machine count
        self.appCounter[Insts[inst_id][0]] -= 1
        if self.appCounter[Insts[inst_id][0]] == 0:
            del self.appCounter[Insts[inst_id][0]]

        self.rcpu = self.rcpu + Apps[Insts[inst_id][0]].cpu
        self.cpurate = max((self.cpu-self.rcpu)/self.cpu)
        self.rmem = self.rmem + Apps[Insts[inst_id][0]].mem
        self.rdisk = self.rdisk + Apps[Insts[inst_id][0]].disk
        self.rP = self.rP + Apps[Insts[inst_id][0]].P
        self.rM = self.rM + Apps[Insts[inst_id][0]].M
        self.rPM = self.rPM + Apps[Insts[inst_id][0]].PM

        self.UpdateStatus()
        return True

    def ScoreChangeOfAddInst(self, inst_id):
        # Returns the increase in penalty score
        # after adding inst_id to the current machine
        
        curApp = Apps[Insts[inst_id][0]]
        score = 0
        for rate in (self.cpu - (self.rcpu - curApp.cpu))/self.cpu:
            score += (1 + self.alpha*(exp(max(rate-self.beta, 0))-1))
        return score - self.score

    def ScoreChangeOfRemoveInst(self, inst_id):
        # Returns the reduction in penalty score 
        # after shifting out inst_id to the current machine
        
        curApp = Apps[Insts[inst_id][0]]
        score = 0
        if(len(self.insts) == 1):
            score = 0
        else:
            for rate in (self.cpu - (self.rcpu + curApp.cpu))/self.cpu:
                score += (1 + self.alpha*(exp(max(rate-self.beta, 0))-1))
        return score - self.score

    def VarianceChangeOfAddInst(self, inst_id):
        
        # Returns the increase in penalty score 
        # after adding inst_id to the current machine 
        # (the smaller the standard deviation, the better)
       
        curApp = Apps[Insts[inst_id][0]]
        curVariance = np.std(self.cpu-(self.rcpu-curApp.cpu))
        return curVariance - self.stability

    def VarianceChangeOfRemoveInst(self, inst_id):
        # Returns the change in machine stability 
        # after moving inst_id to the current machine 
        # (the smaller the standard deviation, the better)
        
        curApp = Apps[Insts[inst_id][0]]
        curVariance = np.std(self.cpu-(self.rcpu+curApp.cpu))
        return curVariance - self.stability

    def IncreaseThreshold(self, threhold):
        # Change the upper limit of the current machine's CPU usage
        self.cputhreshold = threhold

    # The following is an internal status update function 
    # that does not need to be called externally.
    def ResetStatus(self):
        if len(self.insts) == 0:
            self.cpurate = 0.0
            # Remaining resources
            self.rcpu = self.cpu
            self.rmem = self.mem
            self.rdisk = self.disk
            self.rP = self.P
            self.rM = self.M
            self.rPM = self.PM
            # Current machine score
            self.score = 0.0
            # Machine cpu stability
            self.stability = 0  # np.std(self.cpu-self.rcpu)
            # Mean value of cpu utilization
            self.avgCpurate = 0  # np.mean((self.cpu-self.rcpu)/self.cpu)

    def UpdateStatus(self):
        # Update the current machine status, 
        # including scores, stability, average utilization, etc.

        if(len(self.insts) == 0):
            self.ResetStatus()
        else:
            # 更新当前机器的得分
            self.UpdateScore()
            # 更新稳定性和平均利用率
            self.stability = np.std(self.cpu-self.rcpu)
            self.avgCpurate = np.mean((self.cpu-self.rcpu)/self.cpu)

    def UpdateScore(self):
        # Update the score of the current machine
        self.score = 0
        if len(self.insts) == 0:
            self.score = 0
        else:
            for rate in (self.cpu-self.rcpu)/self.cpu:
                self.score += (1 + self.alpha*(exp(max(rate-self.beta, 0))-1))
        self.score /= 98
        self.scorenew = 0
        if len(self.insts) == 0:
            self.scorenew = 0
        else:
            for rate in (self.cpu-self.rcpu)/self.cpu:
                self.scorenew +=  self.alpha*(exp(rate-self.beta))
        self.scorenew /= 98# print("number of grater than 0.5 {}".format(count))
        return True


# Comparing the stability of the inst app from stable to unstable
def CaculateScore():
    score = 0
    for machine in Machines:
        # Machines[machine].UpdateScore()
        score += Machines[machine].score

    return score

def stable_compare(instl, instr):
    return Apps[Insts[instl][0]].stability - Apps[Insts[instr][0]].stability

# 从不稳定到稳定


def stable_compare_reverse(instl, instr):
    return Apps[Insts[instr][0]].stability - Apps[Insts[instl][0]].stability

# 比较cpu大小的函数
# 从小到大排列


def cpu_compare(machinel, machiner):
    return Machines[machinel].cpu - Machines[machiner].cpu

# 从大到小排列


def cpu_compare_reverse(machinel, machiner):
    return Machines[machiner].cpu - Machines[machinel].cpu

# 比较cpu使用率的函数
# 从小到大排


def cpurate_compare(machinel, machiner):
    return Machines[machinel].avgCpurate - Machines[machiner].avgCpurate

# 从大到小排序


def cpurate_compare_reverse(machinel, machiner):
    return Machines[machiner].avgCpurate - Machines[machinel].avgCpurate

# 比较Inst的cpu使用
# 从小到大排


def inst_cpurate_compare(instl, instr):
    appl = Apps[Insts[instl][0]]
    appr = Apps[Insts[instr][0]]
    return appl.avgCpu - appr.avgCpu


def inst_cpurate_compare_reverse(instl, instr):
    appl = Apps[Insts[instl][0]]
    appr = Apps[Insts[instr][0]]
    return appr.avgCpu - appl.avgCpu


def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K:
        def __init__(self, obj, *args):
            self.obj = obj

        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0

        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0

        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0

        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K

# 辅助类函数


def exchangeScoreChangeOfInsts(inst_1, inst_2):
    '''
        交换 machine_1上的 inst1 和 machine_2 上的inst_2
    '''
    machine1 = Insts[inst_1][1]
    machine2 = Insts[inst_2][1]
    score = 0
    # 对于inst_1,inst_2而言,所在机器相同则无需调换
    if(machine1 == machine2):
        return score

    if(Machines[machine1].available(inst_2) and Machines[machine1].scoreChangeOfAddInst(inst_2) + Machines[machine2].scoreChangeOfRemoveInst(inst_2) < 0):
        score += MoveInstToMachine(inst_2, machine1)
        outfile.write(inst_2+','+machine1+'\n')

    if (Machines[machine2].available(inst_1) and Machines[machine1].scoreChangeOfRemoveInst(inst_1) + Machines[machine2].scoreChangeOfAddInst(inst_1) < 0):
        score += MoveInstToMachine(inst_1, machine2)
        outfile.write(inst_1+','+machine2+'\n')

    if(score < 0):
        return score

    if Machines[machine1].available(inst_2):
        # 先把inst2 移到machine 1上
        score = MoveInstToMachine(inst_2, machine1)
        if (Machines[machine2].available(inst_1)):
            score += Machines[machine1].scoreChangeOfRemoveInst(
                inst_1) + Machines[machine2].scoreChangeOfAddInst(inst_1)
        if(score >= 0):
            MoveInstToMachine(inst_2, machine2)
            score = 0
        else:
            MoveInstToMachine(inst_1, machine2)
            outfile.write(inst_2+','+machine1+'\n')
            outfile.write(inst_1+','+machine2+'\n')
    return score


def MoveInstToMachine(inst, target_machine):
    score = 0
    if Insts[inst][1] == None:
        '''
            当前inst尚未布置
        '''
        score = Machines[target_machine].scoreChangeOfAddInst(inst)
        Machines[target_machine].AddInst(inst)
        return score
    else:
        try:
            assert(Machines[target_machine].available(inst))
        except:
            print(inst, target_machine, Insts[inst][1])
            exit(-1)
        '''
            当前inst已经布置
        '''
        # 找出当前的机器
        curMachine = Insts[inst][1]
        curScore = Machines[curMachine].score + Machines[target_machine].score
        # Move machine
        Machines[curMachine].RemoveIns(inst)
        Machines[target_machine].AddInst(inst)
        return Machines[curMachine].score + Machines[target_machine].score - curScore
