import random

import xlwt


def cre_data():
    job = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 100, 100, 100, 100, 100]
    m = [3, 5, 10, 10, 15, 20, 20, 25, 30, 30, 10, 20, 30, 40, 50]
    # 数据集
    matr = []
    for k in range(15):
        # 工件数
        num_job = job[k]
        num_m = m[k]
        # 增加一个数据集
        matr.append([])
        for i in range(num_job):
            # 增加工件维度
            matr[k].append([])
            for j in range(num_m):
                matr[k][i].append([])
                tem = random.randint(30, 100)
                matr[k][i][j] = tem

    for i in range(15):
        excel_path = '.\\save_data\\' + str(job[i]) + '_' + str(m[i]) + '.xls'  # 保存路径
        work_book = xlwt.Workbook(encoding='utf-8')  # 创建一个excel工作表
        sheet = work_book.add_sheet(str(job[i]) + '_' + str(m[i]))  # 给该工作表命名
        for j in range(job[i]):
            for k in range(m[i]):
                sheet.write(j, k, matr[i][j][k])
        work_book.save(excel_path)

if __name__ == '__main__':
    cre_data()
