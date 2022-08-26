from pareto2 import simple_cull, dominates


def re_pareto2(new_res, old_res):
    len_new = len(new_res[0])
    for i in range(len_new):
        a = new_res[0][i]
        b = new_res[1][i]
        c = new_res[2][i]
        old_res[0].append(a)
        old_res[1].append(b)
        old_res[2].append(c)
    input_points = []
    for i in range(len(old_res[0])):
        input_points.append([])
        for j in range(3):
            input_points[i].append(old_res[j][i])
    paretoPoints, dominatedPoints = simple_cull(input_points, dominates)
    paretoPoints = list(paretoPoints)
    best_res = []
    for i in range(3):
        best_res.append([])
    for i in range(len(paretoPoints)):
        best_res[0].append(paretoPoints[i][0])
        best_res[1].append(paretoPoints[i][1])
        best_res[2].append(paretoPoints[i][2])
    min_ct = min(best_res[1])  # 找到解集中最小节拍
    new_best_res = []
    for i in range(3):
        new_best_res.append([])
    for i in range(len(best_res[0])):
        if min_ct == best_res[1][i]:  # 将节拍值最优的拿出来\差的拿走
            new_best_res[0].append(best_res[0][i])
            new_best_res[1].append(best_res[1][i])
            new_best_res[2].append(best_res[2][i])

    return new_best_res

def re_pareto(new_res, old_res):
    '''
    新解的某一个指标大于所有即可添加
    旧中某个解
    :param new_res:
    :param old_res:
    :return:
    '''
    # 添加解集
    len_old = len(old_res[0])
    len_new = len(new_res[0])
    # for i in range(len_new):
    #     a = new_res[0][i]
    #     b = new_res[1][i]
    #     c = new_res[2][i]
    #     for j in range(len_old):
    #         x = old_res[0][j]
    #         y = old_res[1][j]
    #         z = old_res[2][j]
    #         # 添加新解
    #         if (a < x) and (b < y) and (c < z):
    #             old_res[0].append(a)
    #             old_res[1].append(b)
    #             old_res[2].append(c)
    #             break
    # 新解全部添加
    for i in range(len_new):
        a = new_res[0][i]
        b = new_res[1][i]
        c = new_res[2][i]
        old_res[0].append(a)
        old_res[1].append(b)
        old_res[2].append(c)
    # 剔除旧解集
    del_set = []
    len_old = len(old_res[0])
    for i in range(len_old):
        a = old_res[0][i]
        b = old_res[1][i]
        c = old_res[2][i]
        for j in range(len_old):
            if j != i:
                x = old_res[0][j]
                y = old_res[1][j]
                z = old_res[2][j]
                if (a >= x) and (b >= y) and (c >= z):
                    del_set.append(i)
                    break
    #   根据下标剔除
    try:
        for i in del_set:
            del old_res[0][i]
            del old_res[1][i]
            del old_res[2][i]
        best_res = old_res
    except IndexError:
        pass
    return best_res






