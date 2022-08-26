def startwith(start: int, mgraph: list) -> list:
    # 开始节点
    passed = [start]
    # 未遍历结点
    nopass = [x for x in range(len(mgraph)) if x != start]
    # 初始距离
    dis = mgraph[start]
    # 抵达每个点需要经过的点
    pass_point = []
    for x in range(len(mgraph)):
        pass_point.append([start])
    # 遍历所有nopass
    while len(nopass):
        idx = nopass[0]
        for i in nopass:
            if dis[i] < dis[idx]:
                idx = i

        nopass.remove(idx)
        passed.append(idx)

        for i in nopass:
            if dis[idx] + mgraph[idx][i] < dis[i]:
                dis[i] = dis[idx] + mgraph[idx][i]
                pass_point[i].append(idx)

    return [pass_point, dis]


# 求最短路径
def min_dis():
    inf = 10086
    mgraph = [[0, 1, 12, inf, inf, inf],
              [inf, 0, 9, 3, inf, inf],
              [inf, inf, 0, inf, 5, inf],
              [inf, inf, 4, 0, 13, 15],
              [inf, inf, inf, inf, 0, 4],
              [inf, inf, inf, inf, inf, 0]]

    result = startwith(0, mgraph)
    print(result)


if __name__ == '__main__':
    min_dis()

