from matplotlib import pyplot as plt


def draw_points(total_lines, total_den):
    """
    :param total_lines:  总路程 列表
    :param total_den:   总滞留时间 列表
    :return:
    """
    for i in range(len(total_lines)):
        x = total_lines[i]
        y = total_den[i]
        plt.plot(x, y, 'o')  # 仓库在地图上的位置
    plt.show()
