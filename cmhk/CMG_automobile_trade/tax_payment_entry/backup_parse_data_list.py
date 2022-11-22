#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import datetime
import json
import os
import pandas as pd
import ntpath

# 入参
home_path = r'D:/RPA/缴税/数据源'
excel_list = os.listdir(r'D:/RPA/缴税/数据源')

# start

# 将文件列表组合成为绝对地址列表
abs_file_list = [os.path.join(home_path, excel_name) for excel_name in excel_list]

data_dict = {}
for file_url in abs_file_list:
    # 获取文件名作为KEY
    file_key = ntpath.basename(file_url)
    table = pd.read_excel(file_url, header=1)
    # 对日期进行处理
    table_dict = table.to_dict()
    time_dict = table_dict.get('交税日期')
    for time_s in time_dict:
        time_dict.update({time_s: time_dict.get(time_s).strftime('%Y-%m-%d')})
    table_dict.update({'交税日期': time_dict})
    data_dict.setdefault(file_key, table_dict)

data_print = json.dumps(data_dict, indent=4, ensure_ascii=False, sort_keys=False, separators=(',', ':'))
log_name = datetime.datetime.now().strftime('%Y%m%d.%H%M%S')
with open(r'D:/RPA/缴税/日志/解析清单.%s.json' % log_name, 'w', encoding='utf-8') as f:
    f.write(data_print)

# end
print(data_print)
