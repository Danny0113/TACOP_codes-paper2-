# coding=UTF-8
import math

from pylab import imread,imshow,figure,show,subplot
from numpy import reshape,uint8,flipud
from matplotlib.colors import rgb2hex
from scipy.cluster.vq import vq
from sklearn.cluster import KMeans
import random
import xlwt
from matplotlib import rcParams
import other
import matplotlib.pyplot as mp
import matplotlib.pyplot as plt


def solve_pic():
    img = imread('对象图片.jpg')
    img = img / 255
    # reshaping the pixels matrix
    pixel = reshape(img, (img.shape[0]*img.shape[1], 3))
    choose_c = []
    num = []
    for i in range(100):
        num.append(random.randint(0, len(pixel)))
    for i in range(100):
        choose_c.append([pixel[num[i]]])
    # draw_point(choose_c)
    res_kmean = KMeans(n_clusters=15, random_state=0).fit(pixel)  # six colors will be found
    # quantization
    centroids = res_kmean.cluster_centers_
    draw_point(centroids)
    qnt, _ = vq(pixel, centroids)

    # reshaping the result of the quantization
    centers_idx = reshape(qnt, (img.shape[0], img.shape[1]))
    clustered = centroids[centers_idx]

    figure(1)
    subplot(211)
    imshow(flipud(img))
    subplot(212)
    imshow(flipud(clustered))
    show()


def draw_point(centroids):
    X = []
    Y = []
    Z = []
    try:
        for i in range(len(centroids)):
            X.append(centroids[i][0])
        for i in range(len(centroids)):
            Y.append(centroids[i][1])
        for i in range(len(centroids)):
            Z.append(centroids[i][2])
    except IndexError:
        pass
    # 三维散点图
    config = {
        "font.family": 'Times New Roman',  # 设置字体类型
        "font.size": 10,
        #     "mathtext.fontset":'stix',
    }
    rcParams.update(config)
    mp.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=1, wspace=0.8)
    mp.figure("3D Scatter", facecolor="none")
    ax3d = mp.gca(projection="3d")  # 创建三维坐标
    ax3d.set_xlabel('x', fontsize=20, labelpad=10)
    ax3d.set_ylabel('y', fontsize=20, labelpad=10)
    ax3d.set_zlabel('z', fontsize=20, labelpad=10)
    mp.tick_params(labelsize=20)
    '''
    s：大小固定设置为64
    c:通过arctan函数随机生成一个数列，映射到coloarmap的颜色上
    makrer：散点标记类型设置为‘o’对应圆圈
    aplpha：透明度设置为0.5，重合部分可以正常显示
    linewidths：为散点标记的边界宽度
    edgecolors：散点边界的点色，“w”为白色
    '''
    for i in range(len(centroids)):
        colors = [X[i], Y[i], Z[i]]
        # plt.scatter(X[i], Y[i], s=100, c=colors, marker='o')
        label = '('+str(math.ceil(X[i]*255)) +','+ str(math.ceil(Y[i]*255)) +','+ str(math.ceil(Z[i]*255))+')'
        ax3d.text(X[i]*255-20, Y[i]*255, Z[i]*255+5, label)
        ax3d.scatter(X[i]*255, Y[i]*255, Z[i]*255, s=100, c=colors, marker='o')

    # plt.xlim(0, 1)
    # plt.ylim(0, 1)
    # savefig('../figures/scatter_ex.png',dpi=48)
    plt.show()

if __name__ == '__main__':
    solve_pic()