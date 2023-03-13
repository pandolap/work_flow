#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import pandas as pd
import os

# 入参
task_list_file = r'D:\RPA\申报数据统计\2022-10-10_2022-10-16\报关数据_含海关编号.csv'
task_amount_file = ''
config_dict = {}
task_dir = ''
start_time = ''
end_time = ''

# start
try:
    df = pd.read_csv(task_list_file, dtype={'海关编号': str})
    task_flags = df['进出口标志'].value_counts()
    r_export_count = int(task_flags.get('出口', 0))
    r_import_count = int(task_flags.get('进口', 0))
    with open(task_amount_file, 'r', encoding='utf-8-sig') as f:
        task_amount = f.read().strip().split('\t')
        t_export_count = int(task_amount[0])
        t_import_count = int(task_amount[1])
except Exception as e:
    raise Exception('程序异常-读取报关业务统计数据异常')

# 比较两个页面的记录数数是否相等
flag = True
if r_export_count == t_export_count and r_import_count == t_import_count:
    flag = False

# 输出的excel
result_datatable = df[list(df.columns)[:-1]].copy()
if flag:
    result_datatable.iloc[-1, 0] = '本次报关业务统计数量与报关数据查询结果不一致，请留意！'

# 模板文件位置
home_dir = config_dict.get('home_dir')
template_file = os.path.join(home_dir, '单一窗口海关数据列表导出模板.xlsx')

# 输出文件位置
output_file = os.path.join(task_dir, '单一窗口海关数据列表%s_%s.xlsx' % (start_time, end_time))

content = '''
Dear 业务老师，
\n\t汽贸单证中心RPA流程-申报数据统计运行结束，结果请查看附件。
\n此次任务查询数据时间为:%sTo%s\n 
其中，报关业务统计数量为: 出口：%s；进口：%s\n
报关数据查询含海关编号的数据量为: 出口：%s；进口：%s\n
''' % (start_time, end_time, t_export_count, t_import_count, r_export_count, r_import_count)

if flag:
    content += '本次报关业务统计数量与报关数据查询结果不一致，请留意！'
else:
    content += '本次报关业务统计数量与报关数据查询结果一致'
# end
