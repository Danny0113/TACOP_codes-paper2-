import matplotlib.pyplot as plt

#解决中文显示问题
# plt.rcParams['font.sans-serif'] = ['SimHei']
# plt.rcParams['axes.unicode_minus'] = False
plt.rcParams["font.family"] = ['Times New Roman']

# 这是一个集成调度的实例
factory = []
assembly_pos = (31.29, 102.98)
factory_pos = [(33.61, 103.28), (28.49, 105.29), (34.29, 100.51), (30.09, 101.62), (35.99, 102.49), (30.49, 99.61),
               (28.55, 97.45), (27.56, 102.59), (26.08, 105.62)]

x, y = [], []
for i in range(len(factory_pos)):
    x.append(factory_pos[i][0])
    y.append(factory_pos[i][1])
# 绘制散点
p1 = plt.scatter(assembly_pos[0], assembly_pos[1], marker='o', color='g', label='装配厂', s=50)

p2 = plt.scatter(x, y, marker='x', color='b', label='配件厂', s=50)

plt.tick_params(labelsize=20)

# plt.legend(loc='upper right')
plt.show()
