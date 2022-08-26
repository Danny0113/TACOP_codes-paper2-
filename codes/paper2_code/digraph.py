import networkx as nx
import matplotlib.pyplot as plt

import other


# 载入数据
def digraph(case_name):
    path = '.\\second_data_cases\\'+case_name+'.IN2'
    data, car_position = other.load_data(path)

    # 创建什么都没有的空图
    g = nx.DiGraph()

    for i in range(len(data)):
        for j in range(len(data[i][2])):
            g.add_edge(i+1, data[i][2][j])
    pos = nx.circular_layout(g)          # 生成圆形节点布局

    nx.draw(g, pos, with_labels=True)
    plt.show()
