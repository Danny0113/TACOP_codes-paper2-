# 装配线平衡(随机方式)
import copy
import random

import gantt
from other import data_prep_alb


# 创建随机排序（首次迭代时）
from trans import insert, choose_action, order_choose_action, Reverse_order, swap, interchange, refresh_p, generate_pop, \
    ga_cross


def ini_list(data):
    n_op = len(data)
    list_alb = []
    for i in range(n_op):
        list_alb.append(i)  # 顺序排序
    return list_alb


# 评价排序-返回节拍和装配排序
def calculate_alb(list_alb, num_station, ct, pre_op, data):

    copy_list = copy.deepcopy(list_alb)  # 传入序列
    n_op = len(data)  # 工序长度
    state_op = []  # 初始化工序状态
    t_sta = []  # 工作站时间初始化
    n_sta = num_station  # 工作站数目
    op_sta = []
    for i in range(n_sta):
        t_sta.append(0)  # 工作站时间初始化
        op_sta.append([])  # 工作站数目初始化
    for i in range(n_op):  # 未被安排
        state_op.append(1)
    n_curr_sta = 0

    while copy_list:  # 存在未被安排工序
        assign, index = 0, 0  # 初始化
        t_op, op = 0, 0  # 初始化
        n_copy_list = len(copy_list)
        for i in range(n_copy_list):  # 遍历无前序约束的工序 指导找到满足节拍约束的工序
            index = i
            pre_limit = 1  # 初始化前序约束标志
            op = copy_list[i]  # 待判断工序
            length_op_pre = len(pre_op[op])
            if length_op_pre >= 1:
                for j in range(length_op_pre):  # 判断前序
                    p_pre = pre_op[op][j] - 1
                    if state_op[p_pre] == 0:
                        pre_limit = 0
                    else:
                        pre_limit = 1
                        break  # 存在前序约束
            else:
                pre_limit = 0
            t_op = data[op][1]  # 工序的装配时间
            if pre_limit == 0:  # 前序约束
                if n_curr_sta < n_sta - 1:  # 非最后一台工作站
                    if t_sta[n_curr_sta] + t_op <= ct:  # 满足装配节拍约束
                        n_curr_sta = n_curr_sta  # 当前工作站增加新工序
                        assign = 1
                        break

                else:  # 最后一台工作站
                    n_curr_sta = n_curr_sta
                    assign = 1
                    break
        if assign == 0 and index == n_copy_list - 1:  # 所有工序均不满足节拍约束
            n_curr_sta = n_curr_sta + 1  # 开辟新工作站
            assign = 0

        if assign == 1:  # 满足前序+节拍约束-安排工序
            t_sta[n_curr_sta] += t_op  # 工作站时间递增
            op_sta[n_curr_sta].append(op)  # 工作站工序添加
            del copy_list[index]  # 从序列中删除该工序
            state_op[op] = 0  # 工序状态变更

    new_ct = max(t_sta)

    return new_ct, op_sta  # 返回节拍、装配排序


# 获取更多装配解
def get_s_alb_res(best_alb_list, best_alb_ct, list_best, n_sta, pre_op, data):
    s_alb_res = []
    for i in range(3):
        s_alb_res.append([])
    s_alb_res[0].append(best_alb_ct)
    s_alb_res[1].append(best_alb_list)
    s_alb_res[2].append(list_best)
    for i in range(50):
        list_best = s_alb_res[2][random.randint(0, len(s_alb_res[2]) - 1)]  # 从最优排序中随机选一个
        copy_list = copy.deepcopy(list_best)
        # copy_list = interchange(copy_list)
        copy_list = Reverse_order(copy_list)  # 为了获取多样的优质装配排序-用局部逆序
        new_ct, op_sta = calculate_alb(copy_list, n_sta, best_alb_ct, pre_op, data)  # CT为最优节拍
        if new_ct == best_alb_ct:
            print("拓展了")
            s_alb_res[0].append(best_alb_ct)
            s_alb_res[1].append(op_sta)
            s_alb_res[2].append(copy_list)
    return s_alb_res


# 学习型vns装配线平衡方式
def ga_alb(lvns, set_result, input_CT, data, cm, num_station, pre_op):
    refresh_flag = 0  # 初始化
    best_sta_order = 0
    best_list = 0
    best_ct = 0

    best_ct_lim = input_CT  # 初始化节拍

    if input_CT == 1.5 * cm:  # 当首轮迭代时
        list_alb = ini_list(data)  # 产生随机排序
        set_result = []  # 初始化装配解集
        for i in range(3):
            set_result.append([])
    else:  # 非首轮迭代
        n_res = len(set_result[0])
        list_alb = set_result[2][random.randint(0, n_res-1)]  # 从现有优质装配排序中随机选择一个
        pass  # 利用输入的集合

    n_pop = 20  # 种群大小
    list_prod = list_alb  # 待处理的排序
    pop_sta = []
    for i in range(n_pop):
        pop_sta.append([])
    pop, pop_value = generate_pop(list_prod, n_pop)
    for j in range(n_pop):
        ct_value, op_sta_order = calculate_alb(pop[j], num_station, best_ct_lim - 1, pre_op, data)  # 评价此序列节拍
        pop_value[j] = ct_value  # 节拍
        pop_sta[j] = op_sta_order  # 装配站

    pop_best_ct = min(pop_value)
    pop_min_index = pop_value.index(pop_best_ct)  # 种群内最短路径个体的系数
    pop_best_sta_order = pop_sta[pop_min_index]
    pop_best_list = pop[pop_min_index]
    for k in range(20):  # 种群迭代次数

        new_pop = []

        for j in range(n_pop):  # 交叉\变异生成新种群
            ind1, ind2 = 0, 0
            while ind1 == ind2:
                ind1 = random.randint(0, n_pop - 1)
                ind2 = random.randint(0, n_pop - 1)
            p_value = random.randint(1, 10)
            if 1 <= p_value <= 3:
                new_ind = ga_cross(pop, ind1, ind2)  # 交叉
            else:
                new_ind = insert(pop[ind1])  # 变异
            new_pop.append(new_ind)

        for j in range(n_pop):  # 评价新种群
            ct_value, op_sta_order = calculate_alb(pop[j], num_station, best_ct_lim - 1, pre_op, data)  # 评价此序列节拍
            pop_value[j] = ct_value  # 节拍
            pop_sta[j] = op_sta_order  # 装配站

        min_ct = min(pop_value)  # 种群内最短路径
        min_index = pop_value.index(min_ct)  # 种群内最短路径个体的系数
        min_list = pop[min_index]  # 该个体的序列

        if min_ct < best_ct_lim:
            best_ct = min_ct
            best_sta_order = pop_sta[min_index]
            best_list = min_list
            best_ct_lim = best_ct
            refresh_flag = 1
    if refresh_flag == 1:
        s_alb_res = get_s_alb_res(best_sta_order, best_ct, best_list, num_station, pre_op, data)  # 将最优解排序处理为多种排序方式-该过程也可能是np问题
    else:  # 20次迭代没有更新
        s_alb_res = set_result
        best_ct = input_CT
    return s_alb_res, best_ct


# 学习型vns装配线平衡方式
def vns_alb(a, b, lvns, set_result, input_CT, data, cm, num_station, pre_op):
    ini_ct = input_CT  # 初始化节拍
    if input_CT == 1.5 * cm:  # 当首轮迭代时
        list_alb = ini_list(data)  # 产生随机排序
        set_result = []  # 初始化装配解集
        for i in range(3):
            set_result.append([])
    else:  # 非首轮迭代
        n_res = len(set_result[0])
        list_alb = set_result[2][random.randint(0, n_res-1)]  # 从现有优质装配排序中随机选择一个
        pass  # 利用输入的集合
    new_ct, new_op_sta = calculate_alb(list_alb, num_station, ini_ct, pre_op, data)  # 解码、评价此序列节拍
    list_best = list_alb
    best_alb_ct = new_ct  # 初始化最优节拍
    best_alb_list = new_op_sta  # 最优装配排序
    n_length = len(best_alb_list)
    s_p_a = []
    new_list_alb = []  # 初始化
    for j in range(4):  # 初始化动作的概率值
        s_p_a.append(0.25)

    for j in range(n_length * 200):  # 路径优化迭代次数
        if lvns == 1:  # 通过概率选择邻域结构
            n_action = choose_action(s_p_a)
        else:  # 标准vns、按顺序执行领域结构
            n_action = order_choose_action()
        old_list_prod = copy.deepcopy(list_best)  # 旧解  - 未解码的序列
        if n_action == 0:  # 根据动作选择函数选择动作
            new_list_alb = Reverse_order(old_list_prod)  # 局部逆序算子-新解
        elif n_action == 1:
            new_list_alb = swap(old_list_prod)  # 交换算子-新解
        elif n_action == 2:
            new_list_alb = insert(old_list_prod)  # 插入算子-新解
        elif n_action == 3:
            new_list_alb = interchange(old_list_prod)  # 相邻交换算子-新解
        new_ct, new_op_sta = calculate_alb(new_list_alb, num_station, best_alb_ct - 1, pre_op, data)  # 解码、评价此序列节拍
        if new_ct < best_alb_ct:  # 新解更好
            best_alb_ct = new_ct  # 节拍
            best_alb_list = new_op_sta  # 装配排序
            list_best = old_list_prod  # 旧解  - 未解码的序列
            flag = 1  # 给与奖励
        else:
            flag = 0  # 给与惩罚
        if lvns == 1:  # 启用学习型vns更新
            s_p_a = refresh_p(a, b, n_action, flag, s_p_a)  # 更新动作执行后的概率
        else:
            pass
    if best_alb_ct < input_CT:
        refresh_flag = 1
    else:
        refresh_flag = 0

    if refresh_flag == 1:
        s_alb_res = get_s_alb_res(best_alb_list, best_alb_ct, list_best, num_station, pre_op, data)  # 将最优解排序处理为多种排序方式-该过程也可能是np问题
    else:  # 20次迭代没有更新
        s_alb_res = set_result
        best_alb_ct = input_CT

    return s_alb_res, best_alb_ct


# 随机型方法求解-alb装配线平衡方式
def alb_3(set_result, input_CT, data, cm, num_s, pre_op):
    '''
    :param data:
    :param cm:
    :param num_s:
    :param pre_op:
    :return: 每个工作站的工序排列、每个工序的开始装配时间
    '''

    iter_ct = 1
    min_ct = input_CT
    min_station_op = []
    for i in range(num_s):  # 建立工作站的工序存储与工序结束时间二维数据结构 num_s*2
        min_station_op.append([])
        for j in range(2):
            min_station_op[i].append([])
    # 记录最优解的三个维度
    if input_CT == 1.5 * cm:  # 初次迭代创建装配解的集合
        set_result = []
        for i in range(3):
            set_result.append([])
    n_NOchange = 0
    while iter_ct < 200:  # 重复迭代次数
        # print(min_ct)
        op_state = []  # 工件状态 0-没有分配 1-已被分配
        for i in range(len(data)):
            op_state.append(0)
        iter_ct += 1
        ct = min_ct - 1
        # 分配规则
        # 满足节拍和前序和开工时间 > 等待时间（i工件与第一个抵达的工件的时间差值）
        station_time = []
        for i in range(num_s):  # 给工作站赋予时间 0-ct
            station_time.append(0)
        station_op = []
        for i in range(num_s):  # 建立工作站的工序存储与工序结束时间二维数据结构 num_s*2
            station_op.append([])
            for j in range(2):
                station_op[i].append([])
        for n in range(num_s):  # 基于工作站递增
            if n != num_s - 1:
                no_suit_op = 0
                while station_time[n] <= ct and no_suit_op == 0:  # 当前装配站的结束时间<节拍 并且 有合适的工序安排
                    level_1 = []
                    for i in range(len(op_state)):  # 1遍历工序 若工序未被安排
                        if op_state[i] == 0:  # 工序没有被安排
                            if pre_op[i]:  # 1.1.1存在前序情况
                                num = 0
                                for j in range(len(pre_op[i])):  # 1.1.1.1判断i工序的前序状态
                                    if op_state[pre_op[i][j] - 1] == 1:  # 如果i工序的前序分配了
                                        num += 1
                                    else:
                                        break
                                if num == len(pre_op[i]) and data[i][1] + station_time[n] <= ct:
                                    # 如果i工序的前序分配了
                                    level_1.append(i + 1)
                            elif not pre_op[i]:  # 1.1.2 不存在前序情况
                                if data[i][1] + station_time[n] <= ct:  # 满足节拍约束
                                    level_1.append(i + 1)
                                else:
                                    pass
                    # 选择工件更新装配线状态
                    if level_1:
                        num = random.randint(1, len(level_1))  # 在待选集合中选择一个工序安排
                        station_op[n][0].append(level_1[num - 1])  # 添加工序到装配站
                        station_op[n][1].append(station_time[n] + data[level_1[num - 1] - 1][1])
                        station_time[n] = station_time[n] + data[level_1[num - 1] - 1][1]
                        op_state[level_1[num - 1] - 1] = 1  # 该工件已分配位置
                    else:
                        no_suit_op = 1  # 没有工序可分配了
            # 是最后一个工作站
            elif n == num_s - 1:
                op = 1  # 存在工序
                while op == 1:  # 存在工序为完工
                    level_1 = []
                    for i in range(len(op_state)):  # 1遍历工序 若工序未被安排
                        if op_state[i] == 0:  # 工序没有被安排
                            if pre_op[i]:  # 1.1.1存在前序情况
                                num = 0
                                for j in range(len(pre_op[i])):  # 1.1.1.1判断i工序的前序状态
                                    if op_state[pre_op[i][j] - 1] == 1:  # 如果i工序的前序分配了
                                        num += 1
                                    else:
                                        break
                                if num == len(pre_op[i]):  # 如果i工序的前序分配了
                                    level_1.append(i + 1)
                            elif not pre_op[i]:  # 1.1.2 不存在前序情况
                                level_1.append(i + 1)
                    # 选择工件更新装配线状态
                    if level_1:
                        num = random.randint(1, len(level_1))  # 在待选集合中选择一个工序安排
                        station_op[n][0].append(level_1[num - 1])  # 添加工序到装配站
                        station_op[n][1].append(station_time[n] + data[level_1[num - 1] - 1][1])
                        station_time[n] = station_time[n] + data[level_1[num - 1] - 1][1]
                        op_state[level_1[num - 1] - 1] = 1  # 该工件已分配位置
                    else:  # 没有工序了
                        op = 0
        this_ct = max(station_time)
        if station_op and this_ct <= min_ct:
            if this_ct < min_ct:  # 最优解集刷新
                set_result[0] = []
                set_result[1] = []
                min_ct = this_ct
                min_station_op = station_op
                set_result[0].append(min_ct)
                set_result[1].append(min_station_op)
            elif this_ct == set_result[0][0]:
                for i in range(len(set_result[1])):
                    # 查找已有的每一个排序
                    if station_op == set_result[1][i]:
                        break
                    else:
                        pass
                    # 查找到最后没有重复排序
                    if i == (len(set_result[1])-1):
                        min_ct = this_ct
                        min_station_op = station_op
                        set_result[0].append(min_ct)
                        set_result[1].append(min_station_op)
        else:  # 本次迭代没有被更新
            pass
    len_set = len(set_result[0])
    set_result[2] = []
    for i in range(len_set):
        set_result[2].append([])
    for i in range(len_set):
        for j in range(num_s):
            for k in range(len(set_result[1][i][j][0])):
                op = set_result[1][i][j][0][k]
                set_result[2][i].append(op)
    # gantt.get_gantt(min_station_op, num_s, data, min_ct)  # 画出装配方案的 gantt
    return set_result, min_ct


#   改进的装配线平衡算法
def alb_2(ar_time, data, cm, num_s, pre_op):

    sum_op = len(data)
    iter_ct = 1
    min_ct = cm*num_s
    while iter_ct < 2:  # 装配线平衡的优化次数
        # 找到能够被安排的工序, 将其作为参考计算其它工件的抵达时间
        first_op = []
        for i in range(sum_op):
            if not pre_op[i]:
                first_op.append(i)  # 工序：第一个可以被装配的工序
        sum_first_op = len(first_op)  # 数量：第一个可以被装配的工序
        min_at = ar_time[first_op[0]]  # 时间：第一个可以被装配工序中 第一个工序
        min_at_op = first_op[0]  # 工序：第一个可以被装配工序中 第一个工序
        for i in range(sum_first_op):  # 找到第一个能被装配工序中最快抵达的工序、抵达抵达时间
            if min_at > ar_time[first_op[i]]:
                min_at = ar_time[first_op[i]]  # 抵达时间
                min_at_op = first_op[i]  # 抵达的工序
        wt_time = data_prep_alb(min_at_op, ar_time, data)  # 其它工序相对与第一个抵达工序还需要多久抵达
        op_state = []  # 工件状态 0-没有分配 1-已被分配
        for i in range(len(ar_time)):
            op_state.append(0)
        for i in range(len(op_state)):
            op_state[i] = 0
        # 更新节拍约束
        iter_ct += 1
        if iter_ct == 1:
            ct = min_ct
        else:
            ct = min_ct - 1
        # 分配规则
        # 1.满足节拍和前序和 开工时间 > 等待时间（i工件与第一个抵达的工件的时间差值）
        # 装配环节的时间轴
        station_time = []
        for i in range(num_s):  # 给工作站赋予时间 0-ct
            station_time.append(0)
        # 建立工作站的工序存储与工序结束时间二维数据结构 num_s*2
        station_op = []
        for i in range(num_s):
            station_op.append([])
            for j in range(2):
                station_op[i].append([])
        # 依次装满工作站
        for n in range(num_s):
            # 非最后工作站
            if n != num_s - 1:
                no_suit_op = 0
                # 当前装配站的结束时间 < 节拍 并且 有合适的工序安排
                while station_time[n] < ct and no_suit_op == 0:
                    level_1 = []
                    # 满足基本约束
                    for i in range(len(op_state)):  # 1遍历工序 若工序未被安排
                        if op_state[i] == 0:  # 工序没有被安排
                            if wt_time[i] < (n + 1) * ct:  # 1.1 在当前站内，满足抵达时间（工件已抵达）
                                if pre_op[i]:  # 1.1.1存在前序情况
                                    num = 0
                                    for j in range(len(pre_op[i])):  # 1.1.1.1判断i工序的前序状态
                                        # 有*个前序被分配
                                        if op_state[pre_op[i][j] - 1] == 1:
                                            num += 1
                                        else:
                                            break
                                    # 前序全被分配、完成时间不超出CT
                                    if num == len(pre_op[i]) and data[i][1] + station_time[n] <= ct:
                                        level_1.append(i + 1)
                                elif not pre_op[i]:  # 1.1.2 不存在前序情况
                                    # 需要考虑等待时间
                                    if wt_time[i] - station_time[n] - n*ct > 0:
                                        other_t = wt_time[i] - station_time[n] - n*ct
                                    else:
                                        other_t = 0
                                    if data[i][1] + station_time[n] + other_t <= ct:  # 满足节拍约束
                                        level_1.append(i + 1)
                                    else:
                                        pass
                    # 选择工件更新装配线状态
                    if level_1:
                        num = random.randint(1, len(level_1))  # 在待选集合中选择一个工序安排
                        op = level_1[num - 1]
                        station_op[n][0].append(op)  # 添加工序到装配站
                        # 需要考虑等待时间
                        if wt_time[op-1] - station_time[n] - n * ct > 0:
                            other_t = wt_time[op-1] - station_time[n] - n * ct
                        else:
                            other_t = 0
                        # add工序在工作站的完工时间、工作站的完工时间
                        station_op[n][1].append(station_time[n] + data[op - 1][1] + other_t)
                        station_time[n] = station_time[n] + data[level_1[num - 1] - 1][1] + other_t
                        op_state[level_1[num - 1] - 1] = 1  # 该工件已分配位置
                    else:
                        no_suit_op = 1  # 没有工序可分配了
            elif n == num_s - 1:  # 是最后一个工作站
                no_suit_op = 0
                while no_suit_op == 0:  # 有合适的工序安排
                    level_1 = []
                    # 1遍历工序 若工序未被安排
                    for i in range(len(op_state)):
                        # 工序没有被安排
                        if op_state[i] == 0:
                            # 存在前序情况
                            if pre_op[i]:
                                num = 0
                                # 判断i工序的前序状态
                                for j in range(len(pre_op[i])):
                                    # 如果i工序的前序被分配
                                    if op_state[pre_op[i][j] - 1] == 1:
                                        num += 1
                                    else:
                                        break
                                # 前序都被分配
                                if num == len(pre_op[i]):
                                    level_1.append(i+1)
                            # 不存在前序情况
                            elif not pre_op[i]:
                                level_1.append(i+1)
                    # 选择工件更新装配线状态
                    if level_1:
                        num = random.randint(1, len(level_1))  # 在待选集合中选择一个工序安排
                        op = level_1[num - 1]
                        station_op[n][0].append(op)  # 添加工序到装配站
                        # 需要考虑等待时间
                        if wt_time[op-1] - station_time[n] - n * ct > 0:
                            other_t = wt_time[op-1] - station_time[n] - n * ct
                        else:
                            other_t = 0
                        # add工序在工作站的完工时间、工作站的完工时间
                        station_op[n][1].append(station_time[n] + data[op - 1][1] + other_t)
                        station_time[n] = station_time[n] + data[level_1[num - 1] - 1][1] + other_t
                        op_state[level_1[num - 1] - 1] = 1  # 该工件已分配位置
                    else:
                        no_suit_op = 1  # 没有工序可分配了
        this_ct = max(station_time)
        # 更新最优节拍、最优排序
        if this_ct <= min_ct:
            min_ct = this_ct
            min_sta_op = station_op
        elif iter_ct == 2:
            min_ct = this_ct
            min_sta_op = station_op
    # gantt.get_gantt(min_sta_op, num_s, data, min_ct)
    # 工件的开始装配时间
    try:
        b_t_op = []
        for i in range(sum_op):
            b_t_op.append([])
        for i in range(num_s):
            for j in range(len(min_sta_op[i][0])):
                b_t_op[min_sta_op[i][0][j]-1] = min_sta_op[i][1][j] + i*min_ct
    except UnboundLocalError:
        pass
    return min_ct, min_sta_op, b_t_op
