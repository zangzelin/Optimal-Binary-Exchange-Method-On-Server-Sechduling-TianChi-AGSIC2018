
import sys
import matplotlib.pyplot as plt
import copy
import pickle
# import matplotlib.pyplot as plt

import guro as g
from loaddata import *
from util import * 
scorelist = {}

allrate = np.zeros((3000,6000))

def GetRateOfAllMachine():
    rate = np.zeros((1,6000))
    for machine,i in zip(Machines ,range(len(Machines))):
        rate[0,i] = Machines[machine].cpurate
    return rate
def GetUsefulMachineList():
    machinelist = list(Machines)
    for machineitem in machinelist:
        if Machines[machineitem].use == 0:
            machinelist.remove(machineitem)

    return machinelist


def Reallocate(inst_id, machinelist, machine_id=""):

    randlist = random.sample(machinelist, len(machinelist))

    for machine_id in randlist:
        if Machines[machine_id].AvailableThreshold(inst_id) and Machines[machine_id].use == 1:
            Machines[machine_id].AddInst(inst_id)
            return machine_id
    return ":"


def Reallocatenew(inst_id, machine_id=""):

    # machinelist = GetUsefulMachineList(Machines)
    randlist = ["machine_{}".format(6000-i) for i in range(6000)]

    for machine_id in randlist:
        if Machines[machine_id].AvailableThreshold(inst_id) and Machines[machine_id].use == 1:
            Machines[machine_id].AddInst(inst_id)
            return machine_id
    return ":"


def NumberOfUsedMachine():
    n_usemachine = 0
    for mach in Machines:
        if len(Machines[mach].insts) != 0:
            n_usemachine += 1
    return n_usemachine


def LoadStep3(sort_ins_list):

    changelist = []
    num_hundred = 0
    num_strong = 0
    # sorted_ins_list = zzlsave.LoadSortIns('zzl/inssort/savetxt'+proboem+'.txt')
    machinelist = GetUsefulMachineList()

    process = 0
    allnumber = len(Insts)
    # NonDeploy.reverse()
    for i in range(len(Insts)):

        inst = sort_ins_list[i]
        app = Insts[inst][0]
        machine = Insts[inst][1]

        if machine == None:
            if process % 10000 == 0:
                print('find satify : finish {} use machine {}%'.format(
                    process/allnumber, NumberOfUsedMachine()))
            process += 1

            new_machine = Reallocate(inst, machinelist)
            if new_machine not in list(Machines):
                input('need strong relocate')
            else:
                changelist_current = [[inst, new_machine]]

            changelist += changelist_current

    print("after step findsatisfy : {} NonDeploy ins has been put into another machine! \n and  {} strong relocate, {} hundrade relocate".format(
        len(Insts), num_strong, num_hundred))

    return changelist


def Get_appcons(o_inslist):

    appset = set()
    for ins in o_inslist:
        appset.add(ins)

    applist = list(appset)
    o_appcons = []
    for app1 in applist:
        appconsi = []
        for app2 in applist:
            if app1 == app2:
                try:
                    a = 1+Inferrences[app1+" "+app2]
                except:
                    a = 100
                try:
                    b = 1+Inferrences[app2+" "+app1]
                except:
                    b = 100
            else:
                try:
                    a = Inferrences[app1+" "+app2]
                except:
                    a = 100
                try:
                    b = Inferrences[app2+" "+app1]
                except:
                    b = 100
            appconsi.append(min(a, b))
        o_appcons.append(appconsi)
    return o_appcons, applist


def IfCanPutInOneMachine(o_machine):

    out = True
    machine1 = o_machine[0]
    machine2 = o_machine[1]
    # o_inslist1 = []

    if Machines[machine1].cpu >= Machines[machine1].cpu:
        newmachine = copy.deepcopy(Machines[machine1])
        oldmachine = copy.deepcopy(Machines[machine2])
        o_inslist1 = list(Machines[machine2].insts)
        o_inslist2 = list(Machines[machine1].insts)
    else:
        newmachine = copy.deepcopy(Machines[machine2])
        oldmachine = copy.deepcopy(Machines[machine1])
        o_inslist1 = list(Machines[machine1].insts)
        o_inslist2 = list(Machines[machine2].insts)

    has_added_ins = []
    # if len(o_inslist2) > 0:
    #     print("zzl")
    for ins in o_inslist1:
        if newmachine.AvailableThreshold(ins):
            oldmachine.RemoveIns(ins)
            newmachine.AddInst(ins)
            has_added_ins.append(ins)
        else:
            out = False
            break

    for ins in has_added_ins:
        newmachine.RemoveIns(ins)
        oldmachine.AddInst(ins)
    return out


def PutInOneMachine(o_machine):
    machine1 = o_machine[0]
    machine2 = o_machine[1]

    if Machines[machine1].cpu >= Machines[machine1].cpu:
        for ins in list(Machines[machine2].insts):
            Machines[machine2].RemoveIns(ins)
            Machines[machine1].AddInst(ins)
    else:
        for ins in list(Machines[machine1].insts):
            Machines[machine1].RemoveIns(ins)
            Machines[machine2].AddInst(ins)


def FindOptimal(firstone, lastone):

    o_inslist = []
    o_machine = []

    for ins in list(Machines[firstone[0]].insts) + list(Machines[lastone[0]].insts):
        o_inslist.append(ins)

    o_appcons, applist = Get_appcons(o_inslist)
    o_machine.append(firstone[0])
    o_machine.append(lastone[0])

    if False and IfCanPutInOneMachine([firstone[0], lastone[0]]):
        print("put {} and {} to {}".format(
            firstone[0], lastone[0], firstone[0]))
        PutInOneMachine(o_machine)
        

    else:
        if Machines[o_machine[0]].disk > Machines[o_machine[1]].disk:
            o_machine.reverse()
        out = g.main(o_inslist, o_machine, o_appcons)

        for ins in list(Machines[firstone[0]].insts):
            Machines[firstone[0]].RemoveIns(ins)
        for ins in list(Machines[lastone[0]].insts):
            Machines[lastone[0]].RemoveIns(ins)
        for ins, mach1, mach2 in out:

            # Machines[mach1].RemoveIns(ins)
            Machines[mach2].AddInst(ins)


def CheckInsNumInMachine(machine_name):
    ins_set = Machines[machine_name].insts
    return len(ins_set)


def CutMachine(num):
    for i in range(num):
        Machines["machine_{}".format(i+1)].use = 0


def FindSatisfySolution():
    CutMachine(0)
    Globalthreshold = 1
    for machine in Machines:
        Machines[machine].IncreaseThreshold(Globalthreshold)

    sort_ins_list = []
    disklist = []
    for ins in Insts:
        disklist.append([ins, max(Apps[Insts[ins][0]].disk/1024,
                                  max(Apps[Insts[ins][0]].cpu)/92, max(Apps[Insts[ins][0]].mem)/288)])

    sort_ins_list = sorted(disklist, key=lambda item1: item1[1])
    sort_ins_list .reverse()
    for i in range(len(sort_ins_list)):
        sort_ins_list[i] = sort_ins_list[i][0]

    changelist3 = LoadStep3(sort_ins_list)


def SaveSatisfySolution(text):
    f_Machines = open("initsolution"+text+'b_Machines.data', 'wb')
    pickle.dump(Machines, f_Machines)
    f_Machines.close()
    f_Insts = open("initsolution"+text+'b_Insts.data', 'wb')
    pickle.dump(Insts, f_Insts)
    f_Insts.close()
    f_Apps = open("initsolution"+text+'b_Apps.data', 'wb')
    pickle.dump(Apps, f_Apps)
    f_Apps.close()
    allscore = CaculateScore()
    print('finsh find satisfy,and score is {}'.format(allscore))


def LoadSatisfySolution(text):
    f_Machines = open("initsolution"+text+'b_Machines.data', 'rb')
    # pickle.dump(Machines, f_Machines)
    Machines1 = pickle.load(f_Machines)
    f_Machines.close()
    f_Insts = open("initsolution"+text+'b_Insts.data', 'rb')
    # pickle.dump(Insts, f_Insts)
    Insts1 = pickle.load(f_Insts)
    f_Insts.close()
    f_App = open("initsolution"+text+'b_Apps.data', 'rb')
    # pickle.dump(Insts, f_Insts)
    Apps1 = pickle.load(f_App)
    f_App.close()

    for machine in Machines1:
        Machines[machine] = Machines1[machine]
    for insts in Insts1:
        Insts[insts] = Insts1[insts]
    for app in Apps1:
        Apps[app] = Apps1[app]


def caculatins():
    num_ins = 0
    for machine in Machines:
        num_ins += len(Machines[machine].insts)

    return num_ins


def ReduceMachine(cutthre):
    global scorelist
    leavemachinelist = []
    aimlist = []
    numberofcut = 0
    
    for machine in scorelist:
        if Machines[machine].use == 1:
            if int(machine.split('_')[1]) < cutthre:
                leavemachinelist.append(machine)
            else:
                aimlist.append(machine)
    random.shuffle(leavemachinelist)
    aimlist = aimlist+leavemachinelist[50:]
    leavemachinelist = leavemachinelist[:50]

    count = 0
    # plt.figure()
    for leavemachine in leavemachinelist:
        # print(leavemachine)
        count += 1
        cuthistory = []

        for ins in list(Machines[leavemachine].insts):
            for aimmachine in aimlist:
                if Machines[aimmachine].AvailableThreshold(ins):

                    Machines[aimmachine].AddInst(ins)
                    Machines[leavemachine].RemoveIns(ins)
                    cuthistory.append([aimmachine, ins])

                    break

        if len(Machines[leavemachine].insts) == 0 and leavemachine in scorelist:
            # print('cut {}'.format(leavemachine))
            # print(cuthistory)
            numberofcut += 1
            if leavemachine in scorelist:
                scorelist.pop(leavemachine)

        else:  # 没有成功的话重载
            for aimmachine, ins in cuthistory:
                # assert( Machines[leavemachine].AvailableThreshold(ins)  == True)
                Machines[leavemachine].AddInst(ins)
                Machines[aimmachine].RemoveIns(ins)
    print("successful cut machine {}".format(numberofcut))

    return numberofcut

def OptimalBinaryExchangeMethod(gap,cutthre,loop):
    global scorelist

    firstscore = scorelist[min(scorelist, key=scorelist.get)]
    lastscore = scorelist[max(scorelist, key=scorelist.get)]

    firstscorelist = []
    lastscorelist = []

    for mach in scorelist.keys():
        gaap =  (lastscore - firstscore) * loop/10000 *1.5
        if scorelist[mach] <= firstscore + gaap  :
            firstscorelist.append([mach, firstscore])
        if scorelist[mach] >= lastscore - gaap :
            lastscorelist.append([mach, lastscore])

    firstscorenumber = len(firstscorelist)
    lastscorenumber = len(lastscorelist)

    rand1 = random.randint(0, firstscorenumber-1)
    rand2 = random.randint(0, lastscorenumber-1)

    firstone = firstscorelist[rand1]
    lastone = lastscorelist[rand2]

    FindOptimal(firstone, lastone)

    scorelist[firstone[0]] = Machines[firstone[0]].score
    scorelist[lastone[0]] = Machines[lastone[0]].score

    if len(Machines[firstone[0]].insts) == 0 and int(firstone[0].split('_')[1]) < cutthre:
        scorelist.pop(firstone[0])
    if len(Machines[lastone[0]].insts) == 0 and int(lastone[0].split('_')[1]) < cutthre:
        scorelist.pop(lastone[0])

    return firstone, lastone, firstscorenumber, lastscorenumber

# def HistoryRecord():


def Optimization(his,cutthre):

    global scorelist
    mach_history = []
    scoreall_history = []

    Globalthreshold = 1
    for machine in Machines:
        Machines[machine].IncreaseThreshold(Globalthreshold)

    for machine in Machines:
        if len(Machines[machine].insts) != 0:
            Machines[machine].UpdateScore()
            scorelist[machine] = Machines[machine].score

    for loop in range(10000):
        gap = 0.000 + loop/(100000) 
        firstone, lastone, firstscorenumber, lastscorenumber = OptimalBinaryExchangeMethod(gap,cutthre,loop)

        # 如果机器里没有ins，则移除ins

            #  print('remove {}'.format(lastone[0]))

        if loop % 500 == 1:
            scoreall = CaculateScore()
            
            cpuuse = 0
            memuse = 0
            diskuse = 0
            for machine in scorelist:
                cpuuse += Machines[machine].cpu
                memuse += Machines[machine].mem
                diskuse += Machines[machine].disk
            meancpu = np.mean(cpuneed / cpuuse)
            meanmem = np.mean(memneed/memuse)
            meandisk = np.mean(diskneed/diskuse)
            his.append([scoreall, len(scorelist), firstscorenumber,
                        lastscorenumber,  meancpu ,meanmem , meandisk,np.std(scoreall_history)] )
            allrate[loop//50,:] = GetRateOfAllMachine()

            if len(scoreall_history) > 3:
                scoreall_history.pop(0)
                scoreall_history.append(scoreall)
            else:
                scoreall_history.append(scoreall)

            putlog = open('outlog', 'a')
            putlog.write('loop:{} score:{} group good: {} group bad:{} machine:{} CPU:{} MEM:{} DISK:{}  \n'.format(loop,
                                                                                              scoreall, firstscorenumber, lastscorenumber, len(scorelist), meancpu ,meanmem , meandisk ))
            putlog.close()

        if loop % 1000 == 1:
            # assert(caculatins() == 68219)
            print('loop:{} \tscore:{} \tgroup good: {} \tgroup bad:{} \tmachine:{} \t std {}'.format(loop,
                                                                                           scoreall, firstscorenumber, lastscorenumber, len(scorelist),np.std(scoreall_history) ))

            # print(scoreall_history, np.std(scoreall_history))
            if np.std(scoreall_history) < 20 and len(scoreall_history) > 3:
                print('cut machne')
                cutnum = ReduceMachine(cutthre)
                # if cutnum == 50:
                #     ReduceMachine(cutthre)
                #     ReduceMachine(cutthre)
    return 0


if __name__ == '__main__':
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

    FindSatisfySolution()
    SaveSatisfySolution(text)
    # LoadSatisfySolution(text)
    Optimization(his,cutthre)

    his = np.array(his)
    np.savetxt(text+'.csv', his, delimiter=',')
    np.savetxt('TY'+text+'rate.csv', allrate, delimiter=',')

