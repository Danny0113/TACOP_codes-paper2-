import random
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import rgb2hex
from sklearn import cluster
from digraph import digraph
import copy


#  在车辆载重约束下的工厂地址聚类算法
def my_cluster(pos_wh, k, data, car_max_w):
    """
    :param pos_wh:配件位置
    :param k: 簇数即车辆数
    :param data: 包含配件重
    :return: 配件被分配的车辆编号
    :car_max_w: 车辆最大载重
    """
    n_car = k
    cluster_adj(n_car, pos_wh, data, car_max_w)

    return


# 仅仓库位置进行聚类 - 每次聚类的结果不太一样 -因为 本来聚类就是个np问题
def c_cluster(n_car, position_warehouse, data):
    k = n_car  # clusters簇中心的数量
    [centroid, label, inertia] = cluster.k_means(position_warehouse, k)
    # 调颜色
    # colors = tuple([(np.random.random(), np.random.random(), np.random.random()) for i in range(n_car + 1)])
    # colors = [rgb2hex(x) for x in colors]
    # for i in range(len(data)):
    #     plt.plot(position_warehouse[i][0], position_warehouse[i][1], 'o', color=colors[label[i]])  # 仓库在地图上的位置
    # plt.plot(50, 50, 'x', color='black')
    # plt.show()
    # plt.close('all')

    return label


# 在车辆容量约束下, 改进k-mean算法
def cluster_adj(n_car, position_warehouse, data, car_max_w):
    k = n_car  # clusters簇中心的数量
    # k-mean聚类
    [centroid, label, inertia] = cluster.k_means(position_warehouse, k)
    # 计算每一簇的总体积
    v_clus = []
    # 记录超出与否、记录总体积、工厂编号、几何中心
    for i in range(1, 6):
        v_clus.append([])
    for i in range(k):
        v_clus[0].append(0)
        v_clus[1].append(0)
    for i in range(k):
        v_clus[2].append([])
        v_clus[3].append([])
        v_clus[4].append([])
    for i in range(len(data)):
        # 累计簇的体积
        v_clus[1][label[i]] = v_clus[1][label[i]] + data[4][0]
        # 累计簇内的工序集
        v_clus[2][label[i]-1].append(i)
        # 初始化簇内工序与中心的距离为 0
        v_clus[4][label[i]-1].append(0)
    # 划分为两种簇, 超出体积与未超出体积
    for i in range(k):
        if v_clus[1][i] > car_max_w:
            v_clus[0][i] = 1
        else:
            pass
    # 计算所有簇的几何中心
    for i in range(k):
        x = 0
        y = 0
        num_op = len(v_clus[2][i])
        for j in range(num_op):
            op = v_clus[2][i][j]
            x += data[op][3][0][0]
            y += data[op][3][0][1]
        x = round(x / num_op, 2)
        y = round(y / num_op, 2)
        v_clus[3][i] = (x, y)
        # 计算工厂距离各自簇的直线距离
        for j in range(num_op):
            op = v_clus[2][i][j]
            x += data[op][3][0][0]
            y += data[op][3][0][1]
            try:
                v_clus[4][i][j] = round(pow(pow(x - v_clus[3][i][0], 2) + pow(y - v_clus[3][i][1], 2), 0.5), 2)
            except IndexError:
                pass
    # 计算超出体积簇边缘的工厂与哪一个未超出簇的几何中心最近则将其移入
    for i in range(k):
        # 体积超标
        if v_clus[0][i] == 1:
            # 指导体积达标
            while v_clus[0][i] == 1:
                # 计算距离几何中心最远的工厂
                num_op = len(v_clus[4][i])
                dis_max = v_clus[4][i][0]
                op_max = v_clus[2][i][0]
                for j in range(num_op):
                    if v_clus[4][i][j] > dis_max:
                        dis_max = v_clus[4][i][j]
                        op_max = v_clus[2][i][j]

                # 计算并找到最近邻临近可容簇, 将其移入
                if i != 0:
                    j = 0
                else:
                    j = 1
                to_cluster = j
                dis_min = round(
                    pow(pow(data[op_max][3][0][0] - v_clus[3][j][0], 2) + pow(data[op_max][3][0][1] - v_clus[3][j][1],
                                                                                  2), 0.5), 2)
                for j in range(k):
                    if j == i:
                        pass
                    else:
                        dis = round(
                            pow(pow(data[op_max][3][0][0] - v_clus[3][j][0], 2) + pow(
                                data[op_max][3][0][1] - v_clus[3][j][1], 2), 0.5), 2)
                        if dis < dis_min:
                            to_cluster = j
                # 移入并计算新簇的体积、族内工序、簇的几何中心

                # 计算旧簇的体积、是否超出体积、簇内工序、簇的几何中心
        else:
            pass
    # 得到所有未超出体积的簇
    # 计算匹配度最高的装配排序
    # 调整排序使CT不变且匹配度提高
    # 调整簇内边缘工厂使匹配度提高

    # 显示最终的簇划分
    colors = tuple([(np.random.random(), np.random.random(), np.random.random()) for i in range(n_car + 1)])
    colors = [rgb2hex(x) for x in colors]
    for i in range(len(data)):
        plt.plot(position_warehouse[i][0], position_warehouse[i][1], 'o', color=colors[label[i]])  # 仓库在地图上的位置
    plt.plot(50, 50, 'x', color='black')
    # 簇的几何中心
    for i in range(k):
        plt.plot(v_clus[3][i][0], v_clus[3][i][1], 'x', color='red')

    plt.show()
    return label




