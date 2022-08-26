from other import data_prep_alb


def evaluate_2(arrive_time, this_ct, num_s):
    total_t = min(arrive_time) + this_ct * num_s
    return total_t


def calculate_detention_time(arrive_time, this_station_op, this_ct, data, cm):
    # print('载入数据...')
    # print(arrive_time)
    # print(this_station_op)
    # print('载入数据完毕')
    # print('处理数据...')
    # print('配件的开始装配时间：')
    op_begin_t = []
    for i in range(len(data)):
        op_begin_t.append([])

    for i in range(len(this_station_op)):  # 工作站数目
        for k in range(len(this_station_op[i][0])):  # i工作站内的配件数目
            op_begin_t[this_station_op[i][0][k] - 1] = this_ct*i + this_station_op[i][1][k] - data[this_station_op[i][0][k] - 1][1]
    # print(op_begin_t)
    # print('抵达时间：')
    # print(arrive_time)
    # print('首个配件抵达即开始计算滞留时间')
    # print('各配件滞留时间：')
    wt_time, ct = data_prep_alb(arrive_time, cm, data)  # 各配件抵达时间-首个配件抵达时间、初始节拍
    detention_time = []
    for i in range(len(data)):
        detention_time.append([])
    for i in range(len(data)):
        detention_time[i] = round(op_begin_t[i] - wt_time[i], 2)
        if detention_time[i] < -0.1:
            print('滞留时间计算错误！！！！！！')
    # print(detention_time)
    # print('所有配件滞留时间之和与装配总时间的比值：')
    for i in range(len(data)):
        sum_detention = sum(detention_time)

    ratio_sum_detention_mct = round(sum_detention / (len(this_station_op)*this_ct), 2)
    # print(ratio_sum_detention_mct)
    # print('配件的平均滞留时间：')
    average_detention = sum_detention / len(data)
    # print(average_detention)
    # print('滞留时间计算完毕！')

    return average_detention
