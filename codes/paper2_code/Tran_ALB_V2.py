import copy
import math
import random
from scipy.interpolate import griddata
import numpy as np
import xlwt
import time
from datetime import datetime

from matplotlib import pyplot as plt
from matplotlib.colors import rgb2hex
from mpl_toolkits.mplot3d import Axes3D

import alb
import my_cluster
import gantt
import other
import transport
import evaluate
from comp import NS_GA
from dent_op import calculation_den
from digraph import digraph
import trans

from ini import ini_all, initial
from pareto import re_pareto, re_pareto2
from show3D import show_result_3D
from matplotlib import cm

from surface3D import matching_3D


def NN_RN(pareto_res):
    # 三个目标
    merge_res = []
    for i in range(3):
        merge_res.append([])
    # 合并所有算法的pareto_res
    num_ag = len(pareto_res)
    for i in range(num_ag):
        for j in range(len(pareto_res[i][0])):
            merge_res[0].append(pareto_res[i][0][j])
            merge_res[1].append(pareto_res[i][1][j])
            merge_res[2].append(pareto_res[i][2][j])
    # 计算非支配解的占优个数、占优比
    nn = []
    rn = []
    for i in range(num_ag):
        nn.append([])
        rn.append([])
    # 算法
    for i in range(num_ag):
        count = 0
        # 算法非支配解数目
        for j in range(len(pareto_res[i][0])):
            # 与所有其它非支配解比较
            for k in range(len(merge_res[0])):
                if ((merge_res[0][k] < pareto_res[i][0][j]) and (merge_res[1][k] < pareto_res[i][1][j]) and (
                        merge_res[2][k] < pareto_res[i][2][j])) \
                        or ((merge_res[0][k] < pareto_res[i][0][j]) and (merge_res[1][k] == pareto_res[i][1][j]) and (
                        merge_res[2][k] == pareto_res[i][2][j])) \
                        or ((merge_res[0][k] == pareto_res[i][0][j]) and (merge_res[1][k] == pareto_res[i][1][j]) and (
                        merge_res[2][k] < pareto_res[i][2][j])) \
                        or ((merge_res[0][k] == pareto_res[i][0][j]) and (merge_res[1][k] < pareto_res[i][1][j]) and (
                        merge_res[2][k] == pareto_res[i][2][j])) \
                        or ((merge_res[0][k] == pareto_res[i][0][j]) and (merge_res[1][k] < pareto_res[i][1][j]) and (
                        merge_res[2][k] < pareto_res[i][2][j])) \
                        or ((merge_res[0][k] < pareto_res[i][0][j]) and (merge_res[1][k] == pareto_res[i][1][j]) and (
                        merge_res[2][k] < pareto_res[i][2][j])) \
                        or ((merge_res[0][k] < pareto_res[i][0][j]) and (merge_res[1][k] < pareto_res[i][1][j]) and (
                        merge_res[2][k] == pareto_res[i][2][j])):
                    break
                # 非支配解数目+1
                elif k == len(merge_res[0]) - 1:
                    count += 1
        nn[i] = count
    #  计算非支配解占比
    for i in range(num_ag):
        rn[i] = round(nn[i] / len(merge_res[0]), 2)
    return nn, rn


def list2excel(name, list_a):
    # 1.创建excel保存数据
    vis = str(random.randint(1, 1000))  # 避免重名
    excel_path = '.\\save_data\\' + name + vis + '.xls'  # 保存路径
    work_book = xlwt.Workbook(encoding='utf-8')  # 创建一个excel工作表
    sheet = work_book.add_sheet(name)  # 给该工作表命名

    n_comp = len(list_a)  # 算法数量
    n_goal = len(list_a[0])  # 结果的指标数
    crow = 0  # 列系数

    for i in range(n_comp):  # 按算法逐个输出
        n_res = len(list_a[i][0])  # 该算法得到结果个数
        for j in range(n_goal):  # 按指标输出
            for k in range(n_res):  # 按结果数输出
                try:
                    sheet.write(k, i * n_goal + j, str(list_a[i][j][k]))  # 表头
                except Exception:
                    pass
    work_book.save(excel_path)
    print('保存成功')


def station(n_case):  # 算例对应工作站数目
    n_sta = [3, 4, 6, 8, 10, 15, 20, 30]
    return n_sta[n_case]


# 散点图中显示帕累托解集
def show_all_res_pareto(s_pareto_res):
    # 处理数据
    n_algorithm = len(s_pareto_res)  # 算法个数
    x, y, z = [], [], []
    for i in range(n_algorithm):  # 逐一处理每个算法
        n_res = len(s_pareto_res[i][0])  # 该算法内解的个数
        s_x, s_y, s_z = [], [], []
        for j in range(n_res):  # 分别提取三个目标的解
            s_x.append(s_pareto_res[i][0][j])
            s_y.append(s_pareto_res[i][1][j])
            s_z.append(s_pareto_res[i][2][j])
        x.append(s_x)
        y.append(s_y)
        z.append(s_z)
    fig = plt.figure()  # 绘制图片
    ax = fig.add_subplot(111, projection='3d')  # 创建3D坐标
    ax.set_xlabel('COST_Tran')
    ax.set_ylabel('CT')
    ax.set_zlabel('Ave_DT')
    colors = ['r', 'g', 'b', 'y', 'p']  # 设置颜色
    for i in range(n_algorithm):
        ax.scatter(x[i], y[i], z[i], s=20, c=colors[i], depthshade=True)  # 绘制散点
    plt.show()


# 参数实验
def par_set(par):

    par += 1
    dirct_num_a = {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 3, 8: 3, 9: 3}
    dirct_num_b = {1: 1, 2: 2, 3: 3, 4: 1, 5: 2, 6: 3, 7: 1, 8: 2, 9: 3}
    dirct_par_a = {1: 0.05, 2: 0.25, 3: 0.5}  # 三水平参数设置
    dirct_par_b = {1: 0.2, 2: 0.4, 3: 0.6}

    return dirct_par_a[dirct_num_a[par]], dirct_par_b[dirct_num_b[par]]


def main():
    total_nn_rn = []  # 输出nn\rn
    for j in range(9):  # 创建5种算法nn\rn  & 参数设置9组
        total_nn_rn.append([])
        for k in range(2):  # 每种算法保存两个指标
            total_nn_rn[j].append([])
    name = '参数实验'
    for t in range(20):  # 每种算法每种算例重复次数
        s_pareto_res = []  # 收集不同算法求解的结果
        for par in range(9):  # DOE参数水平
            print('参数:', par+1)
            best_res = []
            a, b = par_set(par)
            comp = 2  # 调节对比实验组：共3组
            if comp == 0:
                name = '关键环节验证_' + str(t) + '_'
                n_algorithm = 4  # 三组
                print('关键环节验证实验: ', '第', str(t + 1), '次实验')
            elif comp == 1:
                n_algorithm = 4  # 三组
                name = '与其它现有算法对比_' + str(t) + '_'
                print('与其它现有算法对比实验: ', '第', str(t + 1), '次实验')
            else:
                n_algorithm = 2  # 三组
                name = '参数实验_' + str(t) + '_'
                print('参数实验: ', '第', str(t + 1), '次实验')

            for i in range(0, 1):  # 更换算例
                n_cases = 1  # 求解算例
                total_m, cases_name, data, car_position, num_data, excel_path, work_book = ini_all(n_cases)  # 初始化 excel、工序数据、工厂位置数据
                # digraph(cases_name[n_cases])  # 画出装配产品的有向图
                num_station = station(n_cases)  # 装配环节工作站数目
                car_v, min_n_car, pos_wh, p2p_t, p2c_t, cm, pre_op, car_max_w, total_op_m, m_op = \
                    other.data_preprocessing(data, num_station)  # 数据预处理
                t_run = len(data) * num_station / 3  # 单个算例运行时间
                print('算例' + str(n_cases), '运行时间:', t_run, '秒')
                for exp in range(1, n_algorithm):  # 同组实验中对比算法的数目
                    input_CT = 1.5 * cm  # 初始化-节拍约束
                    set_result, set_res, list_rand = [], [], []  # 初始化
                    set_alb_res, choose_rand, temp, nsga_2 = 0, 0, 0, 0  # 初始化
                    T1 = time.time()  # 获取系统时间
                    end = pow(10, 10)  # 表示一个极大的整数
                    text1_dict_algorithm = {1: '文章算法:学习型VNS', 2: '关键环节实验:装配导向,装配解确定', 3: '关键环节实验:运输导向'}
                    text2_dict_algorithm = {1: 'LVNS', 2: '其它多目标算法:NSGA-2', 3: '其它多目标算法: 标准vns'}
                    text3_dict_algorithm = {1: 'LVNS' }
                    if comp == 0:
                        nsga_2 = 0
                        print(text1_dict_algorithm[exp])
                    elif comp == 1:
                        nsga_2 = 1
                        print(text2_dict_algorithm[exp])
                    else:
                        print(text3_dict_algorithm[exp])
                    while temp < end:
                        temp += 1  # 迭代数累计
                        if exp == 1:  # “装配导向”的LVNS
                            lvns = 1  # 启用学习型vns
                            if temp >= 2:
                                input_CT = input_CT
                                set_result = copy.deepcopy(set_alb_res)
                            set_alb_res, input_CT = alb.vns_alb(a, b, lvns, set_result, input_CT, data, cm, num_station, pre_op)  # 装配优化
                            set_res, set_alb_res = trans.alb_c_sch(a, b, lvns, exp, total_m, num_station, pre_op, cm, set_alb_res, pos_wh, data, p2p_t,
                                                      p2c_t)   # 优化运输
                        elif comp == 0:  # 关键环节验证实验
                            if exp == 2:  # 对比实验: 装配确定不变
                                lvns = 1  # 启用学习型vns
                                if temp >= 2:
                                    input_CT = input_CT
                                    set_result = copy.deepcopy(set_alb_res)
                                set_alb_res, input_CT = alb.alb_3(set_result, input_CT, data, cm, num_station, pre_op)  # 优化装配
                                if temp == 1:
                                    list_rand, choose_rand = trans.choose_ALB_rand(set_alb_res, data)  # 选择一个装配排序并确定不变
                                set_res = trans.dirct_c_sch(nsga_2, lvns, total_m, num_station, pre_op, cm, set_alb_res, pos_wh,
                                                            data, p2p_t,
                                                            p2c_t, list_rand, choose_rand)   # 优化运输

                            elif exp == 3:  # 对比试验：采用正向优化, 验证反向优化的有效性
                                lvns = 1
                                set_res = trans.c_sch(lvns, total_m, num_station, pre_op, cm, pos_wh, data, p2p_t, p2c_t)  # 优化运输+装配
                        elif comp == 1:  # 与其他现有算法对比
                            if exp == 2:  # 对比NSGA-2
                                lvns = 0
                                if temp >= 2:
                                    input_CT = input_CT
                                    set_result = copy.deepcopy(set_alb_res)
                                set_alb_res, input_CT = alb.ga_alb(lvns, set_result, input_CT, data, cm, num_station, pre_op)  # 装配优化(利用交叉变异)  --结果-节拍不够好
                                nsga_2 = 1  # 启用交叉-变异算子
                                set_res = trans.dirct_c_sch(nsga_2, lvns, total_m, num_station, pre_op, cm, set_alb_res, pos_wh,
                                                            data, p2p_t,
                                                            p2c_t, list_rand, choose_rand)   # 优化运输
                            elif exp == 3:  # 对比标准VNS
                                lvns = 0
                                if temp >= 2:
                                    input_CT = input_CT
                                    set_result = copy.deepcopy(set_alb_res)
                                set_alb_res, input_CT = alb.vns_alb(lvns, set_result, input_CT, data, cm, num_station,
                                                                    pre_op)  # 装配优化
                                set_res, set_alb_res = trans.alb_c_sch(lvns, exp, total_m, num_station, pre_op, cm, set_alb_res,
                                                                       pos_wh, data, p2p_t,
                                                                       p2c_t)  # 优化运输
                        new_res = set_res  # 本次迭代解集
                        if temp == 1:  # 首次迭代认为是非支配解集
                            best_res = new_res
                            for k in range(3):
                                best_res.append([9999])
                            best_res = re_pareto2(new_res, best_res)  # 更新帕累托解集
                        else:
                            best_res = re_pareto2(new_res, best_res)  # 更新帕累托解集
                        T2 = time.time()   # 第二次获取系统时间、单位是秒
                        if T2 - T1 >= t_run:  # 是否达到算法终止时间
                            print('迭代次数' + str(temp), '结果:', best_res)
                            break
                s_pareto_res.append(best_res)  # 保存不同算法的帕累托前沿
            # show_all_res_pareto(s_pareto_res)  # 显示不同算法的非支配三维、二维图像

        nn, rn = NN_RN(s_pareto_res)  # 计算不同算法的帕累托占优个数、占优比 & 计算不同参数设置下的占有个数、占优比
        print(nn, rn)
        n_comp = len(nn)  # 对比算法数量
        for j in range(n_comp):
            total_nn_rn[j][0].append(nn[j])
        for j in range(n_comp):
            total_nn_rn[j][1].append(rn[j])
        print(total_nn_rn)

    list2excel(name, total_nn_rn)  # 保存数据到excel


if __name__ == '__main__':  # 程序开始的地方
    main()
