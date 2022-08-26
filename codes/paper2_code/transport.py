import math

from sympy import solve, Symbol


# 运输阶段(随机)
def transport_1(label, n_car, wh_to_wh, wh_to_center):
    car_tasks = []
    car_finish_time = []
    for i in range(n_car):
        car_tasks.append([])
    for i in range(len(label)):
        car_tasks[label[i]].append(i)

    car_finish_time = []
    for i in range(n_car):
        car_finish_time.append([])
        temp = 0
        for j in range(len(car_tasks[i]) - 1):
            temp += (wh_to_wh[car_tasks[i][j]][car_tasks[i][j + 1]])
        car_finish_time[i] = round(temp, 2)

    for i in range(n_car):
        try:
            last_wh = len(car_tasks[i])
            car_finish_time[i] += (wh_to_center[car_tasks[i][0]] + wh_to_center[car_tasks[i][last_wh - 1]])
            car_finish_time[i] = round(car_finish_time[i], 2)
        except IndexError:
            print(i)
            print(car_tasks)
            print(car_tasks[i][0])
            print(wh_to_center[car_tasks[i][0]])
            print(wh_to_center[car_tasks[i][last_wh - 1]])

    # 每个工件抵达的时间
    arrive_time = []
    for i in range(len(label)):
        arrive_time.append([])
    for i in range(len(car_tasks)):
        for j in range(len(car_tasks[i])):
            arrive_time[car_tasks[i][j]] = car_finish_time[i]

    total_t = 0
    for i in range(len(arrive_time)):
        total_t += arrive_time[i]

    b = Symbol('b')
    b = solve([b * n_car / ((1 - b) * total_t) - 7 / 3], b)
    b = list(b.values())[0]
    cost = round(b * n_car + (1 - b) * total_t, 2)

    return arrive_time, cost


# 包含车辆载重的运输阶段
def transport_2(label, n_car, wh_to_wh, wh_to_center):
    '''
    :param label: 配件属于 哪一辆车
    :param cars_op_wi: 车辆包含的 配件编号 & 配件 的重量
    :param n_car: 车辆数
    :param wh_to_wh: 配件到配件 的距离
    :param wh_to_center: 各配件到中心 的距离
    :return: 达到时间 和运输总成本
    '''

    car_tasks = []
    car_finish_time = []
    for i in range(n_car):  # 车辆数目
        car_tasks.append([])
    for i in range(len(label)):  # 车辆需要运输的配件编号  【数值+1=编号】
        car_tasks[label[i]].append(i)

    for i in range(n_car):  # 计算车辆的抵达时间  【没有计算中心出发及返回中心的时间】
        car_finish_time.append([])
        temp = 0
        for j in range(len(car_tasks[i]) - 1):
            temp += (wh_to_wh[car_tasks[i][j]][car_tasks[i][j + 1]])
        car_finish_time[i] = round(temp, 2)

    # 每个工件抵达的时间
    arrive_time = []
    for i in range(len(label)):
        arrive_time.append([])
    for i in range(len(car_tasks)):
        for j in range(len(car_tasks[i])):
            arrive_time[car_tasks[i][j]] = car_finish_time[i]

    total_t = 0
    for i in range(len(arrive_time)):
        total_t += arrive_time[i]

    b = Symbol('b')
    b = solve([b * n_car / ((1 - b) * total_t) - 7 / 3], b)
    b = list(b.values())[0]
    cost = round(b * n_car + (1 - b) * total_t, 2)

    return arrive_time, cost


# 有限设车辆重复调度，以此减少配件在装配中心的滞留时间
def transport_3(label, all_cars_need, cars_op_num, n_car_have, wh_to_wh, wh_to_center):
    '''
    :param cars_op_num:
    :param label:
    :param all_cars_need:   需要的车辆总数
    :param n_car_have: 拥有的车辆数目，每批车辆数目
    :param wh_to_wh:
    :param wh_to_center:
    :return:
    '''
    lot = math.ceil(all_cars_need / n_car_have)  # 需要的运输批次
    lot_cars = []
    for i in range(0, lot):  # 运输的批次  按批次计算配件抵达的时间
        lot_cars.append([])
        for j in range(n_car_have):  # 批次内车辆数目
            lot_cars[i].append([])

    # print(wh_to_center)
    # 各车辆出发经所有配件点返回的总时间
    cars_time = []
    for i in range(len(cars_op_num)):
        cars_time.append(0)
    for i in range(len(cars_op_num)):  # 将划分的所有组 用车辆 运输
        if cars_op_num[i][0]:
            for j in range(len(cars_op_num[i][0]) - 1):  # 配件数
                cars_time[i] += wh_to_wh[j][j + 1]
            cars_time[i] += round(wh_to_center[cars_op_num[i][0][0] - 1] + wh_to_center[
                cars_op_num[i][0][len(cars_op_num[i][0]) - 1] - 1], 2)
        else:
            break
    # 各车辆的运输时间
    # print('车辆抵达时间：')
    # print(cars_time)
    # print('按批次调整后的车辆抵达时间：')
    # 车辆抵达时间
    car_arrive_time = []
    for i in range(len(label)):
        car_arrive_time.append([])

    op_arr_time = []  # 建立工件抵达的时间
    for i in range(len(label)):
        op_arr_time.append([])

    for i in range(0, lot):  # 要分的批次
        for j in range(0, n_car_have):  # 每批次需要计算的车辆抵达时间
            if i == 0:  # 第一批 不用管车辆抵达的顺序
                car_arrive_time[j] = cars_time[j]
                for k in range(len(cars_op_num[j][0])):
                    op_arr_time[cars_op_num[j][0][k] - 1] = round(car_arrive_time[j], 2)  # 第一批次的配件抵达时间

            else:  # 考虑车辆抵达的顺序（仅）  也 考虑后续路程的长度（不考虑，直接按分的顺序）
                temp_arr_time = sorted(car_arrive_time[(i - 1) * n_car_have:(i - 1) * n_car_have + n_car_have])
                # print('车辆抵达时间排序（升序）：')
                # print(temp_arr_time)
                # temp_next_time = sorted(cars_time[i*n_car_have:i*n_car_have + n_car_have], reverse=True)
                # print('下一批次目标簇运输时间排序（降序）：')
                # print(temp_next_time)
                # print('批次抵达时间：')
                car_arrive_time[i * n_car_have - 1 + j] = temp_arr_time[j] + cars_time[i * n_car_have + j]
                for k in range(len(cars_op_num[i * n_car_have + j][0])):
                    op_arr_time[cars_op_num[i * n_car_have + j][0][k] - 1] = round(car_arrive_time[i * n_car_have - 1 + j],
                                                                                   2)  # 第一批次的配件抵达时间
    # print('所有车辆抵达时间：')
    # print(car_arrive_time)
    # print('各配件抵达时间：')
    # print(op_arr_time)
    #  把抵达时间对应大配件层面
    # 计算批次内每辆车抵达的抵达时间
    # print(cars_op_num_weight)
    # print('...')
    trans_cost = 0
    return op_arr_time, trans_cost
