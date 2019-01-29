# Optimal-Binary-Exchange-Method-On-Server-Sechduling-TianChi-AGSIC2018

This code solves the scheduling problem of a large number of servers.
The 68219 tasks are scheduled to 6000 servers, taking into account the constraints of the server's cpu, MEM, DISK, and app constraints.
I have tried to use PYHON, MINZINC, GUROBI and other tools to solve, using the firstfit method, localsearch method and random algorithm.

# English version of the problem description
====================================================================================================================================

![1440-天池-en.jpg](https://work.alibaba-inc.com/aliwork_tfs/g01_alibaba-inc_com/tfscom/TB1wvJPoOCYBuNkHFCcXXcHtVXa.tfsprivate.jpg)  

====================================================================================================================================

Alibaba Global Scheduling Algorithm Competition
===============================================

The problem in the preliminary is an abstraction of one of many our scenarios in production, where the number of constraints is reduced. The problem would help participants understand our concern. In the semi-final, we will add more constraints as well as more optimization objectives. The problem for semi-final will not be published until the end of preliminary. For the accurate schedule of the competition, please refer to the introduction.

We look forward to having you and your teammates share your ideas to solve the problem!

Note: The current datasets are for participants to get an idea of the problem. They may be changedlater after more evaluation and possible feedback. The final data will be determined with the annoucement of the evaluation on Aug 20th.

Semi-final is built based on preliminary with some modifications on both data and constraints.

Constraints for rescheduling the instances
------------------------------------------

The rescheduling of instances is more practical. The rescheduling should be executed in multiple rounds, and in each round, there can be many rescheduling actions. A rescheduling is carried out in a create-then-delete manner. For instance:

    1,inst1,A
    1,inst2,A
    2,inst3,B
    

describes a _double-phase_ rescheduling plan. In the 1st round, inst1 and inst2 are rescheduled to machine A (suppose both inst were on other machines), and this is executed as follows. In the first phase, machine A creates new inst1 and inst2, if succeed, inst1 and inst2 are deleted on their original hosts. After these actions, the 2nd round is executed (inst3 to machine B).

If rescheduling fails, the scheduling of inst'sise terminated.

**Constraints on rescheduling**: The is no limit on the number of rescheduling action per round, but there is a limit on the number of rounds k: k<= 3.

scheduling of batch computation workloads
-----------------------------------------

In preliminary, there are only instances from online service applications, whose performance must be guaranteed. One approach on protecting their performance is to maintain the resource utilization at a moderate level (50% in preliminary). However, this approach causes low resource utilization rate. In production, to reach higher resource utilization, some batch computation workloads are deployed too.

A batch task is defined in `job_info.x.csv`, in the form of:

    task_id, cpu, mem, number_of_instances, execution_time, dependency_task_id
    

in which:

*   The unit of execution_time is minute. The 98 time points in cpu/mem curve represent the resource consumption at \[0,15), \[15,30), ..., \[1455,1470) (98 time spans in total)
*   The start time of any instance cannot be earlier than the completion of its dependency task
*   All task instances must be completed within \[0, 1470)
    *   note that for any task, iif all instances for this task are completed, then the task can be considered as completed.
*   Instances of tasks cannot be rescheduled (once scheduled, cannot move)

The valid solution shoud consis of two parts:

*   for application instances: `<scheduling-round_number, instance_id, target_machine_id>`
*   for batch task instances: `task_instance_id, target-machine-id, start_time, number_of_instances_to_start`

Once batch task instances begin to get scheduled, no more rescheduling of application instances is allowed.

Evaluation modification
-----------------------

The evaluation method is updated based on the preliminary, where `a=10` is changed to

    a=(1+<number of inst's on this machine>)
    

Data description
----------------

There are 5 datasets for semi-final: a, b, c, d, e, each representing an individual problem. They are of the same format and constraints, and the differences are their numeric values.

*   app\_interference.csv and app\_resources.csv are shared by all 5 sets of data
*   instance\_deploy.x.csv, job\_info.x.csv, machine_resources.x.csv are the dedicated data for dataset x.

The submission should be in the order of a, b, c, d, e, separated by #

Below is an example:

    1, inst1, machine_a
    task_1, machine_a, 10, 31
    #
    1, inst1, machine_b
    2, inst2, machine_c
    task_1, machine_c, 10, 28
    

The score of a team is the sum of 5 scores.

Preparation for final submission
--------------------------------

The qualification to final is partially determined by the rank in the semi-final. Also, we will ask the top teams in the semi-final to submit their code and a brief document for offline review. We have the following suggestions to the participants:

*   Please organize your code as recommended in the problem description in preliminary (link)
*   Please prepare a brief doc, including:
    *   Your idea on solving the problem
    *   The computation environment (hardware, software, etc) and execution time.
    *   Anything you would like us to know
*   After the semi-final (2018.09.07), we will ask top teams to submit their code and report and we will evaluate them offline for qualification to final. Teams that refuse to provide code and report will not be qualified, however, we sincerely wish you could share with us. Also, you are welcome to send us the code and doc even though you are not invited, and we will have a serious look at them and give you feedback.

**Preliminary Round Task**

  
Important update:

1\. On July 26th, the preliminary is updated as follows:

    \* An additional problem (Data\_B) is added, the original problem is now referred to as Data\_A

    \* Data\_B and Data\_A are two independent problems, but they are of the same format and only differ numerically. The idea behind adding Data\_B is to prevent from an algorithm that is overfitting to Data\_A

    \* By adding Data_B into preliminary, the submission needs updating too, which is described in "submission of work" below. In short, the updated submission format is:

        <Solution to Data_A>

        #

        <Solution to Data_B>

    \* The evaluation method will be updated and applied to the leaderboard on July 30th. Here is the updated evaluation:  final\_score = 0.5*(score(Data\_A)+score(Data\_B)), in which the evaluation of either Data\_A or Data_B remains the same as before, see details in "evaluation and ranking".  The rules on qualification to semi-final remain unchanged (see "Introduction")

    \* We are sorry for the inconvenience of this update and we will try to bring the best experience to the participants. More about the rationale underlying this update can be found at [https://tianchi.aliyun.com/forum/new_articleDetail.html?spm=5176.8366600.0.0.14b3311fg7jiwI&raceId=231663&postsId=5805](https://tianchi.aliyun.com/forum/new_articleDetail.html?spm=5176.8366600.0.0.14b3311fg7jiwI&raceId=231663&postsId=5805)

### 1 Problem description

On July 26th, an additional problem (described by  Data\_B\_xxxx) is added to the preliminary. The problem described by Data\_A (i.e. the original problem) and the problem described by Data\_B are two independent problems. The resulting update in the evaluation (which is mandatory of course) of the preliminary is presented in "Important update" above.

The data used in this competition is sampled from one of our production clusters, including about 6K machines and 68K instances. Some of the instances have already scheduled to the machines while the rest are unscheduled. 

Requirement: Design an algorithm to generate an optimal deployment plan by scheduling all unscheduled instances to machines, and moving some already scheduled instances to another machine (i.e. rescheduling). Note that both scheduling and rescheduling must respect some constraints which are to be presented in the next section. An optimal deployment plan is a plan in which the number of actually used machines is as less as possible while the resource utilization of each machine cannot be too high. See “Evaluation and Ranking (Preliminary)” for more details.

Before going to the description of constraints, 3 objects need to be defined for participants to better understand the scenario.

**_Instance_**: An instance is the object to be scheduled to a machine. In production, an instance may be a docker container.

**_App_**: Each instance belongs to one and only one App (short for “Application”). An App often includes many instances, and all instances belong to one App have same constraints.

**_Machine_**: A machine is a server in our cluster. An instance is said to be scheduled to a machine if the instance is assigned to the machine.

**1.1Constraint description**

The following constraints should be respected when assigning an instance to a machine.

**_（_****_1_****_）_****_Resource constraint._**Each instance has resource constraint with 3 resource dimensions: CPU, Memory and Disk, in which CPU and Memory are given as time curves. Each value in the curve represents the amount of corresponding resource required by the instance at the time point. The constraint is that, at any timestamp T, on any machine A, for any resource type (CPU, Memory or Disk), the sum of resource required by the instances on this machine cannot be larger than the capacity of corresponding resource of the machine.

**_（_****_2_****_）_****_Special resource constraint._**We have 3 special resource types reflecting the importance of instances: P type, M type, and PM type. They are independent resource constraints. For any given machine, the capacity for P, M and PM resources are specified and none can be violated, i.e. the sum of all instances’ P requirement on the machine cannot be larger the P capacity of the machine. Same for M, and PM.

**_（_****_3_****_）_****_Anti-affinity constraint (due to interference)_**. As there are instances from different Apps running on the same machine, there are potential interference between instances from certain Apps and we need to try not put them on the same machine. Such anti-affinity constraint is described in the form of <App\_A, App\_B, k>, which means that if there is one instance from App\_A on a machine, there could be at most k instances from App\_B (k could be 0) on the same machine. App\_A and App\_B could be the same App id (e.g. <App\_A, App\_A, k>), and this means at most k instances from App_A could be on one machine.

**1.2Data Description**

The constraints explained in section “constraint description” are expressed with 4 files: instance\_deply.csv, app\_resource.csv, machine\_resource.csv and app\_intereference.csv. Every line in the files represents one record, while the meaning of each line is introduced as following:

（1）instance_deploy.csv

![屏幕快照 2018-06-11 下午3.46.48.png](https://work.alibaba-inc.com/aliwork_tfs/g01_alibaba-inc_com/tfscom/TB1BjG3h26TBKNjSZJiXXbKVFXa.tfsprivate.png)  

  

  
  
（2）app_resource.csv  

![屏幕快照 2018-06-11 下午3.47.41.png](https://work.alibaba-inc.com/aliwork_tfs/g01_alibaba-inc_com/tfscom/TB1U.JqiXooBKNjSZFPXXXa2XXa.tfsprivate.png)  

  

  

  

  
  
（3）machine_resource.csv  

![屏幕快照 2018-06-11 下午3.48.34.png](https://work.alibaba-inc.com/aliwork_tfs/g01_alibaba-inc_com/tfscom/TB1kDsyw29TBuNjy1zbXXXpepXa.tfsprivate.png)  

  

  

  

  

  
（4）app_interference.csv

![屏幕快照 2018-06-11 下午3.49.17.png](https://work.alibaba-inc.com/aliwork_tfs/g01_alibaba-inc_com/tfscom/TB1mLIqwVOWBuNjy0FiXXXFxVXa.tfsprivate.png)  

### 1.3 Submission of work

#### 1.3.1 General Submission Format (Preliminary)

Due to the additional problem (Data_B) updated on July 26th, there is a small change in the submission of work. The new submission format is:

        <Solution to Data_A>

        #

        <Solution to Data_B>

Note that the solution to Data\_A must come before the solution to Data\_B.

The format of the solution to either Data\_A or Data\_B remains and can be found below. An example of the updated submission format of Data\_A and Data\_B can be found in submit_sample.csv.

#### 1.3.2 Submission Format of each problem (Preliminary)

For each problem (i.e. the solution to Data\_A or Data\_B), the solution should be an “instance migration plan”, which is consisted of a serial of placement decisions and every single line represents the placement decision of an instance, started from the first line. An instance can be moved multiple times. The format is as follows:

<instance id, target machine id>

<instance id, target machine id>

<instance id, target machine id>

…

Here is an example:

`instance_1, machine_1`

`instance_2, machine_2`

`instance_3, machine_2`

`instance_4, machine_1`

Requirement:

*   All instances should be placed eventually.
*   Invalid instance id or machine id is not allowed.
*   Please save and submit your file as “submit_<YYMMDD-hhmmss>.csv” <YYMMDD-hhmmss> is the time stamp of your submitted plan. We recommend such naming style.

#### 1.3.3 Evaluation and Ranking (Preliminary)

（1）Evaluate by executing the_instance migration plan_, from top line to the last, to produce the final deployment plan (in which every instance should be assigned with a machine). If any placement decision in the plan violates any of the constraints, the evaluation terminates and we would take the current the deployment plan as final to perform ranking.

（2）Ranking criteria of the deployment plan

*   When a deployment plan is generated, we will calculate its total\_cost\_scoreusing the formulation:   
    ![屏幕快照 2018-06-11 下午3.39.40.png](https://work.alibaba-inc.com/aliwork_tfs/g01_alibaba-inc_com/tfscom/TB1EFnEoOOYBuNjSsD4XXbSkFXa.tfsprivate.png)  
    

#### 1.3.4 How to win

（1）The ranking of preliminary is depended only on the**_total\_cost\_score_**of the submitted_instance migration plan._

（2）Top 100 teams in the preliminary will be qualified to semi-final.

（3）Top 10 teams in the semi-final will be required to submit your code, documentation and a brief report. We will have our algorithm experts to evaluate

（4）More details for semi-final will be released later. However, we always prefer:

Algorithms with less complexity and short execution time (say, less than 1 hour, will be specified with the release of semi-final).

Algorithms with reasonable convergence rate.

Algorithms with good creativity, flexibility and robustness.

#### 1.3.5 Recommended Submission Format in Semi-Final (Draft)

_Note: This may be updated when the problem for semi-final gets online._

For the semi-final, we will also ask the participants to submit the instance\_migration\_plan and rank the results. By the end of the semi-final, top 10 teams on the rank will be asked to provide the code, design doc, etc. for off-line evaluation. Teams that do not provide the required materials will not be qualified to the final. The following is the requirement of submission of your code, and we recommend the participants to arrange your project accordingly to make your submission more enjoyable (see example in Note1).

（1）Data file: data/*.csv

This is where you should put the original input of your algorithm. So please leave this directory empty in your submission. If your algorithm has any intermedia file to generate, you can put them here in your code.

（2）Code file: code/*.py (or any programming language)

It is better to make your input directory in relative path instead of absolute path

You should have main.py or main.ipynb so that the result of your algorithm can be produced by executing it directly (or other equivalent main in other languages)

The result of your code should be written to ../submit/ directory

（3）Output file: submit/*.csv

This is where you should put the result.csv

Please generate your result with time, such assubmit\_Ymd\_HMS.csv(e.g.submit\_20180203\_040506.csv)

（4）Randomness in the code:

If there is any random number / variables used in your program, please set them in your submission. If not set, we will run multiple times and use the average as your submission result. If the error is too far from the submitted result, the team will not be qualified. Please name your results by time (example code in Note2.)

Note1: the directory of project

·project

·|--README.md

·|--data

·|--code

·   |\-\- main.py or main.ipynb or <other languages>

·|--submit

·   |\-\- submit\_20180203\_040506.csv

Note2: recommended file name of your submission

·\# java for example

·import datetime

·data.to\_csv(("../submit/submit\_"+datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + ".csv"), header=None, index=False)

### 1.4 You Could Do More …

What is described in this section is NOT part of requirement of the competition.

The idea of us hosting this competition is not only having some winners, we would also like to share a practical case for enthusiasts in related area to have more fun playing with our data. The following ideas are left for you to explore. They do not count as part of the competition, but we are keen to hear your ideas on these scenarios.

（1）Very similar to the formal competition, only that you could design an online algorithm instead of this offline one. The difference is that, in our given scenario, designer has full knowledge of what to schedule and could manipulate on the sequence of instances to schedule. However, for an online algorithm, scheduler can only schedule instance one by one and does not have knowledge on which one among the many type of instances to come next while scheduler cannot deny an instance to be scheduled (not at all or for too long, depending on the assumption you make).

（2）Make the algorithm more robust. As you may have noticed, we use time curves to describe the resource requirement of CPU and Memory. The curves are generated with our estimation model based on the historical data we sampled for every application. In production, it is very likely that the actual resource consumption does not meet the estimation. How can you design robust algorithm that leads to optimal solution despite such error?

（3）Any wild thoughts you would like to play with the data. If you are interested in this, we are sure you would have more fun in the second phase of our competition. Please stay tuned!


# Chinese version of the problem description

![1440-天池-cn.jpg](https://work.alibaba-inc.com/aliwork_tfs/g01_alibaba-inc_com/tfscom/TB129kCw1ySBuNjy1zdXXXPxFXa.tfsprivate.jpg)  

====================================================================================================================================

阿里巴巴全球调度算法大赛
============

在百万级的宿主机规模环境下，资源调度/管理系统显得愈发重要，如何在保证数据中心业务运行性能的同时，提高资源利用率，降低基础设施的成本是我们要考虑的核心问题。

此次赛题来自阿里巴巴生产环境中的一个子场景，并做了相应的简化。优秀的解决方案会对我们解决这个场景以及其它场景下的问题带来极大的启发。我们期待优秀的你和你的团队能够投入进来！

注意：目前的赛题数据主要为了让大家了解复赛的情况。根据我们进一步测试和反馈得到的情况，数据有可能修改。数据会在评测发布的同时（8月20日）最终确定。

在初赛的基础上，增加了以下内容：

在线任务的迁移限制
---------

迁移将更遵循实际，采取多轮并发执行，每一轮并发迁移为多个迁移命令同时执行，一个迁移命令将采取先新建后删除的方式。例如：

    1,inst1,A
    1,inst2,A
    2,inst3,B

为_两阶段_迁移计划。在第一轮中，inst1和inst2迁移到了机器A上，这个是分两个阶段执行的：第一阶段，将同时在机器A上新建inst1、inst2实例，新建成功后再将inst1、inst2在原来所属的机器删除旧实例，并执行下一轮（inst3到机器B）。

若出现迁移失败，则直接退出在线任务调度阶段。

**迁移限制**：每轮迁移没有命令数量限制，但限制轮数小于等于k（暂定k=3）。

离线任务调度
------

初赛仅涉及在线任务的调度，实际场景我们常常需要在离线任务混部才能获得最高的资源利用率。

定义一个离线任务(job_info.x.csv)为：

    离线任务id, cpu占用, mem占用, 实例数, 执行时间, 前驱任务id列表
    

其中

*   执行时间的单位为分钟。对应到在线任务的cpu/mem曲线的98个点，分别代表该在线任务在\[0, 15)、\[15, 30)、...、\[1455, 1470)时刻的资源用量
*   每个离线任务的最早启动时刻，必须大于其所有前驱任务的所有实例执行完成的时刻t
*   在一个完整周期\[0, 1470)内，所有离线任务的所有实例必须全部被执行完成离线任务不允许迁移
    *   对于一个离线任务，只有当其所有的instance都执行完毕，这个离线任务才可以被认为是执行完成

所以最终的提交结果分为两个部分：

*   在线任务阶段：`迁移轮数, 在线任务实例id, 目标宿主机id`
*   离线任务阶段：`离线任务id, 目标宿主id, 启动时刻, 启动实例数量`

一旦开始离线任务的调度，便不允许继续进行在线任务的调度。

评分修改
----

原评分公式中的a，由a=10，修改为

`a=(1+该机器上部署的在线任务inst数量)` 

赛题数据说明
------

复赛有a, b, c, d, e一共5份赛题，每份赛题包含5份数据，其中：

*   app\_interference.csv、app\_resources.csv为5份赛题的公用数据
*   instance\_deploy.x.csv、job\_info.x.csv、machine_resources.x.csv为第x份赛题对应的独有数据

最终提交结果按a,b,c,d,e的顺序拼接，以#分割。

下面是一个例子：

`1, inst1, machine_a
task_1, machine_a, 10, 31
#
1, inst1, machine_b
2, inst2, machine_c
task_1, machine_c, 10, 28` 

复赛排行榜中，选手的分数为五份赛题答案得分的总和。


**初赛赛题描述**

重要更新：

1\. 7月26日，我们对初赛赛制进行了更新，具体的：

    \* 我们新开放了新一个版本的数据（Data\_B），之前的数据称之为Data\_A，作用于初赛

    *Data\_B和Data\_A描述的是两个独立的问题。Data\_B和Data\_A的格式一致，只有数值不同，主要目的是为了防止参赛选手设计针对Data\_A过拟合的算法（经我们测试，通用算法无需修改就可以算出合法的解，但Data\_B有更多优化空间）

    \* 由于添加Data_B导致的提交结果的变化，见下面的“提交结果”部分。简单的说，新的提交方式中，参赛选手还是提交一份答案，其格式为

        <Data_A的解>

        #

        <Data_B的解>

    \* 评分机制会有相应修改，并在7月30日作用于排行榜。修改后的评分公式为：final\_score = 0.5*(score(Data\_A)+score(Data\_B))；针对Data\_A和Data_B的评分机制score函数，与更新前保持一致，具体见“执行与评分（初赛）”部分；进入复赛的条件保持不变（见“赛制介绍”）

    \* 对于此次更新给各位选手带来的不便我们感到十分抱歉，但会尽力为选手提供最好的参赛体验。更多关于赛题更新的说明可以参考：[https://tianchi.aliyun.com/forum/new_articleDetail.html?spm=5176.8366600.0.0.52f3311fT3qWk6&raceId=231663&postsId=5802](https://tianchi.aliyun.com/forum/new_articleDetail.html?spm=5176.8366600.0.0.52f3311fT3qWk6&raceId=231663&postsId=5802)

2\. 赛题在6月11日有一次更新（赛题描述和数据），6月7日上线的赛题已经彻底下线，请所有参赛同学以你当前看到的版本赛题为准，7月初开始的评测工作将以目前版本为准。由此给各位选手带来的不便，深感歉意。但我们相信，目前这个版本的赛题无论对于初学者还是资深的研究者，都是很有趣的。

1赛题描述
-----

7月26日添加了一份新的数据（Data\_B\_xxxx），下面的赛题描述同时适用于之前版本的数据（Data\_A\_xxxx）和更新的数据（Data\_B\_xxxx），基于二者共同作用的评分机制见上面的“重要更新”部分。注意，Data\_A和Data\_B描述的是两个独立的问题，只是格式一样。

共约6K台宿主机（machine），包含了若干种型号，约68K个任务实例（instance），其中一部分已经部署在宿主机上，还有一部分没有被部署。

要求： 设计调度算法，在满足要求约束的前提下，通过将全部未被调度的任务实例调度到宿主机上以及腾挪部分已经部署的实例的方式，得到最优的部署方案。最优部署方案指实际使用宿主机数目尽可能少，且宿主机负荷不能过高。请参考“执行与评分（初赛）”部分来获得更多关于最优部署方案的说明。

在解释数据格式、约束条件之前，为防止概念混淆，先给出几个定义，全文出现的概念以此定义为准。

实例（instance）：一个实例是可以被调度到一个机器上的对象，在实际生产中，一个实例可以是一个docker容器

应用分组（App）:一个应用分组包括很多实例（instance）。属于同一个App下的所有实例，具备相同的约束条件。一个实例能且只能属于一个应用分组

机器（Machine）：机器是集群中的服务器，一个实例被可以被调度到一个机器上

###  1.1约束描述

任务实例到宿主机的分配，需要满足下列约束：

·每个实例都标明了CPU、memory、disk此3个维度的资源需求，其中CPU、memory以分时占用曲线的形式给出，在任意时刻，任意一个宿主机A上，所有部署在宿主机A上的实例的任意资源都不能超过宿主机A的该资源容量

·另外还有P、M、PM三类资源，定义了应用实例的重要程度，任意一台宿主机上的部署数目不能超过该类型宿主机能够容纳的重要应用数目上限

·混部集群时刻处于复杂的干扰环境中，所以我们需要满足一些规避干扰约束，一条规避干扰约束被描述为<APP\_A, APP\_B, k>，代表若一台宿主机上存在APP_A类型的实例，则最多能部署k个APP_B类型的实例。注意，k可能为0。APP_A和APP_B也可能代表同一个APP（e.g. <APP\_A, APP\_A, k>），代表同一台机器上最多可以部署的该APP的实例的数目

### 1.2数据描述

问题一共包含四份数据表：instance\_deploy.csv, app\_resources.csv, machine\_resources.csv, app\_interference.csv

·instance_deploy.csv

o实例id

o实例所属应用

o实例所属宿主机:

§注：当前未分配的实例，实例所属宿主机列为空

·app_resources.csv

o应用id

ocpu分时占用曲线（每个点由< | >隔开）

omem分时占用曲线（每个点由< | >隔开）

odisk申请量（标量）

oP

oM

oPM

·machine_resources.csv

o宿主机id

ocpu规格

omem规格

odisk规格

oP上限

oM上限

oPM上限

·app_interference.csv

o应用id1

o应用id2

o最大部署量

### 1.3结果提交

#### 1.3.1 提交格式（初赛）

由于7月26日更新了Data_B（具体见本文顶部的“重要更新”），新的提交格式为：

        <Data_A的解>

        #

        <Data_B的解>

注意把Data_A的解放在前面。

单份数据的解（i.e. Data\_A的解或者Data\_B的解）的具体格式，以及单份数据的评分方式见下面的描述。具体的例子可以参考我们的submit_sample.csv

#### 1.3.2 单份数据的解的格式（初赛）

单份数据的解（i.e. Data\_A的解或者Data\_B的解）是一系列对应用实例进行分配或迁移的决策动作，顺序由第一行开始，到最后一行，格式为： 

<实例ID>, <目标宿主机ID>

<实例ID>, <目标宿主机ID>

<实例ID>, <目标宿主机ID>

<实例ID>, <目标宿主机ID>

... ...

·**要求**

o最终所有实例都要部署到宿主机中

o不能出现无效的实例id或宿主机id

o请保存为submit_<YYMMDD_hhmmss>.csv。<YYMMDD_hhmmss>是结果生成时的时间戳，这是我们建议的结果命名方式

例子，

`<``实例的UID>, <目标宿主机的UID>`

`<``实例的UID>, <目标宿主机的UID>`

`<``实例的UID>, <目标宿主机的UID>`

`<``实例的UID>, <目标宿主机的UID>`

`... ...`

**1.3.3 执行与评分（初赛）**

·**可执行性**

o决策动作会按文件从上到下的顺序串行执行，若遇到不可执行的操作，评价程序会中断，并直接开始评价当前状态的得分

·**评分**

o根据执行完提交结果的最终状态，计算成本分数**_total\_cost\_score_**

**_![17_39_17__08_29_2018.jpg](https://work.alibaba-inc.com/aliwork_tfs/g01_alibaba-inc_com/tfscom/TB19FfPunmWBKNjSZFBXXXxUFXa.tfsprivate.jpg)  
_**

#### 1.3.4对方案的评测

·初赛成绩以提交结果的评分为准

·复赛阶段会要求排名前10的队伍提交代码与文档，进行方案评测。同时参考提交结果的评分及方案，进入决赛，角逐冠军

·方案评测的细节，会于复赛前公布，基本会遵循以下原则：

o求解时间短(例如1小时以内，具体要求复赛确定)

o鼓励策略性模型(可以快速输出部分决策，但效果是前提)

o鼓励创新性

o鼓励灵活性

### 1.4你可以用这份数据设计其它算法

下面的要求不是比赛的一部分，但同样是数据中心资源调度关心的目标。爱好者可以根据这份数据设计以下面需求之一为目的的调度算法。我们十分欢迎您与我们交流您的想法！

1.同样是上述数据和问题，设计在线调度算法。所谓在线调度算法，是待调度的任务顺序地被调度器调度，而调度器不知道待调度任务序列中靠后的任务的信息。实践中，在线算法只能接近，但很难达到离线算法的效果。

2.让算法更robustness。实际环境中，大量数据为建模预估产生的模型化数据，例如赛题中的cpu, mem分时占用曲线，如何在预估数据存在偏差的前提进行问题求解，或者如何在已知决策模型的前提下调整预估方法，也是充满挑战的问题。

3.其它任何你能想到的使用这份数据可以设计的问题和算法。如果你对这个有兴趣，我们相信你会对我们第二阶段的比赛更加有兴趣，请保持关注并一定参加我们的正式比赛！