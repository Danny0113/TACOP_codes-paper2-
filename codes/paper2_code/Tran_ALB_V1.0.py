import random
import xlwt
import time
from datetime import datetime

import alb
import my_cluster
import gantt
import other
import transport
import evaluate
from digraph import digraph


def main():
    print('正在求解...')
    cases_name = ['BUXEY', 'JACKSON', 'JAESCHKE', 'KILBRID', 'LUTZ1', 'LUTZ2', 'LUTZ3', 'SCHOLL']
    n_cases = 6  # 第六个算例
    # digraph(cases_name[n_cases])                #  画出算例的工序装配约束有向图
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
    for num_station in range(5, 6):  # 装配站数目 先跑一组装配站
        # 数据预处理
        # 返回：需要的最低车辆数、配件仓位置、配件仓到配件仓的距离、配件仓到装配中心的距离、理想节拍、配件前序、车辆容积、配件总重量
        n_car_one_all, position_warehouse, wh_to_wh, wh_to_center, cm, pre_op, car_max_w, total_op_m = \
            other.data_preprocessing(data, num_station)
        for car in range(13, 14):  # 车辆数
            n_car = car  # 车辆增加
            # 3.仅对仓库的位置进行聚类(不考虑车辆载重，不考虑各车辆运回时间均匀性)
            # label = cluster.warehouse_clustering_1(n_car, position_warehouse, data)
            # 对考虑车辆载重 随机成簇
            # label = my_cluster.warehouse_clustering_2(n_car, position_warehouse, data, car_max_w)
            # 按照有向图，装车（不考虑配件位置）
            min_total_wt = 0  # 因运输产生的装配等待时间
            min_this_ct = 0  # 节拍
            min_average_detention = 0  # 平均滞留时间
            min_trans_cost = 0  # 运输成本
            for i in range(0, 10):  # 重复十次工序分组过程
                # 对配件进行聚类- 聚到一辆车上，所以考虑车辆出发的先后才有意义，所以滞留时间为一个评价指标
                # 返回：哪几个配件为一辆车、需要的总运输次数(辆)、每辆车运输的配件编号及重量
                label, all_cars_need, cars_need_op_num_weight = my_cluster.warehouse_clustering_3(n_car,
                                                                                                  position_warehouse,
                                                                                                  data, car_max_w,
                                                                                                  cases_name[
                                                                                                      n_cases],
                                                                                                  pre_op,
                                                                                                  total_op_m)
                # 4.车辆运输阶段（VRP）
                # arrive_time, trans_cost = transport.transport_1(label, n_car, wh_to_wh, wh_to_center)
                # 车辆内部的vrp问题优化
                # arrive_time, trans_cost = transport.transport_2(label, n_car, wh_to_wh, wh_to_center)
                # 有限的 车辆 反复调度（批次）
                # 返回：车辆抵达时间、运输成本
                arrive_time, trans_cost = transport.transport_3(label, all_cars_need, cars_need_op_num_weight,
                                                                n_car,
                                                                wh_to_wh, wh_to_center)
                # 5.装配线平衡(随机方式,仅考虑合理性,即满足所有基本约束)
                this_ct, this_station_op, total_wt = alb.alb_1(arrive_time, data, cm, num_station, pre_op)
                #  计算配件平均滞留时间
                average_detention = evaluate.calculate_detention_time(arrive_time, this_station_op, this_ct, data,
                                                                      cm)
                # 启发式算法求解装配线平衡
                # this_ct, this_station_op = alb.alb_2(arrive_time, data, cm, num_station, pre_op)
                # gantt.get_gantt(this_station_op, num_station, data, this_ct)
                # 6.评价该运输+装配方案
                # this_cost = evaluate(n_car, arrive_time, this_ct)
                this_cost = evaluate.evaluate_2(arrive_time, this_ct, num_station)  # 不对的！
                if this_ct < min_this_ct or min_this_ct == 0:
                    min_total_wt = total_wt  # 因运输产生的装配等待时间
                    min_this_ct = this_ct  # 节拍
                    min_average_detention = average_detention  # 平均滞留时间
                    min_trans_cost = trans_cost
                    min_this_station_op = this_station_op

            print('车辆数量: %d(%d), 工作站数目:%d, 运输成本: %.2f, 节拍: %d(CM: %.2f), 运输产生的装配空闲时间：%.2f, '
                  '下线时间(两阶段之和)：%.2f, 配件平均滞留时间:%d '
                  % (n_car, n_car_one_all, num_station, min_trans_cost, min_this_ct, cm,
                     min_total_wt, this_cost, min_average_detention))
            gantt.get_gantt(min_this_station_op, num_station, data, min_this_ct)
            # save_data(n_car, num_station, trans_cost, this_ct, cm, num_data, data_name, sheet)
            # 保存数据到excel
            i = num_data
            sheet.write(i, 0, int(n_car))
            sheet.write(i, 1, int(num_station))
            sheet.write(i, 2, float(min_trans_cost))
            sheet.write(i, 3, int(min_this_ct))
            sheet.write(i, 4, int(cm))
            sheet.write(i, 5, float(min_total_wt))
            sheet.write(i, 6, float(min_average_detention))

            num_data += 1
    work_book.save(excel_path)


if __name__ == '__main__':  # 程序开始的地方
    main()
