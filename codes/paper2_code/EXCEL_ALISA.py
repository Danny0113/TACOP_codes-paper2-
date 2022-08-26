from random import random

import xlwt
from xlutils.copy import copy
import xlrd

book = xlrd.open_workbook('D:\集成调度问题\物流+装配\代码\Alisa\攀枝花分户情况统计表.xlsx')

sheet1 = book.sheets()[4]

nrows = sheet1.nrows

print('表格总行数',nrows)

ncols = sheet1.ncols

print('表格总列数',ncols)

row3_values = sheet1.row_values(2)

print('第3行值',row3_values)

col3_values = sheet1.col_values(2)

print('第3列值',col3_values)

cell_3_3 = sheet1.cell(2,2).value

print('第3行第3列的单元格的值：',cell_3_3)

list2 = []
# 总人数1261

first_num =sheet1.cell(1,6).value
hu_num = 0
for k in range(1, 1262):
    # 如果相等则为一组
    comp = sheet1.cell(k, 6).value
    # 如果是一户，编号相同
    if comp == first_num:
        # 生日
        birth = sheet1.cell(k, 3).value
        # 性别
        sex = sheet1.cell(k, 2).value
        if birth <= 37948.0 and sex == '男':
            hu_num += 1
            pass
        # print(sheet1.cell(k,6))
        # 判断男是否18
        # 累计
    #     下一户的第一个编号
    else:
        list2.append(hu_num)
        print('----')
        hu_num = 0
        # 生日
        birth = sheet1.cell(k, 3).value
        # 性别
        sex = sheet1.cell(k, 2).value
        if birth <= 37948.0 and sex == '男':
            hu_num += 1
        # 该户编号
        first_num = sheet1.cell(k, 6).value


# 1.创建excel保存数据
name = '关键环节验证'
vis = '1'
excel_path = '.\\save_data\\' + name + vis + '.xls'  # 保存路径
work_book = xlwt.Workbook(encoding='utf-8')  # 创建一个excel工作表
sheet = work_book.add_sheet(name)  # 给该工作表命名

# for i in range(2):
#     if i == 1:
#         count = 3
#     else:
#         count = 0
#     for j in range(len(list_a[i])):
#         for k in range(n_comp):
#             # 添加数据
#             try:
#                 sheet.write(j, k + count, str(list_a[i][j][k]))  # 表头
#             except IndexError:
#                 print('输出错误！')
first_num = 0
hu_num = 0
num = 0
for k in range(1, 1262):
    # 如果相等则为一组
    comp = sheet1.cell(k, 6).value

    if comp != first_num:
        try:
            n = list2[num]-1
            if n <= 1:
                n = 1
            sheet.write(k,  7, str(n))
            if n == 1:
                sheet.write(k, 8, '无')
            else:
                sheet.write(k, 8, str(n-1))
        except IndexError:
            pass
        num += 1
        first_num = comp
    else:
        pass

work_book.save(excel_path)
print('保存成功')


# # 将户数写入excel
# # 加载已存在的xls
# old_workbook = xlrd.open_workbook(r'D:\集成调度问题\物流+装配\代码\Alisa\处理后.xlsx')
#
# # 将已存在的excel拷贝进新的excel
# new_workbook = copy(old_workbook)
#
# # 获取sheet
# new_worksheet = new_workbook.get_sheet(4)
#
# # 写入数据
# # cow = 7  # 已存在文件中的数据行数
# # row = 1  # 第一行
# # for data in data_set:
# #     new_worksheet.write(cow, 0, data['href'])
# # new_worksheet.write(cow, 1, data['star'])
#
#
# first_num = 0
# hu_num = 0
# num = 0
# for k in range(1, 1262):
#     # 如果相等则为一组
#     comp = sheet1.cell(k, 6).value
#
#     if comp != first_num:
#         try:
#             new_worksheet.write(k, 7, list2[num]-1)
#         except IndexError:
#             pass
#         num += 1
#         first_num = comp
#     else:
#         pass
#
# # 将新写入的数据保存
# new_workbook.save(r'D:\集成调度问题\物流+装配\代码\Alisa\处理后.xlsx')
print('结束')


