import math

from matplotlib import pyplot as plt
import numpy as np
from matplotlib.colors import rgb2hex
from matplotlib import rcParams


def get_gantt(station_op, m_station, data, ct):
    """
    装配站工序的分配及完成时间
    装配站数目
    """
    config = {
        "font.family": 'Times New Roman',  # 设置字体类型
        "font.size": 80,
        #     "mathtext.fontset":'stix',
    }
    rcParams.update(config)
    # 创建颜色(通用)
    colors = tuple(
        [(np.random.random(), np.random.random(), np.random.random()) for i in range(len(data))])
    colors = [rgb2hex(x) for x in colors]
    for j in range(m_station):  # j工作站编号
        for i in range(len(station_op[j][0])):
            try:
                plt.text(station_op[j][1][i] - data[station_op[j][0][i]-1][1] + data[station_op[j][0][i]-1][1] / 4, j+1, '%s' % (str(station_op[j][0][i])), fontsize=25)
                plt.barh(j + 1, data[station_op[j][0][i]-1][1], left=(station_op[j][1][i] - data[station_op[j][0][i]-1][1]))
            except TypeError:
                pass
    plt.yticks(np.arange(0, m_station + 2, 1), fontsize=20)
    plt.xticks(np.arange(0, ct*1.2, 2), fontsize=20)
    plt.show()
    a = 1
