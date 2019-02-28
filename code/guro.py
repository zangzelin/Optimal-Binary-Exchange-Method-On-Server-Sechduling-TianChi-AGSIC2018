# import numpy as np
from gurobipy import *
from util import *
# import loaddata1
import math


def mycallback(model, where):
    # the callback function used to limit the runing time.

    if where == GRB.Callback.MIP:
        time = model.cbGet(GRB.Callback.RUNTIME)
        best = model.cbGet(GRB.Callback.MIP_OBJBST)
        if time > 100 and best < GRB.INFINITY:
            model.terminate()


def main(o_inslist, o_machine, o_appcons):
    # app_cons, app_resources, instan_deploy, machine_resources = LoadData()

    ins_number = len(o_inslist)
    machine_number = len(o_machine)
    m = Model("schedule")

    ins_to_to_app_machine = []
    # Create decision variables for the foods to buy
    for i in range(ins_number):
        ins_to_to_app_machinei = []
        for j in range(machine_number):
            ins_to_to_app_machinei.append(
                m.addVar(
                    vtype=GRB.BINARY, name="ins {} to machine {} ".format(i, j)
                )
            )

    ins_to_machine = []
    # Create decision variables for the foods to buy
    for i in range(ins_number):
        ins_to_machine.append([])
        for j in range(machine_number):
            ins_to_machine[i].append(
                m.addVar(
                    vtype=GRB.BINARY, name="ins {} to machine {} ".format(i, j)
                )
            )

    for i in range(ins_number):
        m.addConstr(
            quicksum(ins_to_machine[i]) == 1
        )

    machine_status = []
    for i in range(machine_number):
        machine_status_detail = []
        # set cpu var value
        for j in range(98):
            machine_status_detail.append(
                m.addVar(
                    lb=0, ub=Machines[o_machine[i]].cpu, vtype=GRB.CONTINUOUS,
                    name="machine {} cpu {} stutus".format(i, j)
                )
            )
        # set mem var value
        for j in range(98):
            machine_status_detail.append(
                m.addVar(
                    lb=0, ub=Machines[o_machine[i]].mem, vtype=GRB.CONTINUOUS,
                    name="machine {} mem {} stutus".format(i, j)
                )
            )
        # set cpu var value
        machine_status_detail.append(
            m.addVar(
                lb=0, ub=Machines[o_machine[i]].disk, vtype=GRB.INTEGER,
                name="machine {} disk stutus".format(i)
            )
        )
        # set M var value
        machine_status_detail.append(
            m.addVar(
                lb=0, ub=Machines[o_machine[i]].P, vtype=GRB.INTEGER,
                name="machine {} P stutus".format(i)
            )
        )
        # set P var value
        machine_status_detail.append(
            m.addVar(
                lb=0, ub=Machines[o_machine[i]].M, vtype=GRB.INTEGER,
                name="machine {} M stutus".format(i)
            )
        )
        # set PM var value
        machine_status_detail.append(
            m.addVar(
                lb=0, ub=Machines[o_machine[i]].PM, vtype=GRB.INTEGER,
                name="machine {} PM stutus".format(i)
            )
        )
        machine_status.append(machine_status_detail)

    # set the constrain 
    ins_list = list(o_inslist)
    for pma in range(machine_number):
        for count in range(98):
            m.addConstr(machine_status[pma][count] == quicksum(
                (ins_to_machine[i][pma] * Apps[Insts[ins_list[i]][0]].cpu[count] for i in range(ins_number))))
        for count in range(98, 98*2):
            m.addConstr(machine_status[pma][count] == quicksum(
                (ins_to_machine[i][pma] * Apps[Insts[ins_list[i]][0]].mem[count-98] for i in range(ins_number))))
        m.addConstr(machine_status[pma][196] == quicksum(
            (ins_to_machine[i][pma] * Apps[Insts[ins_list[i]][0]].disk for i in range(ins_number))))

    # calculate the score
    score = []
    mid = []
    for ma in range(len(o_machine)):
        scorei = []
        midi = []
        for i in range(98):
            scorei.append(m.addVar(vtype=GRB.CONTINUOUS))
            midi.append(m.addVar(vtype=GRB.CONTINUOUS))
            m.addConstr(midi[i] == machine_status[ma][i] *
                        (1.0 / Machines[o_machine[ma]].cpu))
            m.addConstr(scorei[i] == max_(midi[i], 0.5))
        score.append(scorei)
        mid.append(midi)

    # set the object 
    m.setObjective(quicksum(score[0]) + quicksum(score[1]) +
                   quicksum(machine_status[0][i] for i in range(98))/1000.0 -
                   quicksum(machine_status[0][i] for i in range(98))/1000.0, GRB.MINIMIZE)
    m.setParam(GRB.Param.OutputFlag, 0)
    m.optimize()
    output = []
    m.Params.outputFlag = 0

    for i in range(len(o_inslist)):
        for ma in range(len(o_machine)):
            if abs(ins_to_machine[i][ma].X - 1.0) < 0.01:
                output.append(
                    [ins_list[i], Insts[ins_list[i]][1], o_machine[ma]])

    return output

