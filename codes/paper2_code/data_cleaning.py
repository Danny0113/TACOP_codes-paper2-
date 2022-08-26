import math
import random
import re
import os
import json

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import rgb2hex


def create_data(path):
    with open(path, 'r') as file:
        data = file.readlines()

    # 建立二维存储矩阵
    m2 =[]
    # 前两行没用
    sum_hang = len(data)
    sum_team = math.ceil((sum_hang - 2)/4)
    for i in range(sum_team):
        m2.append([])
        for j in range(8):
            m2[i].append([])

    # 提取时间
    time = re.compile(r'.*:(.*):')
    # 提取距离
    # dis = re.compile()
    # 组数
    for i in range(0, sum_team):
        # 组内包含时间4条
        for j in range(0, 4):
            try:
                a = re.findall(time, data[i*j+2]).group()  # 匹配到序号
            except IndexError:
                print(a)
            print(a)
    print(a)

    # order = re.compile(r'\d(\d)?')
    # relation = re.compile(r'(\d\d$|\d$)')
    # operation_relation = []

    # # 工件的紧邻后续装配工序
    # for i in range(num_operation + 1, num_operation + 1 + len(data) - num_operation - 1):
    #     try:
    #         a = re.match(order, data[i]).group()  # 匹配到序号
    #         b = re.findall(relation, data[i])  # 匹配到后边的紧邻相干序列
    #         op[int(a) - 1][2].append(int(b[0]))
    #     except AttributeError:
    #         continue
    return m2


# 保存数据到文件
def save_data(file_name, data):
    path = '.\清洗后正常数据' + '\\' + file_name
    with open(path, 'w') as f_obj:  # 先从数据库中查询，没有的话，则写入新的用户文件
        json.dump(data, f_obj)


# p = os.getcwd()
# # print(p)
# files = open('D:\集成调度问题\代码\init_data_cases\BUXEY.IN2')
if __name__ == '__main__':
    path = ".\正常数据"
    # 导入所有文件名
    files = os.listdir(path)
    # 逐个处理所有文件
    for file_name in files:
        path = ".\正常数据"
        path = path + '\\' + file_name
        # 抓取并处理数据
        data = create_data(path)
        # 保存数据
        save_data(file_name, data)

    print('finish')
