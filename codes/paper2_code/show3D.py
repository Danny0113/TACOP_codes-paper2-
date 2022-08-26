from scipy.interpolate import griddata

import numpy as np

import matplotlib.pyplot as plt

from matplotlib import cm

from mpl_toolkits.mplot3d import Axes3D
"""
    绘制三维散点图
"""
import numpy as np
import matplotlib.pyplot as mp
from mpl_toolkits.mplot3d import axes3d


def show_result_3D(set_res, set_color):
    # 1.生成数据
    # n = 200
    # x = np.random.normal(0, 1, n)
    # y = np.random.normal(0, 1, n)
    # z = np.random.normal(0, 1, n)
    # d = np.sqrt(x ** 2 + y ** 2 + z ** 2) # 距离

    # 2.绘制图片
    # mp.subplots_adjust(left=0.2, wspace=0.8, top=0.8)  # 位置调整
    mp.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=1, wspace=0.8)
    mp.figure("3D Scatter", facecolor="lightgray")
    ax3d = mp.gca(projection="3d")  # 创建三维坐标

    # mp.title('标题', fontsize=20)
    ax3d.set_xlabel('c_tran', fontsize=14)
    ax3d.set_ylabel('ct', fontsize=14)
    ax3d.set_zlabel('ave_det', fontsize=14)
    mp.tick_params(labelsize=10)

    # ax3d.scatter(x, y, z, s=20, cmap="jet", marker="o")
    for i in range(len(set_res[0])):
        ax3d.scatter(set_res[0][i], set_res[1][i], set_res[2][i], s=20, c=set_color, marker="o", )
    return


def show_sapce():
    x=np.asarray([3,5,9])

    y=np.asarray([3,3,3])

    z=np.asarray([3,2,4])

    # x = np.random.random(100)

    xi=np.linspace(min(x), max(x),50)

    #print xi

    yi=np.linspace(min(y),max(y),50)

    X,Y= np.meshgrid(xi,yi)

    Z = np.nan_to_num(griddata((x,y), z, (X, Y), method='cubic'))

    fig = plt.figure()

    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(x, y, z)

    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm,

    linewidth=0, antialiased=False, alpha=0.4)

    plt.show()


if __name__ == '__main__':
    show_sapce()
