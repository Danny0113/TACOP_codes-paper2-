import random
import numpy as np
import matplotlib.pyplot as plt

# Fixing random state for reproducibility
# np.random.seed(19680801)
# N = 50
# x = np.array([5])
# y = np.array([5])
# colors = np.random.rand(50)
# area = 30  # 0 to 15 point radii
#
# plt.scatter(x, y, s=area, c=colors, alpha=0.5)
# plt.show()


def main():
    # 1 将仓库设置在【10，10】公里的范围内的区域，装配中心位于原点
    position = []
    for i in range(1, 10):
        x = random.randint(-5, 5)
        y = random.randint(-5, 5)
        position.append((x, y))
        print(position[i-1])
        plt.plot(x, y, 'o')  # 仓库在地图上的位置
    plt.show()


if __name__ == '__main__':
    main()

