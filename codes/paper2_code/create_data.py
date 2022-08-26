import random
import re
import os
import json

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import rgb2hex


def create_data(path):  # 地址不对
    with open(path, 'r') as file:
        data = file.readlines()

    # 建立5*n矩阵表示与工件相关的所有信息
    num_operation = int(data[0])
    op = []
    for i in range(num_operation):
        op.append([])
        for j in range(5):
            if j == 0:
                op[i].append(i+1)
            else:
                op[i].append([])

    data_time = []
    operation_time = []
    for i in range(num_operation):
        data_time.append(data[i+1])
        operation_time.append(int(data_time[i]))

    # 工件的装配时间
    for i in range(num_operation):
        op[i][1] = operation_time[i]

    order = re.compile(r'\d(\d)?')
    relation = re.compile(r'(\d\d$|\d$)')
    operation_relation = []

    # 工件的紧邻后续装配工序
    for i in range(num_operation+1, num_operation+1+len(data)-num_operation-1):
        try:
            a = re.match(order, data[i]).group()  # 匹配到序号
            b = re.findall(relation, data[i])  # 匹配到后边的紧邻相干序列
            op[int(a)-1][2].append(int(b[0]))
        except AttributeError:
            continue
    # 工件摆放在矩形仓库中
    # 工件所在仓库的坐标位置
    # x = 200  # 单位/米
    # rec = 0
    # y = 0
    # print(num_operation)
    # if num_operation == 11:
    #     print('stop')
    # for i in range(num_operation):
    #     rec += 1
    #     if rec == 11:
    #         x += 10  # 第二排库存
    #         rec = 1
    #         y = 5
    #         op[i][3].append((x, y))
    #         print(x, y)
    #     else:
    #         y += 5
    #         op[i][3].append((x, y))
    #         print(x, y)

    # 工件分散在以装配中心的周围
    set_pos = []
    set_pos.append((0, 0))
    for i in range(num_operation):
        x = 0
        y = 0
        while (x, y) in set_pos:
            j = random.randint(1, 4)
            if j == 1:
                x = random.randint(0, 25)
                y = random.randint(0, 100)
            elif j == 2:
                x = random.randint(75, 100)
                y = random.randint(0, 100)
            elif j == 3:
                x = random.randint(25, 75)
                y = random.randint(75, 100)
            elif j == 4:
                x = random.randint(25, 75)
                y = random.randint(0, 25)

        op[i][3].append((x, y))
        set_pos.append((x, y))
    # 显示创建的数据
    colors = tuple([(np.random.random(), np.random.random(), np.random.random()) for i in range(1)])
    colors = [rgb2hex(x) for x in colors]
    for i in range(len(data)):
        try:
            plt.plot(op[i][3][0][0], op[i][3][0][1], 'o', color='blue')  # 仓库在地图上的位置
        except IndexError:
            pass
    plt.show()
    # plt.close('all')
    # 工件的重量
    for i in range(num_operation):
        v = random.uniform(5, 10)
        v = round(v, 2)
        op[i][4].append(v)
    return op


# 保存数据到文件
def save_data(file_name, data):
    path = '.\second_data_cases'+'\\'+file_name
    with open(path, 'w') as f_obj:   # 先从数据库中查询，没有的话，则写入新的用户文件
        json.dump(data, f_obj)


# p = os.getcwd()
# # print(p)
# files = open('D:\集成调度问题\代码\init_data_cases\BUXEY.IN2')
if __name__ == '__main__':
    path = ".\init_data_cases"
    files = os.listdir(path)
    for file_name in files:
        path = ".\init_data_cases"
        path = path+'\\'+file_name
        data = create_data(path)
        save_data(file_name, data)

    print('finish')




