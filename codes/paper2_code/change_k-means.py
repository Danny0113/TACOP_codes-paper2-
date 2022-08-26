import json
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import rgb2hex
from sklearn import cluster
import math


def load_data():
    # 1.工序的加工时间，约束，工厂位置数据，质量
    path = r'.\second_data_cases\LUTZ3.IN2'
    with open(path, 'r') as file:
        data = json.load(file)
    # 2.装配中心位于原点
    car_position = [(0, 0)]
    print('load data over！')
    return data, car_position


def main():
    # 1.读取数据
    data, car_position = load_data()  # 载入数据
    car_maximizes_capacity = 30  # 每辆车载重30
    # 预处理数据
    # get仓库位置
    position_warehouse = []
    for i in range(len(data)):
        position_warehouse.append(data[i][3][0])
    # get 所有工件的总重量和所用最小车辆数量
    m_op = 0
    for i in range(len(data)):
        m_op += data[i][4][0]
    print('m_op: '+str(m_op))
    # 所用最小车辆数量
    n_car = math.ceil(m_op/car_maximizes_capacity)
    print('car_num: '+str(n_car))
    # 2.对仓库的位置进行聚类
    k = n_car  # clusters簇中心的数量
    [centroid, label, inertia] = cluster.k_means(position_warehouse, k)
    # print([centroid, label, inertia])
    # 调颜色
    colors = tuple([(np.random.random(), np.random.random(), np.random.random()) for i in range(n_car)])
    colors = [rgb2hex(x) for x in colors]
    for i in range(len(data)):
        plt.plot(position_warehouse[i][0], position_warehouse[i][1], 'o', color=colors[label[i]])  # 仓库在地图上的位置
    plt.show()


if __name__ == '__main__':  # 程序开始的地方
    main()