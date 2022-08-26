# 对比算法 NSGA-2
# 初始化种群
# 评价
# 非支配排序
# 选择、交叉、变异生产子代种群(gen+1)
# 父代子代合并
# 非支配排序
# 拥挤度计算
# 选择并组成父代
# 达到终止条件
import copy
import math
import random

import trans
from trans import truck_parameter


def station(n_case):
    n_sta = [2, 3, 6, 8, 10, 40, 30, 60]
    return n_sta[n_case]


# GA求解alb
def NS_GA(pop_ind, temp, CT, n_sta, data, n_case, total_m, pre_op, CM):
    '''
    :param CM:
    :param pre_op:
    :param total_m:
    :param n_case:
    :param data:
    :return:
    '''

    n_data = len(data)
    # 记录最优解的三个维度
    set_result = []
    for i in range(3):
        set_result.append([])

    min_station_op = []
    for i in range(n_sta):  # 建立工作站的工序存储与工序结束时间二维数据结构 num_s*2
        min_station_op.append([])
        for j in range(2):
            min_station_op[i].append([])

    # 种群大小
    popsize = 100
    # 初始化种群
    # 初始化装配线排列
    # 工作站数目

    n_sta = station(n_case)
    sum_op = len(data)
    cars = truck_parameter()
    # 车辆数目取值范围
    sum_car_min = math.ceil(total_m / cars[3][0])
    sum_car_max = sum_op

    if temp == 1:
        ind = []
        for i in range(popsize):
            # 新增一个个体
            ind.append([])
            # 生成个体
            for j in range(sum_op):
                ind[i].append(j)
        for i in range(popsize):
            # 每个个体打乱50次
            random.shuffle(ind[i])
        # 添加决策变量车辆数
        in_ind = []
        for i in range(2):
            in_ind.append([])
        for i in range(popsize):
            in_ind[0].append(ind[i])
            cars = random.randint(sum_car_min, sum_car_max)
            in_ind[1].append(cars)
    else:  # 非初代
        for k in range(30):  # 种群迭代次数

            alb_generate_pop(pop_ind)
            # 采用交叉变异产生新个体
            in_ind = copy.deepcopy(pop_ind)
            # 交叉-ox顺序操作 概率0.4
            # 变异-单点变异 概率0.1
            # 选择-轮盘赌选择
            for i in range(popsize):

                # 清空
                for k in range(n_data):
                    in_ind[0][i][k] = -1
                n_ind1, n_ind2 = 0, 0
                while n_ind1 == n_ind2:
                    n_ind1 = random.randint(0, popsize-1)
                    n_ind2 = random.randint(0, popsize-1)
                # 是否发生交叉、变异
                p_change = random.randint(0, 10)
                # 交叉
                if 0 <= p_change <= 3:
                    n_pos1, n_pos2 = 0, 0
                    while n_pos1 == n_pos2:
                        n_pos1 = random.randint(0, n_data - 1)
                        n_pos2 = random.randint(0, n_data - 1)
                    #     调整位置前后关系
                    if n_pos1 < n_pos2:
                        pass
                    else:
                        n_temp = n_pos1
                        n_pos1 = n_pos2
                        n_pos2 = n_temp
                    # 片段包含的元素
                    s_num = []
                    for j in range(n_pos1, n_pos2 + 1):
                        s_num.append(pop_ind[0][n_ind1][j])
                    #   将片段遗传给子代
                    for j in range(n_pos1, n_pos2 + 1):
                        in_ind[0][i][j] = pop_ind[0][n_ind1][j]
                    #   补充两段剩余元素
                    n_p = 0
                    for j in range(0, n_data):
                        try:
                            if not pop_ind[0][n_ind2][j] in s_num:
                                # 该位置没有被补充
                                if in_ind[0][i][n_p] == -1:
                                    # 传递给子代
                                    in_ind[0][i][n_p] = pop_ind[0][n_ind2][j]
                                    n_p += 1
                                else:
                                    n_p = n_pos2 + 1
                                    # 传递给子代
                                    in_ind[0][i][n_p] = pop_ind[0][n_ind2][j]
                                    n_p += 1
                        except IndexError:
                            pass
                    # print('交叉')
                # 变异
                elif 4 <= p_change <= 4:
                    n_pos1, n_pos2 = 0, 0
                    while n_pos1 == n_pos2:
                        n_pos1 = random.randint(0, n_data - 1)
                        n_pos2 = random.randint(0, n_data - 1)
                    op1 = pop_ind[0][n_ind1][n_pos1]
                    pop_ind[0][n_ind1][n_pos1] = pop_ind[0][n_ind1][n_pos2]
                    pop_ind[0][n_ind1][n_pos2] = op1
                    # 传递给子代
                    in_ind[0][i] = copy.deepcopy(pop_ind[0][n_ind1])
                    # print("变异")
                # 直接给, 装配阶段适应值不变
                else:
                    try:
                        in_ind[0][i] = copy.deepcopy(pop_ind[0][n_ind1])
                        in_ind[1][i] = copy.deepcopy(pop_ind[1][n_ind1])
                    except IndexError:
                        pass
                    # print('直接继承')
        #         车辆数编码传递给子代
                pop_ind[1][i] = copy.deepcopy(pop_ind[1][n_ind1])
                # print(str(i)+"个体产生")
                # print(in_ind)
            # print(in_ind)
            # print(pop_ind)

# 创建装配排序种群
    pop_sta = []
    for i in range(2):
        pop_sta.append([])
    # 解码、评价
    for i in range(100):
        # 建立工作站的工序存储与工序结束时间二维数据结构 num_s*2
        station_op = []
        for j in range(n_sta):
            station_op.append([])
            for k in range(2):
                station_op[j].append([])

        # 构建装配站对象
        station_ind = []
        # 维度1 工作站 维度2 工作站完工时间、元素
        for j in range(n_sta):
            station_ind.append([])
            for k in range(2):
                station_ind[j].append([])
                if k == 0:
                    # 初始化工作站完工时间
                    station_ind[j][0] = 0
        # 装配线平衡解码
        code = copy.deepcopy(in_ind[0][i])
        state = []
        # 工序状态
        for t in range(sum_op):
            state.append(0)
        # 已分配的工件数目
        j = 0
        # 初始化当前工作站
        curr_sta = 0
        while j != sum_op:
            # 判断前序
            for k in range(sum_op):
                # 能否被分配状态
                assign = 0
                # 已被分配
                if state[code[k]] == -1:
                    continue
                else:
                    # 检查前序状态
                    if len(pre_op[code[k]]) == 0:
                        assign = 1
                    else:
                        for v in range(len(pre_op[code[k]])):
                            # 前序没有被分配  ** pre_op装的是1起始的编码 所以-1
                            if state[pre_op[code[k]][v] - 1] == 0:
                                break
                            else:  # 前序全部被分配
                                if v == len(pre_op[code[k]]) - 1:
                                    assign = 1
                    if assign == 1:
                        # 判断分配至哪个工作站
                        try:
                            if station_ind[curr_sta][0] + data[code[k]][1] <= CT:
                                # 更细工序状态(已经被分配)
                                state[code[k]] = -1
                                # 更新时间
                                station_ind[curr_sta][0] += data[code[k]][1]
                                # 添加元素
                                station_ind[curr_sta][1].append(code[k])
                                # 已装配工序+1
                                j += 1
                            elif curr_sta != n_sta - 1:  # 当前装配站装不下, 更新当前装配站
                                curr_sta += 1
                            else:
                                # 更细工序状态(已经被分配)
                                state[code[k]] = -1
                                # 更新时间
                                station_ind[curr_sta][0] += data[code[k]][1]
                                # 添加元素
                                station_ind[curr_sta][1].append(code[k])
                                # 已装配工序+1
                                j += 1
                        except IndexError:
                            pass

        # 计算节拍
        set_ct = []
        for j in range(n_sta):
            set_ct.append(station_ind[j][0])
        sta_max_ct = max(set_ct)
        pop_sta[0].append(sta_max_ct)
        pop_sta[1].append(station_ind)
        # 下面是粘贴关键关节对比实验2的装配优化部分：
        # --------------------
        try:
            for j in range(n_sta):
                station_op[j][0] = copy.deepcopy(station_ind[j][1])
        except IndexError:
            pass
        station_time = sta_max_ct
        # ------------------
        this_ct = station_time
        # 第一个个体为首个最优节拍
        if i == 0:
            min_ct = this_ct
        # 节拍被更新或者相等
        if this_ct <= min_ct:
            # 节拍被更新
            if this_ct < min_ct or i == 0:
                # 最优解集刷新
                set_result[0] = []
                set_result[1] = []

                min_ct = this_ct
                min_station_op = copy.deepcopy(station_op)
                set_result[0].append(min_ct)
                set_result[1].append(min_station_op)

            # 节拍相等
            elif this_ct == set_result[0][0]:
                for j in range(len(set_result[1])):
                    # 查找已有的每一个排序
                    if station_op == set_result[1][j]:
                        break
                    else:
                        pass
                    # 查找到最后没有重复排序
                    if j == (len(set_result[1]) - 1):
                        min_ct = this_ct
                        min_station_op = station_op
                        set_result[0].append(min_ct)
                        set_result[1].append(min_station_op)
    list_a = []
    len_set = len(set_result[0])
    for i in range(len_set):
        set_result[2].append([])
    # 将工作站的排序转化为一个排序
    for i in range(len_set):
        for j in range(n_sta):
            for k in range(len(set_result[1][i][j][0])):
                op = set_result[1][i][j][0][k]
                set_result[2][i].append(op)

    return set_result, min_ct, in_ind
