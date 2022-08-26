#  车辆内部运输配件的路径规划问题
#  决策变量：车辆抵达配件的顺序
#  算法：随机迭代保优策略
import copy
import math
import random
from math import ceil

import matplotlib.pyplot as plt

import alb
from my_cluster import my_cluster, c_cluster


# 车辆需要访问工序集的路径规划问题
def VRP(op_car, wh_to_wh, wh_to_center, car_v, op_bg):
    """
    :param op_bg: 配件开始装配的时间
    :param car_v: 车速  m/s
    :param op_car: 每辆车运输的配件编号
    :param wh_to_wh: 配件到配件的距离
    :param wh_to_center: 配件到中心的距离
    :return: 每个车辆行驶的路程（优化后）、行驶的时间
    """
    if not op_car[0]:
        print('error')
    drive_car = []
    for i in range(4):  # 0: 车辆运输的路程 1: 车辆运输的路径
        drive_car.append([])
    dent_op = []
    for i in range(2):  # 0 滞留配件编号 1 配件的滞留时间
        dent_op.append([])
    # 工件的滞留时间
    dent_all_cars = []
    # 计算车辆的最优路径
    for a_car in range(len(op_car)):
        list_car_op = []
        for i in range(len(op_car[a_car])):  # 获取该车辆需要抵达的所有配件列表
            list_car_op.append(op_car[a_car][i])
            first_op = list_car_op[0]
        # 随机迭代的优化方式
        for j in range(10):
            # 随机打乱
            random.shuffle(list_car_op)
            # 地址数>=2
            if len(list_car_op) >= 2:
                sum_line = wh_to_center[list_car_op[0] - 1] + wh_to_center[
                    list_car_op[len(list_car_op) - 1] - 1]  # 首尾相加 第一个和最后一个配件位置
                for i in range(0, len(list_car_op) - 1):  # 配件到配件
                    sum_line += wh_to_wh[list_car_op[i] - 1][list_car_op[i + 1] - 1]
            # 地址数=1
            elif len(list_car_op) == 1:
                sum_line = wh_to_center[list_car_op[0] - 1] * 2
            # 地址数=0
            elif len(list_car_op) == 0:
                sum_line = 0
                min_order = []
                break
            # 首次计算的结果
            if j == 0:
                min_sum_line = sum_line
                min_order = copy.deepcopy(list_car_op)
            # 代数>=2
            if sum_line < min_sum_line:
                min_sum_line = sum_line
                min_order = copy.deepcopy(list_car_op)
        # print(a_car+1, min_order, min_sum_line)
        try:
            car_t = min_sum_line / car_v
        except UnboundLocalError:
            print('error')
        drive_car[0].append(min_sum_line)  # 运输路程
        drive_car[1].append(min_order)  # 运输路径
        drive_car[2].append(car_t)  # 运输时间
        drive_car[3].append(first_op)
        # 计算配件的滞留时间
        op_bg_t = []
        for i in range(len(wh_to_center)):
            op_bg_t.append([])
            for j in range(2):  # 0 编号 1 开始装配时间
                op_bg_t[i].append([])

        for i in range(len(wh_to_center)):  # 调整抵达时间列表 按编号顺序排列
            op_bg_t[op_bg[i][0] - 1][0] = op_bg[i][0]
            op_bg_t[op_bg[i][0] - 1][1] = op_bg[i][1]
        # 计算该辆车内配件抵达后的滞留时间
        dent_t_this_car = 0  # 这辆车内配件总的滞留时间
        for i in range(len(min_order)):  # 车内配件数
            dent_t_this_car += op_bg_t[min_order[i] - 1][1] - op_bg_t[first_op - 1][1]

        dent_all_cars.append(dent_t_this_car)  # 此车辆带来的滞留时间 添加到列表中

    total_den = sum(dent_all_cars)

    # print(len(op_car), dent_all_cars, '\n', total_den)

    sum_line_cars = round(sum(drive_car[0]), 2)
    return drive_car, sum_line_cars, total_den


# 配件分配给车辆的顺序 及 车辆的载重情况
# 决策变量： 车辆的数量（存在最小数量）、配件分配给车辆的顺序、车辆抵达本车配件的次序
# 目标： 车辆的运输总路程 （及车辆运输总次数 即车次）
def car_sch(pos_wh, this_order_op_bgt, car_max_w, wh_to_wh, wh_to_center, min_n_car, m_op, data, car_v):
    """
    :param pos_wh: 仓库地址
    :param op_bg: 配件开始装配的时间
    :param data: 配件数据集
    :param car_v: 车辆速度 m/s
    :param m_op: 配件总重量
    :param this_order_op_bgt:  配件 装配顺序 及开始时间
    :param car_max_w: 车辆的最大载重
    :param wh_to_wh: 配件到配件的 距离
    :param wh_to_center: 配件到装配中心的 距离
    :param min_n_car: 最小车辆数 (按载重计算得到)
    :return: 包含车辆数、路程、用时的数组
    """

    # 最大车辆数
    max_n_car = len(this_order_op_bgt)
    # k = ceil((max_n_car + min_n_car) / 2)
    k = min_n_car
    # 聚类算法将工厂地址划分与车辆数相同的簇
    my_cluster(pos_wh, k, data, car_max_w)
    # 车辆数的列表
    all_kinds_car = []
    for i in range(min_n_car, max_n_car + 1):
        all_kinds_car.append([])
    # 运输阶段的储存的结果
    cars = []
    for i in range(4):
        cars.append([])
    # 车辆数变化
    for num_car in range(min_n_car, max_n_car + 1):
        # 预设平均载重量  向上取整 前车载重大一点 最后一辆可以少点 向下可能导致最后一台车装不下
        ave_m_car = m_op / num_car
        # 每辆车的工序集
        op_car = []
        for i in range(num_car):
            op_car.append([])

        stop = 0
        # 最后一辆的工序集为空
        while not op_car[num_car - 1]:
            temp = 0  # 车辆累加
            m_sum = 0  # 车辆累计载重
            # 车辆得到工序集
            for i in range(len(this_order_op_bgt)):
                # 超载安排给下一辆
                if m_sum > ave_m_car:
                    temp += 1  # 下一辆车
                    m_sum = 0  # 载重清空
                # 分配方案导致车辆数不够
                if temp == num_car:
                    break
                else:
                    # 将配件加入车辆
                    op_car[temp].append(this_order_op_bgt[i][0])
                    # 将配件重量在车辆内累计
                    m_sum += data[this_order_op_bgt[i][0] - 1][4][0]

            if stop == 1:
                break
            # 最后一辆车没有得到工序集或最后一辆装不下, 调整预设载重
            if (not op_car[num_car - 1] or temp == num_car) and stop == 0:
                # 增加平均载重
                if temp == num_car:
                    ave_m_car = ave_m_car + 1
                    stop = 1
                else:  # 减小平均载重
                    ave_m_car = ave_m_car - 1
                # 清空车辆的工序集
                op_car = []
                for i in range(num_car):  # 建立该车辆数下 每辆车 的 配件列表
                    op_car.append([])

        # 车辆内部路径规划(用哪种方案呢 ? )
        drive_t_car, total_lines, total_den = VRP(op_car, wh_to_wh, wh_to_center, car_v, this_order_op_bgt)
        # 记录本次求解的方案
        cars[0].append(num_car)  # 车辆数
        cars[1].append(total_lines)  # 车辆运输总路程
        cars[2].append(drive_t_car)  # 每辆车运输的时间
        cars[3].append(total_den)  # 工件的滞留时间
    return cars


# 调整聚类的结果，使其匹配装配结果
def calcu_match(k, max_d_list, clu_list):
    Flag = 1
    # 重复、指导聚类结果与装配解完全匹配
    while 1 == Flag:
        sum_op = len(max_d_list)
        match_d = []
        # 利用匹配度最高的装配排序, 再次计算所有簇的匹配度
        for i in range(k):
            match_d.append([])
            if clu_list[i][0]:
                # 簇与装配排序的匹配度 每一个簇有一个匹配度
                list_a = []
                for j in range(len(clu_list[i][0])):
                    list_a.append(clu_list[i][0][j])
                first_op = -1
                flag = 0
                len_a = len(list_a)
                # 匹配
                for j in range(sum_op):
                    if not list_a:
                        break
                    op = max_d_list[j]
                    if op in list_a:
                        first_op = op
                        list_a.remove(op)
                    if first_op != -1:
                        flag += 1
            else:
                # 该车辆为空车
                flag = 1
                len_a = 0
            try:
                match_d[i] = len_a / flag
            except IndexError:
                pass
            except ZeroDivisionError:
                pass
        for i in range(k):
            a = i
            if match_d[i] != 0 and match_d[i] != 1:
                continue
        if (match_d[a] == 0 or match_d[a] == 1) and a == k - 1:
            break
        # 匹配度最高(不为1)的簇 吸收装配最优排序内的工序
        max_d = 0
        for i in range(k):
            if match_d[i]:
                try:
                    if match_d[i] > max_d and match_d[i] != 1:
                        max_index = i
                        max_d = match_d[i]
                except TypeError:
                    pass
        if max_d != 1:
            # 找到要吸收的工序  并尝试设计吸收范围
            list_a = []
            for j in range(len(clu_list[max_index][0])):
                list_a.append(clu_list[max_index][0][j])
            first_op = -1
            flag = 0
            list_b = []
            for i in range(sum_op):
                if not list_a:
                    break
                op = max_d_list[i]
                if op in list_a:
                    first_op = op
                    list_a.remove(op)
                elif first_op != -1 and not (op in list_a):
                    list_b.append(op)
                if first_op != -1:
                    flag += 1
            # 吸收这些工序
            for i in range(len(list_b)):
                clu_list[max_index][0].append(list_b[i])
            # 剔除这些工序
            for i in range(k):
                try:
                    if i != max_index:
                        set_del = []
                        for j in range(len(clu_list[i][0])):
                            if clu_list[i][0][j] in list_b:
                                op = clu_list[i][0][j]
                                set_del.append(op)
                        for j in range(len(set_del)):
                            clu_list[i][0].remove(set_del[j])
                except IndexError:
                    pass
            print(clu_list[max_index][0])
        else:
            match_d = 1
            pass

    return clu_list


# 计算运输成本
def calcu_trans_cost(clu_list, data, t_tran):
    """
    :param clu_list:
    :param data:
    :param t_tran: 每辆车运输路程
    :return:
    """
    car = truck_parameter()
    # 计算每辆车的载重、确定属于那种车辆运输
    per_total_m = []
    type_truck = []
    for i in range(len(clu_list)):
        per_total_m.append([])
        per_total_m[i] = 0
        for j in range(len(clu_list[i][0])):
            per_total_m[i] += data[clu_list[i][0][j]][4][0]
        # 乘10条并行
        per_total_m[i] = round(per_total_m[i] * 10, 2)
        for j in range(4):
            if car[j][0] >= per_total_m[i]:
                # 找到满足载重约束的车型
                type_truck.append(j)
                break
            if j == 3:
                print('装不下了')

    # 计算各种车型的总成本
    c_tran = 0
    for i in range(len(type_truck)):
        types = type_truck[i]
        # 计划车辆最终没用用到
        if t_tran != 0:
            per_cost = (car[types][1] * t_tran[i] + car[types][2])
            c_tran += per_cost
    tran_cost = c_tran
    return tran_cost


def Judge_Capacity(k, max_d_list, clu_list, data):
    # 获取车型、容量
    car = truck_parameter()
    # 计算每辆车的载重、确定属于那种车辆运输、调整装不下的车辆
    per_total_m = []
    type_truck = []
    for i in range(len(clu_list)):
        per_total_m.append([])
        per_total_m[i] = 0
        for j in range(len(clu_list[i][0])):
            per_total_m[i] += data[clu_list[i][0][j]][4][0]
        # 乘10条并行
        per_total_m[i] = round(per_total_m[i] * 10, 2)
        for j in range(4):
            if car[j][0] >= per_total_m[i]:
                # 找到满足载重约束的车型
                type_truck.append(j)
                break
            if j == 3:
                print('装不下了')
    pass


#  随机从装配解集合中选择一个装配解
def choose_ALB_rand(alb_set_res, data):
    sum_op = len(data)
    n_res = len(alb_set_res[2])  # 解的总个数
    choose_rand = random.randint(0, n_res - 1)  # 随机选一个解
    list_rand = []
    for i in range(sum_op):
        list_rand.append(alb_set_res[2][choose_rand][i] - 1)  # 一致性

    return list_rand, choose_rand


def ga_choose_alb_rand(alb_set_res, data):
    sum_op = len(data)
    n_res = len(alb_set_res[2])  # 解的总个数
    choose_rand = random.randint(0, n_res - 1)  # 随机选一个解
    list_rand = []
    for i in range(sum_op):
        list_rand.append(alb_set_res[2][choose_rand][i] - 1)  # 一致性

    return list_rand, choose_rand


#  聚类的结果是相对稳定的、大规模会有波动
def choice_ALB(alb_set_res, data, clu_list, k):
    max_match_d = 0  # 匹配度最高的装配排序的匹配度
    sum_op = len(data)
    # car = truck_parameter()
    # 调整运输的簇
    # 1计算较优运输方案与装配排序的匹配度
    for t in range(len(alb_set_res[2])):
        match_d = 0
        for i in range(k):
            if clu_list[i][0] != []:  # 计算每一簇
                # 簇与装配排序的匹配度 每一个簇有一个匹配度
                list_a = []
                for j in range(len(clu_list[i][0])):
                    list_a.append(clu_list[i][0][j])
                first_op = -1
                flag = 0
                len_a = len(list_a)
                # 匹配
                for j in range(sum_op):
                    if list_a == []:
                        break
                    try:
                        op = alb_set_res[2][t][j] - 1
                    except IndexError:
                        pass
                    if op in list_a:
                        first_op = op
                        list_a.remove(op)
                    if first_op != -1:
                        flag += 1
            else:
                # 该车辆为空车
                flag = 1
                len_a = 0

            match_d += len_a / flag

        # 确定簇的平均匹配度
        match_d = match_d / k
        # 更新匹配度最高的装配排序
        if t == 0:
            max_match_d = match_d
            max_t = t
        elif match_d > max_match_d:
            max_match_d = match_d
            max_t = t

    # 2确定匹配度最高的装配排序, 并根据装配排序调整运输的簇
    max_d_list = []
    for i in range(sum_op):
        try:
            max_d_list.append(alb_set_res[2][max_t][i] - 1)
        except UnboundLocalError:
            pass
    return max_d_list, max_t, max_match_d  # 所选装配排序 和 该排序在装配集合内的编号


def alb_c_vrp(alb_set_res, k, clu_list, data, p2p_t, p2c_t):
    '''
    :param alb_set_res: 装配优先
    :param per_a:
    :param per_b:
    :param data:
    :param p2c_t:
    :param p2p_t: 工厂到工厂的时间
    :param k: 车辆数
    :param clu_list: 车辆的目标工厂集
    :return: k车次下的运输成本、每辆车的运输时间、匹配度最高度排序
    '''

    sum_op = len(data)
    car = truck_parameter()
    # 调整运输的簇
    # 1计算较优运输方案与装配排序的匹配度
    for t in range(len(alb_set_res[2])):
        max_match_d = 0
        match_d = 0
        for i in range(k):
            if clu_list[i][0]:
                # 簇与装配排序的匹配度 每一个簇有一个匹配度
                list_a = []
                for j in range(len(clu_list[i][0])):
                    list_a.append(clu_list[i][0][j])
                first_op = -1
                flag = 0
                len_a = len(list_a)
                # 匹配
                for j in range(sum_op):
                    if not list_a:
                        break
                    try:
                        op = alb_set_res[2][t][j] - 1
                    except IndexError:
                        pass
                    if op in list_a:
                        first_op = op
                        list_a.remove(op)
                    if first_op != -1:
                        flag += 1
            else:
                # 该车辆为空车
                flag = 1
                len_a = 0
            try:
                match_d += len_a / flag
            except ZeroDivisionError:
                pass

        # 确定簇的平均匹配度
        match_d = match_d / k
        # 更新匹配度最高的装配排序
        if t == 1:
            max_match_d = match_d
            max_t = t
        elif match_d > max_match_d:
            max_match_d = match_d
            max_t = t

    # 2确定匹配度最高的装配排序, 并根据装配排序调整运输的簇
    max_d_list = []
    for i in range(sum_op):
        try:
            max_d_list.append(alb_set_res[2][max_t][i] - 1)
        except UnboundLocalError:
            pass
    # 调整每一簇, 使整体的匹配度=1，并保证每一簇符合车辆容量
    clu_list = calcu_match(k, max_d_list, clu_list)
    # 判断并调整使其满足车辆容量约束
    Judge_Capacity(k, max_d_list, clu_list, data)

    # 3确定运输的簇
    # 计算每一簇的路径问题
    # 时间成本
    t_tran = []
    sum_tran_t = 0
    for i in range(k):
        p2p_list = []
        for j in range(len(clu_list[i][0])):
            p2p_list.append(clu_list[i][0][j])
        len_list = len(p2p_list)
        min_sum_t = 999999
        for a in range(100):
            if len_list > 1:
                p1 = p2 = 0
                while p1 == p2:
                    p1 = random.randint(0, len_list - 1)
                    p2 = random.randint(0, len_list - 1)
                if p1 > p2:
                    tem = p1
                    p1 = p2
                    p2 = tem
                # p1移入p2之后
                tem = p2p_list[p1]
                for j in range(p1 + 1, p2):
                    p2p_list[j - 1] = p2p_list[j]
                p2p_list[p2 - 1] = tem
            # 计算该路径排序的时间成本
            sum_op = len(p2p_list)
            if sum_op == 0:
                # print('簇内元素为空')
                sum_t = 0
            elif sum_op == 1:
                sum_t = p2c_t[p2p_list[0]] * 2
                min_sum_t = sum_t
                min_list = p2p_list
                break
            elif sum_op > 1:
                # 首尾
                sum_t = p2c_t[p2p_list[0]] + p2c_t[p2p_list[sum_op - 1]]
                # 中间
                for j in range(0, sum_op - 1):
                    sum_t += p2p_t[p2p_list[j]][p2p_list[j + 1]]
            sum_t = round(sum_t, 2)
            if sum_t <= min_sum_t:
                min_sum_t = sum_t
                min_list = p2p_list
                p2p_list = min_list
        t_tran.append(min_sum_t)
        sum_tran_t += min_sum_t
    c_tran = calcu_trans_cost(clu_list, data, t_tran)
    # c_tran = per_a * k + per_b * sum_tran_t
    # 同时可视化所有车辆的路径仍有bug
    # show_line(data, min_list)
    # plt.show()
    return [c_tran, t_tran, max_t]


# 直接利用聚类最优的装配结果进行运输
def dirct_c_vrp(alb_set_res, k, clu_list, data, p2p_t, p2c_t):
    '''
    :param alb_set_res: 装配优先
    :param per_a:
    :param per_b:
    :param data:
    :param p2c_t:
    :param p2p_t: 工厂到工厂的时间
    :param k: 车辆数
    :param clu_list: 车辆的目标工厂集
    :return: k车次下的运输成本、每辆车的运输时间、匹配度最高度排序
    '''
    sum_op = len(data)
    # 计算每一簇(每辆车)的路径问题
    t_tran = []
    sum_tran_t = 0
    for i in range(k):
        p2p_list = []
        for j in range(len(clu_list[i][0])):
            p2p_list.append(clu_list[i][0][j])
        len_list = len(p2p_list)
        min_sum_t = 999999
        for a in range(100):
            if len_list > 1:
                p1 = p2 = 0
                while p1 == p2:
                    p1 = random.randint(0, len_list - 1)
                    p2 = random.randint(0, len_list - 1)
                if p1 > p2:
                    tem = p1
                    p1 = p2
                    p2 = tem
                # p1移入p2之后
                tem = p2p_list[p1]
                for j in range(p1 + 1, p2):
                    p2p_list[j - 1] = p2p_list[j]
                p2p_list[p2 - 1] = tem
            # 计算该路径排序的时间成本
            sum_op = len(p2p_list)
            if sum_op == 0:
                # print('簇内元素为空')
                sum_t = 0
            elif sum_op == 1:
                sum_t = p2c_t[p2p_list[0]] * 2
                min_sum_t = sum_t
                min_list = p2p_list
                break
            elif sum_op > 1:
                # 首尾
                sum_t = p2c_t[p2p_list[0]] + p2c_t[p2p_list[sum_op - 1]]
                # 中间
                for j in range(0, sum_op - 1):
                    sum_t += p2p_t[p2p_list[j]][p2p_list[j + 1]]
            sum_t = round(sum_t, 2)
            if sum_t <= min_sum_t:
                min_sum_t = sum_t
                min_list = p2p_list
                p2p_list = min_list

        t_tran.append(min_sum_t)
        sum_tran_t += min_sum_t
    # 计算运输成本
    c_tran = calcu_trans_cost(clu_list, data, t_tran)
    # 同时可视化所有车辆的路径仍有bug
    # show_line(data, min_list)
    # plt.show()
    return [c_tran, t_tran]


# 直接利用聚类最优的装配结果进行运输
def NSGA_dirct_c_vrp(k, clu_list, data, p2p_t, p2c_t):
    '''
    :param alb_set_res: 装配优先
    :param per_a:
    :param per_b:
    :param data:
    :param p2c_t:
    :param p2p_t: 工厂到工厂的时间
    :param k: 车辆数
    :param clu_list: 车辆的目标工厂集
    :return: k车次下的运输成本、每辆车的运输时间、匹配度最高度排序
    '''
    cars = truck_parameter()
    cost_per = cars[3][1]  # 每公里费用
    const_car = cars[3][2]  # 固定发车费用
    v_car = cars[3][2]  # 车速
    n_problem = len(clu_list)  # 需要求解的vrp数量
    n_add = 0  # 需要减除的空车数量
    for i in range(n_problem):
        if not clu_list[i]:
            n_add += 1
    n_problem = n_problem - n_add  # 真正使用的车辆数
    sum_total_path = 0  # 运输总里程
    t_cars = []

    sum_op = len(data)
    # 计算每一簇(每辆车)的路径问题
    t_tran = []
    sum_tran_t = 0
    for i in range(k):
        p2p_list = []
        for j in range(len(clu_list[i][0])):
            p2p_list.append(clu_list[i][0][j])
        len_list = len(p2p_list)
        min_sum_t = 999999
        for a in range(100):
            if len_list > 1:
                p1 = p2 = 0
                while p1 == p2:
                    p1 = random.randint(0, len_list - 1)
                    p2 = random.randint(0, len_list - 1)
                if p1 > p2:
                    tem = p1
                    p1 = p2
                    p2 = tem
                # p1移入p2之后
                tem = p2p_list[p1]
                for j in range(p1 + 1, p2):
                    p2p_list[j - 1] = p2p_list[j]
                p2p_list[p2 - 1] = tem
            # 计算该路径排序的时间成本
            sum_op = len(p2p_list)
            if sum_op == 0:
                # print('簇内元素为空')
                sum_t = 0
            elif sum_op == 1:
                sum_t = p2c_t[p2p_list[0]] * 2
                min_sum_t = sum_t
                min_list = p2p_list
                break
            elif sum_op > 1:
                # 首尾
                sum_t = p2c_t[p2p_list[0]] + p2c_t[p2p_list[sum_op - 1]]
                # 中间
                for j in range(0, sum_op - 1):
                    sum_t += p2p_t[p2p_list[j]][p2p_list[j + 1]]
            sum_t = round(sum_t, 2)
            if sum_t <= min_sum_t:
                min_sum_t = sum_t
                min_list = p2p_list
                p2p_list = min_list

        t_tran.append(min_sum_t)
        sum_tran_t += min_sum_t
    # 计算运输成本
    c_tran = calcu_trans_cost(clu_list, data, t_tran)

    return c_tran, n_problem


def show_line(data, min_list):
    # 路径可视化
    k = len(min_list)
    for i in range(k):
        sum_op = len(min_list[i])
        x1 = 50
        y1 = 50
        # 起始
        x2 = data[min_list[i][0]][3][0][0]
        y2 = data[min_list[i][0]][3][0][1]
        plt.plot([x1, x2], [y1, y2])
        # 结束
        x2 = data[min_list[i][sum_op - 1]][3][0][0]
        y2 = data[min_list[i][sum_op - 1]][3][0][1]
        plt.plot([x1, x2], [y1, y2])
        for j in range(0, sum_op - 1):
            x1 = data[min_list[i][j]][3][0][0]
            x2 = data[min_list[i][j + 1]][3][0][0]
            y1 = data[min_list[i][j]][3][0][1]
            y2 = data[min_list[i][j + 1]][3][0][1]
            plt.plot([x1, x2], [y1, y2])


# 运输为导向的装配线平衡和库存优化
def tran_alb(sum_op, s_cars_op, t_cars, data, cm, num_s, pre_op, k):
    for i in range(k):
        t_cars[i] = t_cars[i] * 60 * 60  # 运输时间与装配时间折算  小时-秒
    op_at = []
    for i in range(sum_op):
        op_at.append([])
    for i in range(0, k):
        for j in range(len(s_cars_op[i])):
            op_at[s_cars_op[i][j]] = t_cars[i]  # 计算工件抵达的时间

    min_ct, min_sta_op, b_t_op = alb.alb_2(op_at, data, cm, num_s, pre_op)  # 运输导向的装配
    alb_op_list = []
    for i in range(len(min_sta_op)):
        for j in range(len(min_sta_op[i][0])):
            alb_op_list.append(min_sta_op[i][0][j] - 1)  # 装配排序
    sum_op_bt = []
    for i in range(sum_op):
        sum_op_bt.append(b_t_op[i] + op_at[0])
    dent_op = []
    for i in range(sum_op):
        op = alb_op_list[i]
        dent_op.append(sum_op_bt[op] - op_at[op])  # 工件计算滞留时间(保持低位的库存)
    sum_deten = sum(dent_op)
    ave_ren = round(sum_deten / sum_op, 2)
    return min_ct, ave_ren  # 最小节拍、最小库存


# 不考虑车辆容量
def c_sch(lvns, total_m, num_s, pre_op, cm, pos_wh, data, p2p_t, p2c_t):
    '''
    :param p2c_t: 工厂到装配中心的时间
    :param p2p_t: 工厂到工厂的时间
    :param data: 工件数据
    :param pos_wh: 工厂位置
    :param alb_op_t:工件开始装配的时间,相对时间为第一个开始加工的工件
    :return: 运输成本、工件滞留时间
    '''
    car = truck_parameter()  # 车辆信息
    set_min_ct = []  # 节拍
    set_ave_ret = []  # 平均滞留时间
    set_c_tran = []  # 一辆车
    sum_op = len(data)  # 工厂数目
    # ------单车型，直接切片-----------
    n_cars_min = math.ceil(total_m / car[3][0])  # 最少车辆数= 总质量/车辆载重（向上取整）
    n_cars_max = sum_op
    for i in range(n_cars_min, n_cars_max):  # 车辆数决策变量
        n_cars = i
        label = c_cluster(n_cars, pos_wh, data)  # 以车辆数为聚类簇数进行聚类-选了一个装配排序
        clu_list = classify(label, n_cars, sum_op)  # 对工厂分簇
        s_cars_op = []
        for j in range(len(clu_list)):  # 数据结构一致
            s_cars_op.append(clu_list[j][0])
        cost_tran, n_real_cars, t_cars = vns_vrp(lvns, s_cars_op, p2p_t, p2c_t)  # 路径规划同文章算法
        min_ct, ave_ren = tran_alb(sum_op, s_cars_op, t_cars, data, cm, num_s, pre_op, n_real_cars)  # 装配线平衡、计算库存
        set_min_ct.append(min_ct)  # 记录最小节拍
        set_ave_ret.append(ave_ren)  # 记录工件平均滞留时间
        set_c_tran.append(cost_tran)  # 记录不同决策变量的运输成本

    return [set_c_tran, set_min_ct, set_ave_ret]


def truck_parameter():
    # 定义车型
    car = []
    for i in range(4):
        car.append([])
    for i in range(4):
        for j in range(4):
            car[i].append([])
    # 车辆容量
    car[0][0] = 400
    car[1][0] = 500
    car[2][0] = 600
    car[3][0] = 700
    # 每公里费用
    car[0][1] = 1.0
    car[1][1] = 1.5
    car[2][1] = 2.0
    car[3][1] = 2.5
    # 车辆固定发车费用
    car[0][2] = 50
    car[1][2] = 60
    car[2][2] = 70
    car[3][2] = 80
    # 不同车型的平均车速
    car[0][3] = 60
    car[1][3] = 55
    car[2][3] = 50
    car[3][3] = 45
    return car


# 利用聚类标签将工厂分簇
def classify(label, k, sum_op):
    clu_list = []
    for i in range(0, k):
        # 添加簇
        clu_list.append([])
        # 添加簇的记录维度：工序编号
        for j in range(2):
            clu_list[i].append([])
        # 将散点标记出聚类类别
        for j in range(sum_op):
            if label[j] == i:
                clu_list[i][0].append(j)
    return clu_list


# 对装配排序分车、进行路径规划、计算运输成本
def separate2cars(m_total_op, data, list_alb, n_alb, n_cars):
    copy_list_alb = copy.deepcopy(list_alb)
    n_op = len(data)
    cars = truck_parameter()  # 车辆信息    car[3][0] = 700
    m_car = cars[3][0]  # 车辆容量
    s_cars_op = []
    m_ave_car = m_total_op / n_cars  # 每辆车平均重量
    total_m, m_op = 0, 0  # 初始化
    for i in range(n_cars + 1):  # 创建-车辆派遣的地点(多创建一台车备用)
        s_cars_op.append([])

    for i in range(n_cars):  # 分配-车辆派遣的地点
        total_m = 0  # 初始化车辆装载0kg
        while True == 1:
            if copy_list_alb == []:  # 工厂全部分配完毕
                break
            op = copy_list_alb[0]  # 工序编号
            m_op = data[op][4][0]  # 工序重量
            m_op = m_op * 10  # 该工序对应十条装配线的重量
            if i != n_cars - 1:  # 非最后一台车
                if total_m + m_op > m_car or total_m > m_ave_car:  # 该工厂的工序装不下了
                    break
                else:
                    total_m += m_op  # 该工厂的工序装不下了
                    del copy_list_alb[0]  # 剔除已经分配工厂
                    s_cars_op[i].append(op)  # 放入档案集
            else:  # 最后一台车
                if total_m + m_op > m_car:  # 最后一台装不下，再加一台
                    # print('备用车启用')
                    del copy_list_alb[0]  # 剔除已经分配工厂
                    s_cars_op[n_cars].append(op)  # 放入档案集
                else:
                    total_m += m_op  # 该工厂的工序装不下了
                    del copy_list_alb[0]  # 剔除已经分配工厂
                    s_cars_op[i].append(op)  # 放入档案集

    return s_cars_op  # 返回工厂分组情况


def calculate_path(list_prod, p2p_t, p2c_t):
    # 计算该路径排序的时间成本
    p2p_list = list_prod
    sum_op = len(p2p_list)  # 行走的工厂数
    sum_t = 0  # 初始化总运行时间
    if sum_op == 0:  # 车辆为空
        print('空车')
        sum_t = 0
    elif sum_op == 1:  # 车辆仅抵达一个工厂
        sum_t = p2c_t[p2p_list[0]] * 2
    elif sum_op > 1:  # 车辆抵达2个及以上工厂
        sum_t = p2c_t[p2p_list[0]] + p2c_t[p2p_list[sum_op - 1]]  # 首尾
        for j in range(0, sum_op - 1):  # 中间
            sum_t += p2p_t[p2p_list[j]][p2p_list[j + 1]]
    sum_t = round(sum_t, 2)
    return sum_t  # 返回该辆车的总里程


# 插入算子
def insert(list_prod):
    n_list = len(list_prod)
    if n_list <= 2:
        pass
    else:  # 大于两点才有交叉的意义
        rand1, rand2 = 0, 0
        while rand1 == rand2:  # 产生两个不相同的点
            rand1 = random.randint(0, n_list - 1)
            rand2 = random.randint(0, n_list - 1)
        obj1 = list_prod[rand1]
        # ----前插没问题----
        if rand1 > rand2:
            del list_prod[rand1]  # 删除位置1的对象
            list_prod.insert(rand2, obj1)  # 将位置1对象插入位置2
        else:
            del list_prod[rand1]  # 删除位置1的对象
            list_prod.insert(rand2-1, obj1)  # 将位置1对象插入位置2
        # ----后插要调整----
    # print(list_prod)

    return list_prod


# 相邻交换算子
def interchange(list_prod):

    # print(list_prod)
    n_list = len(list_prod)
    if n_list <= 2:
        pass
    else:  # 大于两点才有交叉的意义
        rand1 = random.randint(0, n_list - 1)  # 随机选择一点
        obj1 = list_prod[rand1]
        del list_prod[rand1]  # 删除位置1的对象
        list_prod.insert(rand1 + 1, obj1)  # 将位置1对象插入位置2  # 超出会直接放在末尾
    return list_prod


# 交换算子
def swap(list_prod):
    n_list = len(list_prod)
    if n_list <= 2:
        pass
    else:  # 大于两点才有交叉的意义
        rand1, rand2 = 0, 0
        while rand1 == rand2:  # 产生两个不相同的点
            rand1 = random.randint(0, n_list - 1)
            rand2 = random.randint(0, n_list - 1)
        obj1 = list_prod[rand1]
        obj2 = list_prod[rand2]
        del list_prod[rand1]
        list_prod.insert(rand1, obj2)
        del list_prod[rand2]
        list_prod.insert(rand2, obj1)
    return list_prod


# 局部逆序算子
def Reverse_order(list_prod):

    n_list = len(list_prod)
    if n_list <= 2:
        pass
    else:  # 大于两点才有交叉的意义
        rand1, rand2 = 0, 0
        while rand1 == rand2:  # 产生两个不相同的点
            rand1 = random.randint(0, n_list - 1)
            rand2 = random.randint(0, n_list - 1)
        if rand1 > rand2:
            rand1, rand2 = rand2, rand1  # 交换两个位置，保证rand1为小

        n_length = rand2 - rand1 + 1
        if n_length >= 2:  # 两个以上才有意义
            n_change = math.floor(n_length / 2)  # 向下取整
            rand2 += 1
            for r1 in range(rand1, rand1 + n_change):  # 选取的位置递增
                rand2 -= 1  # 交换的位置递减
                obj1 = list_prod[r1]
                obj2 = list_prod[rand2]
                del list_prod[r1]
                list_prod.insert(r1, obj2)
                del list_prod[rand2]
                list_prod.insert(rand2, obj1)

    return list_prod


# 最优+随机选择一个动作
def choose_action(s_p_a):
    n_rand = random.randint(1, 10)
    if 1 <= n_rand <= 3:
        n_action = random.randint(0, 3)  # 随机选择一个动作
    else:
        n_action = s_p_a.index(max(s_p_a))  # 获取最大值的索引

    return n_action


# 标准vns选择邻域结构的方式
def order_choose_action():
    n_action = random.randint(0, 3)  # 随机选择一个动作
    return n_action


# 动作概率更新函数
def refresh_p(a, b, n_action, flag, s_p_action):

    par = a  # 奖励、惩罚概率
    per_bad = b
    n_len = len(s_p_action)  # 动作数量
    value_total = 0
    for i in range(n_len):
        value_total += s_p_action[i]
    if flag == 0:  # 惩罚
        s_p_action[n_action] = s_p_action[n_action] * (-per_bad + 1) / value_total
    elif flag == 1:  # 奖励
        s_p_action[n_action] = s_p_action[n_action] * (+par + 1) / value_total
    value_total = 0
    for i in range(n_len):  # 概率之和
        value_total += s_p_action[i]
    for i in range(n_len):  # 归一化
        s_p_action[i] = s_p_action[i] / value_total

    return s_p_action


# 学习型变邻域搜索算法求解路径规划
def vns_vrp(a, b, lvns, s_cars_op, p2p_t, p2c_t):
    cars = truck_parameter()
    cost_per = cars[3][1]  # 每公里费用
    const_car = cars[3][2]  # 固定发车费用
    v_car = cars[3][2]  # 车速
    n_problem = len(s_cars_op)  # 需要求解的vrp数量
    n_add = 0  # 需要减除的空车数量
    for i in range(n_problem):
        if not s_cars_op[i]:
            n_add += 1
    n_problem = n_problem - n_add  # 真正使用的车辆数
    sum_total_path = 0  # 运输总里程
    t_cars = []
    for i in range(n_problem):  # 解决n-problem个VRP问题
        new_list_prod = []  # 初始化
        list_prod = s_cars_op[i]  # 待处理的排序
        ini_total_path = calculate_path(list_prod, p2p_t, p2c_t)  # 评价此序列的路径长度
        old_path = ini_total_path  # 旧解的评价值
        best_list = list_prod  # 初始化最优解
        best_path = old_path  # 最优评价值
        n_length = len(list_prod)
        s_p_a = []
        for j in range(4):   # 初始化动作的概率值
            s_p_a.append(0.25)
        for j in range(n_length * 10):  # 路径优化迭代次数
            if lvns == 1:  # 通过概率选择邻域结构
                n_action = choose_action(s_p_a)
            else:  # 标准vns、按顺序执行领域结构
                n_action = order_choose_action()
            old_list_prod = copy.deepcopy(best_list)  # 旧解
            if n_action == 0:  # 根据动作选择函数选择动作
                new_list_prod = Reverse_order(old_list_prod)  # 局部逆序算子-新解
            elif n_action == 1:
                new_list_prod = swap(old_list_prod)  # 交换算子-新解
            elif n_action == 2:
                new_list_prod = insert(old_list_prod)  # 插入算子-新解
            elif n_action == 3:
                new_list_prod = interchange(old_list_prod)  # 相邻交换算子-新解

            new_path = calculate_path(new_list_prod, p2p_t, p2c_t)  # 评价此序列的路径长度
            flag = 0
            if new_path < best_path:  # 新解更好
                best_path = new_path
                best_list = new_list_prod
                flag = 1  # 给与奖励
            else:
                flag = 0  # 给与惩罚
            if lvns == 1:  # 启用学习型vns更新
                s_p_a = refresh_p(a, b, n_action, flag, s_p_a)  # 更新动作执行后的概率
            else:
                pass

        total_path = best_path  # 输出最优路径值
        t_cars.append(total_path / v_car)  # 车辆在途用时
        sum_total_path += total_path

    cost_total = sum_total_path * cost_per + n_problem * const_car  # 运输总成本 = 里程成本 + 固定发车成本
    round(cost_total, 2)
    return cost_total, n_problem, t_cars  # 返回运输成本、真正使用的车辆数、车辆返回的用时


# 生成初始初始种群
def generate_pop(list_prod, n_pop):
    pop = []
    pop_value = []
    for i in range(n_pop):
        copy_list = copy.deepcopy(list_prod)
        for j in range(20):  # 随机打乱列表次数
            copy_list = insert(copy_list)
        pop.append(copy_list)
        pop_value.append(0)
    return pop, pop_value


# 交叉
def ga_cross(pop, ind1, ind2):

    n_ind1 = ind1
    n_ind2 = ind2
    pop_ind = copy.deepcopy(pop)
    n_data = len(pop[ind1])  # 数据长度
    in_ind = []
    for i in range(n_data):
        in_ind.append(-1)

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
        s_num.append(pop[n_ind1][j])
    #   将片段遗传给子代
    for j in range(n_pos1, n_pos2 + 1):
        in_ind[j] = pop_ind[n_ind1][j]
    #   补充两段剩余元素
    n_p = 0
    for j in range(0, n_data):
        if not pop_ind[n_ind2][j] in s_num:
            # 该位置没有被补充
            if in_ind[n_p] == -1:
                # 传递给子代
                in_ind[n_p] = pop_ind[n_ind2][j]
                n_p += 1
            else:
                n_p = n_pos2 + 1
                # 传递给子代
                in_ind[n_p] = pop_ind[n_ind2][j]
                n_p += 1

    return in_ind


# 交叉-变异-算法求解路径规划
def ga_vrp(s_cars_op, p2p_t, p2c_t):

    cars = truck_parameter()
    cost_per = cars[3][1]  # 每公里费用
    const_car = cars[3][2]  # 固定发车费用
    v_car = cars[3][2]  # 车速
    n_problem = len(s_cars_op)  # 需要求解的vrp数量
    n_add = 0  # 需要减除的空车数量
    for i in range(n_problem):
        if not s_cars_op[i]:
            n_add += 1
    n_problem = n_problem - n_add  # 真正使用的车辆数
    sum_total_path = 0  # 运输总里程
    t_cars = []
    n_pop = 20  # 种群大小
    total_line = 0  # 总里程
    for i in range(n_problem):  # 解决n-problem个VRP问题
        new_list_prod = []  # 初始化
        list_prod = s_cars_op[i]  # 待处理的排序
        n_length = len(list_prod)
        if n_length >= 3:  # 地点数量<3
            pop, pop_value = generate_pop(list_prod, n_pop)
            for j in range(n_pop):
                pop_value[j] = calculate_path(pop[j], p2p_t, p2c_t)  # 评价此序列的路径长度
            best_line = min(pop_value)
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
                    pop_value[j] = calculate_path(pop[j], p2p_t, p2c_t)  # 评价此序列的路径长度
                min_line = min(pop_value)  # 种群内最短路径
                min_index = pop_value.index(min_line)  # 种群内最短路径个体的系数
                min_list = pop[min_index]  # 该个体的序列
                if min_line < best_line:
                    best_line = min_line
        else:  # 地点数量<3
            best_line = calculate_path(list_prod, p2p_t, p2c_t)  # 评价此序列的路径长度
            min_list = list_prod  # 该个体的序列

        total_line += best_line
        t_cars.append(best_line / v_car)  # 车辆在途用时

    cost_total = total_line * cost_per + n_problem * const_car  # 运输总成本 = 里程成本 + 固定发车成本
    round(cost_total, 2)
    return cost_total, n_problem, t_cars  # 返回运输成本、真正使用的车辆数、车辆返回的用时


# 装配为导向，装配与运输协同优化方法
def alb_c_sch(a, b, lvns, exp, total_m, num_s, pre_op, cm, set_alb_res, pos_wh, data, p2p_t, p2c_t):
    '''
    :param set_alb_res: 多组优质装配排列的集合
    :param p2c_t: 工厂到装配中心的时间
    :param p2p_t: 工厂到工厂的时间
    :param data: 工件数据
    :param pos_wh: 工厂位置
    :param alb_op_t:工件开始装配的时间,相对时间为第一个开始加工的工件
    :return: 运输成本、工件滞留时间
    '''
    car = truck_parameter()
    set_min_ct = []  # 节拍
    set_ave_ret = []  # 库存
    set_c_tran = []  # 运输成本
    sum_op = len(data)
    # ------单车型，直接切片-----------
    n_cars_min = math.ceil(total_m / car[3][0])  # 最少车辆数= 总质量/车辆载重（向上取整）
    n_cars_max = sum_op
    for i in range(n_cars_min, n_cars_max):  # 车辆数决策变量
        n_cars = i
        # ----利用聚类推荐一个解-----
        # label = c_cluster(n_cars, pos_wh, data)  # 以车辆数为聚类簇数进行聚类-选了一个装配排序
        # clu_list = classify(label, n_cars, sum_op)  # 对工厂分簇
        # list_alb, n_alb, p_comp = choice_ALB(set_alb_res, data, clu_list, n_cars)  # 利用聚类结果推荐一个装配排序
        # -----------------------
        list_alb, n_alb = choose_ALB_rand(set_alb_res, data)  # 从装配排序装选择一个集
        s_cars_op = separate2cars(total_m, data, list_alb, n_alb, n_cars)  # 工厂指派给车辆
        cost_tran, n_real_cars, t_cars = vns_vrp(a, b, lvns, s_cars_op, p2p_t, p2c_t)  # 计算运输成本
        ave_ren = caclu_deten(sum_op, n_real_cars, s_cars_op, list_alb, data)  # 计算滞留时间
        set_min_ct.append(set_alb_res[0][0])  # 记录最小节拍
        set_ave_ret.append(ave_ren)  # 记录工件平均滞留时间
        set_c_tran.append(cost_tran)  # 记录不同决策变量的运输成本

    # 决策变量(车辆数)：从最少到最大变化
    # ----------------------------------
    # for k in range(min_c, max_c + 1):
    #     # k*最大容量
    #     if k*car[3][0] < total_m:
    #         continue
    #     else:  # 这种车辆数是可以满足装在需求的
    #         # ————————————
    #         # 聚类指导的分车(效率不高)
    #         label = c_cluster(k, pos_wh, data)
    #         # —————————————
    #         # _____________
    #         # 随机分车(最垃圾)
    #         # label = []
    #         # for i in range(len(data)):
    #         #     label.append(random.randint(0, k-1))
    #         # ______________
    #         # ——————————————
    #         # 固定分车(只有一个两个解)
    #         # label = [1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0]
    #         # ——————————————
    #         # 聚类结果分簇
    #         clu_list = []
    #         for i in range(0, k):
    #             # 添加簇
    #             clu_list.append([])
    #             # 添加簇的记录维度：工序编号
    #             for j in range(2):
    #                 clu_list[i].append([])
    #             # 将散点标记出聚类类别
    #             for j in range(sum_op):
    #                 if label[j] == i:
    #                     clu_list[i][0].append(j)
    #         # 聚类结果与装配结果匹配策略、匹配调整策略
    #         # 这里的匹配应该是基于概率的，而不是确定的
    #         [c_tran, t_of_cluster, max_t] = alb_c_vrp(set_alb_res, k, clu_list, data, p2p_t, p2c_t)
    #
    #         # 添加min_CT
    #         for i in range(sum_op):
    #             set_min_ct.append(set_alb_res[0][max_t])
    #         alb_op_list = []
    #         # 抓取最优排序
    #         sum_sta = len(set_alb_res[1][max_t])
    #         for i in range(sum_sta):
    #             sum_sta_op = len(set_alb_res[1][max_t][i][0])
    #             # i工作站内工序编号
    #             for j in range(sum_sta_op):
    #                 alb_op_list.append(set_alb_res[1][max_t][i][0][j])
    #
    #         # 记录不同决策变量的运输成本
    #         set_c_tran.append(c_tran)
    #         # 工件计算滞留时间(保持低位的库存)
    #         ave_ren = caclu_deten(sum_op, k, clu_list, alb_op_list, data)
    #         # 滞留时间的解
    #         set_ave_ret.append(ave_ren)
    # ---------------------------------------------

    return [set_c_tran, set_min_ct, set_ave_ret], set_alb_res


# 计算滞留时间
def caclu_deten(sum_op, n_real_cars, clu_list, alb_op_list, data):
    # 遍历工序
    tube = []
    first_op = []

    for i in range(sum_op):  # 遍历簇
        for j in range(n_real_cars):  # 遍历车辆
            if alb_op_list[i] in clu_list[j] and j not in tube:
                op = alb_op_list[i]
                first_op.append(op)  # 目的：找到每辆车第一个被装配的工序
                # 屏蔽簇
                tube.append(j)
                break

    retention = []
    # 计算所有工件的滞留时间
    add_t = 0
    for i in range(sum_op):
        # 工件编号
        op = alb_op_list[i]
        # 是该组首个
        if op in first_op:
            begin = i
            # 该工件的加工时间
            add_t = data[op][1]
            # 该工件的滞留时间为0
            retention.append(0)
        # 不是首个工件
        elif op not in first_op:
            try:
                # 该工件的滞留时间
                retention.append(add_t)
            except UnboundLocalError:
                pass
                # 该工件的加工时间加入后续工件的滞留时间
                add_t += data[op][1]
    # 总滞留时间
    sum_ren = sum(retention)
    # 工件的平均滞留时间
    ave_ren = round(sum_ren / sum_op, 2)
    return ave_ren


# 关键环节验证2：装配最优与运输最优不沟通
def dirct_c_sch(nsga_2, lvns, total_m, num_s, pre_op, cm, set_alb_res, pos_wh, data, p2p_t, p2c_t, list_alb, n_alb):
    '''
    :param set_alb_res: 多组优质装配排列的集合
    :param p2c_t: 工厂到装配中心的时间
    :param p2p_t: 工厂到工厂的时间
    :param data: 工件数据
    :param pos_wh: 工厂位置
    :param alb_op_t:工件开始装配的时间,相对时间为第一个开始加工的工件
    :return: 运输成本、工件滞留时间
    '''
    car = truck_parameter()
    set_min_ct = []  # 节拍
    set_ave_ret = []  # 库存
    set_c_tran = []  # 运输成本
    sum_op = len(data)
    # ------单车型，直接切片-----------
    n_cars_min = math.ceil(total_m / car[3][0])  # 最少车辆数= 总质量/车辆载重（向上取整）
    n_cars_max = sum_op
    for i in range(n_cars_min, n_cars_max):  # 车辆数决策变量
        n_cars = i
        list_alb, n_alb = ga_choose_alb_rand(set_alb_res, data)  # 从装配排序装选择一个集
        s_cars_op = separate2cars(total_m, data, list_alb, n_alb, n_cars)  # 工厂指派给车辆
        if nsga_2 == 0:  # 变邻域搜索求解VRP子问题
            cost_tran, n_real_cars, t_cars = vns_vrp(lvns, s_cars_op, p2p_t, p2c_t)  # 计算运输成本
        else:  # 交叉变异求解VRP子问题
            cost_tran, n_real_cars, t_cars = ga_vrp(s_cars_op, p2p_t, p2c_t)  # 计算运输成本

        ave_ren = caclu_deten(sum_op, n_real_cars, s_cars_op, list_alb, data)  # 计算滞留时间
        set_min_ct.append(set_alb_res[0][0])  # 记录最小节拍
        set_ave_ret.append(ave_ren)  # 记录工件平均滞留时间
        set_c_tran.append(cost_tran)  # 记录不同决策变量的运输成本

    return [set_c_tran, set_min_ct, set_ave_ret]
