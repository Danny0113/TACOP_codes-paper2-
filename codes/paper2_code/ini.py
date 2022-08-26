import random

import xlwt
from matplotlib import rcParams

import other
import matplotlib.pyplot as mp
import matplotlib.pyplot as plt


def initial():
    # 三维散点图
    config = {
        "font.family": 'Times New Roman',  # 设置字体类型
        # "font.size": 80,
        #     "mathtext.fontset":'stix',
    }
    rcParams.update(config)

    ax3d = mp.gca(projection="3d")  # 创建三维坐标
    ax3d.set_xlabel('Cost_Trans', fontsize=20, labelpad=10)
    ax3d.set_ylabel('CT', fontsize=20, labelpad=10)
    ax3d.set_zlabel('Ave_Det', fontsize=20, labelpad=10)
    mp.tick_params(labelsize=20)
    # mp.yticks([])  # 不显示Y轴刻度值
    return ax3d, mp


def ini_all(n_cases):
    cases_name = ['JACKSON', 'JAESCHKE', 'BUXEY', 'KILBRID', 'LUTZ1', 'LUTZ2']
    data_name = cases_name[n_cases] + '.IN2'  # 数据名
    vis = random.uniform(1, 100)  # 保存的版本(随机数方式区别)
    vis = str(vis)

    # 1.创建excel保存数据
    excel_path = '.\\save_data\\' + data_name + vis + '.xls'  # 保存路径
    work_book = xlwt.Workbook(encoding='utf-8')  # 创建一个excel工作表
    sheet = work_book.add_sheet(data_name + vis)  # 给该工作表命名
    num_data = 1  # Excel的行递增
    sheet.write(0, 0, '车辆数')  # 表头
    sheet.write(0, 1, '工作站数')
    sheet.write(0, 2, '运输成本')
    sheet.write(0, 3, '节拍值')
    sheet.write(0, 4, '理想节拍')
    sheet.write(0, 5, '因运输环节而产生的装配空闲时间')
    sheet.write(0, 6, '配件在装配中心的平均滞留时间')

    # 2.读取数据 & 数据预处理
    path = '.\\second_data_cases\\' + cases_name[n_cases] + '.IN2'
    data, car_position = other.load_data(path)  # 载入数据 配件相关信息、仓库位置信息

    # 计算工件总重量
    total_m = 0
    for i in range(len(data)):
        total_m += data[i][4][0]
    # 并行装配线数目 10条
    total_m = total_m*10

    return total_m, cases_name, data, car_position, num_data, excel_path, work_book
