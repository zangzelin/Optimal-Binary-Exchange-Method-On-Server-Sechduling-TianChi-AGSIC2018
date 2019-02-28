
import sys
import matplotlib.pyplot as plt
import copy
import pickle
# import matplotlib.pyplot as plt

import guro as g
from loaddata import *
from util import *

scorelist = {}
allrate = np.zeros((3000, 6000))


def FirstFitMethod(sort_ins_list):

    changelist = []
    num_hundred = 0
    num_strong = 0
    machinelist = GetUsefulMachineList()

    process = 0
    allnumber = len(Insts)
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

    changelist3 = FirstFitMethod(sort_ins_list)


def SaveSatisfySolution(text):

    f_Machines = open("initsolution/"+text+'b_Machines.data', 'wb')
    pickle.dump(Machines, f_Machines)
    f_Machines.close()
    f_Insts = open("initsolution/"+text+'b_Insts.data', 'wb')
    pickle.dump(Insts, f_Insts)
    f_Insts.close()
    f_Apps = open("initsolution/"+text+'b_Apps.data', 'wb')
    pickle.dump(Apps, f_Apps)
    f_Apps.close()
    allscore = CaculateScore()

    print('finsh find satisfy,and score is {}'.format(allscore))


def LoadSatisfySolution(text):

    f_Machines = open("initsolution/"+text+'b_Machines.data', 'rb')
    # pickle.dump(Machines, f_Machines)
    Machines1 = pickle.load(f_Machines)
    f_Machines.close()
    f_Insts = open("initsolution/"+text+'b_Insts.data', 'rb')
    # pickle.dump(Insts, f_Insts)
    Insts1 = pickle.load(f_Insts)
    f_Insts.close()
    f_App = open("initsolution/"+text+'b_Apps.data', 'rb')
    # pickle.dump(Insts, f_Insts)
    Apps1 = pickle.load(f_App)
    f_App.close()

    for machine in Machines1:
        Machines[machine] = Machines1[machine]
    for insts in Insts1:
        Insts[insts] = Insts1[insts]
    for app in Apps1:
        Apps[app] = Apps1[app]


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


def OptimalBinaryExchangeMethod(gap, cutthre, loop):
    # the optimal binary exchange method 
    # input:
    #       gap, the gap parmater used in choose machine 
    #       cutthre, the cutthre parmater used in choose machine 
    #       the max loop

    # load the global var scorelist which record the current score of machine 
    global scorelist

    # calculate the max score and the min score 
    firstscore = scorelist[min(scorelist, key=scorelist.get)]
    lastscore = scorelist[max(scorelist, key=scorelist.get)]

    firstscorelist = []
    lastscorelist = []

    # calculate the set of high score machines and the low score machines. 
    for mach in scorelist.keys():
        gaap = (lastscore - firstscore) * loop/10000 * 1.5
        if scorelist[mach] <= firstscore + gaap:
            firstscorelist.append([mach, firstscore])
        if scorelist[mach] >= lastscore - gaap:
            lastscorelist.append([mach, lastscore])

    # choose the machine with roulette method 
    rand1 = random.randint(0, len(firstscorelist)-1)
    rand2 = random.randint(0, len(lastscorelist)-1)
    firstone = firstscorelist[rand1]
    lastone = lastscorelist[rand2]

    # the most important part of the method 
    FindOptimal(firstone, lastone)

    # update the socrelist     
    scorelist[firstone[0]] = Machines[firstone[0]].score
    scorelist[lastone[0]] = Machines[lastone[0]].score

    if len(Machines[firstone[0]].insts) == 0 and int(firstone[0].split('_')[1]) < cutthre:
        scorelist.pop(firstone[0])
    if len(Machines[lastone[0]].insts) == 0 and int(lastone[0].split('_')[1]) < cutthre:
        scorelist.pop(lastone[0])

    return firstone, lastone, len(firstscorelist), len(lastscorelist)

# def HistoryRecord():


def Optimization(his, cutthre):
    # the main method of OBEM
    # input:
    #       his, the list of the history 
    #       currhre, the cutthre parmater used in choose machine  

    scoreall_history = []

    # set threshold of all machine to 1 for find the satisfy solution as soon as possible
    Globalthreshold = 1
    for machine in Machines:
        Machines[machine].IncreaseThreshold(Globalthreshold)

    # use the scorelist to record the score of all the machine
    global scorelist
    for machine in Machines:
        if len(Machines[machine].insts) != 0:
            Machines[machine].UpdateScore()
            scorelist[machine] = Machines[machine].score

    # the main loop of optimal
    for loop in range(10000):

        # set the gap as parmater
        gap = 0.000 + loop/(100000)
        # use the OBEM do one exchange
        firstone, lastone, firstscorenumber, lastscorenumber = OptimalBinaryExchangeMethod(
            gap, cutthre, loop)

        # Remove the machine every 500 loop
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
                        lastscorenumber,  meancpu, meanmem, meandisk, np.std(scoreall_history)])
            allrate[loop//50, :] = GetRateOfAllMachine()

            if len(scoreall_history) > 3:
                scoreall_history.pop(0)
                scoreall_history.append(scoreall)
            else:
                scoreall_history.append(scoreall)

            putlog = open('log/outlog', 'a')
            putlog.write('loop:{} score:{} group good: {} group bad:{} machine:{} CPU:{} MEM:{} DISK:{}  \n'.format(loop,
                                                                                                                    scoreall, firstscorenumber, lastscorenumber, len(scorelist), meancpu, meanmem, meandisk))
            putlog.close()

        # print the status every 1000 loop
        if loop % 1000 == 1:
            print('loop:{} \tscore:{} \tgroup good: {} \tgroup bad:{} \tmachine:{} \t std {}'.format(loop,
                                                                                                     scoreall, firstscorenumber, lastscorenumber, len(scorelist), np.std(scoreall_history)))

            if np.std(scoreall_history) < 20 and len(scoreall_history) > 3:
                print('cut machne')
                cutnum = ReduceMachine(cutthre)
                # if cutnum == 50:
                #     ReduceMachine(cutthre)
                #     ReduceMachine(cutthre)
    return 0
