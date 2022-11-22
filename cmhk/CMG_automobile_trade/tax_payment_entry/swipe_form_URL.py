#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# 入参
import os

data_list = os.listdir(r'D:/RPA/缴税/数据源')

# start
excel_list = []
for data in data_list:
    if data.endswith('.xls') or data.endswith('.xlsx'):
        excel_list.append(data)
excel_list = list(set(excel_list))
# end

print(excel_list)
