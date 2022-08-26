#  数据清洗后，画直线，对比清洗结果
import math
import random
import re
import os
import json
import pandas as pd
import xlrd
from datetime import date, datetime
import matplotlib.pyplot as plt

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import rgb2hex


# 数据清洗前后对比图，有干扰下、无干扰下 四个图
from mpl_toolkits.axisartist import axislines


def read_data_text(path):
    df = pd.read_csv(path, sep=':', header=None)
    print(df[5][0])
    a = []
    h = []
    # 四个距离
    for i in range(4):
       h.append([])

    k = 1
    for i in range(math.ceil(len(df[5])/4)):
        for j in range(4):
            try:
                h[j].append(int(df[5][k]))
                k += 1
            except KeyError:
                break
                pass
    # 画图
    # fig = plt.figure(1, figsize=(10, 6))
    # fig.subplots_adjust(bottom=0.2)
    #
    # fig = plt.figure()
    # df.plot()
    # plt.ylim(-2, 3)
    # plt.yticks(size=14, color='grey')
    # plt.xticks(size=14, color='grey')
    # 将(0,1)点和(2,4)连起来
    for i in range(len(h[0])):
        plt.plot([i, i+1], [h[0][i], h[0][i]+3], c='r')
    for i in range(len(h[0])):
        plt.plot([i, i+1], [h[1][i], h[1][i]+3], c='b')
    for i in range(len(h[0])):
        plt.plot([i, i+1], [h[2][i], h[2][i]+3], c='g')
    for i in range(len(h[0])):
        plt.plot([i, i+1], [h[3][i], h[3][i]+3], c='y')

    plt.show()
    pass

    # with open(path, 'r') as file:
    #     data = file.readlines()


def read_data_excel(path):
    file = path
    wb = xlrd.open_workbook(filename=file)  # 打开文件
    print(wb.sheet_names())  # 获取所有表格名字
    sheet1 = wb.sheet_by_index(0)  # 通过索引获取表格
    # 四个距离
    h = []
    for i in range(4):
       h.append([])
    # rows = sheet1.row_values(2)  # 获取行内容
    h[0] = sheet1.col_values(0)  # 获取列内容
    h[1] = sheet1.col_values(1)  # 获取列内容
    h[2] = sheet1.col_values(2)  # 获取列内容
    h[3] = sheet1.col_values(3)  # 获取列内容
    for i in range(4):
       for j in range(1,len(h[0])):
           try:
                h[i][j-1] = int(float(h[i][j]))
           except ValueError:
               break

    for i in range(len(h[0])):
        plt.plot([i, i+1], [h[0][i], h[0][i]+3], c='r')
    for i in range(len(h[0])):
        plt.plot([i, i+1], [h[1][i], h[1][i]+3], c='b')
    for i in range(len(h[0])):
        plt.plot([i, i+1], [h[2][i], h[2][i]+3], c='g')
    for i in range(len(h[0])):
        plt.plot([i, i+1], [h[3][i], h[3][i]+3], c='y')

    plt.show()
    pass

if __name__ == '__main__':
    path = ".\数据清洗" + '\\' + '4.异常.txt'
    # # 导入所有有无干扰下的四组数据
    # files = os.listdir(path)
    read_data_text(path)
    # read_data_excel(path)
    print('finish')


