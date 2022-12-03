#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Description 筛选日期列表
import re
import os
import decimal
import pandas as pd
from win32com import client
from datetime import datetime

# ARGS!>
in_file_path = r"C:\RPA\招商_招投标中心_交易明细导入导出\output\20221205\old_detail\银行账户交易明细20221205144751.xlsx"


# START:>

def handle_excel_fmt(file_path):
    """
    由于从ERP系统中导出的表格文件是Apache POI生成的没有格式信息，所以需要进行一次保存操作
    :param file_path: 文件地址
    """
    app = client.gencache.EnsureDispatch('Excel.Application')
    app.Visible = False
    wb = app.Workbooks.Open(file_path)
    wb.Save()
    wb.Close()
    # 关闭文件
    app.Quit()


def check_row(row):
    summary = getattr(row, "摘要")
    if re.search(u"^招行", str(summary)):
        summary = summary[2:]
        tmp_list = summary.split("/")
        if len(tmp_list) == 3:
            summary_amount = decimal.Decimal(tmp_list[1])
            amount_collected = decimal.Decimal(str(getattr(row, "_12")))
            if summary_amount == amount_collected:
                return True, tmp_list[0]
    return False, None


def get_excel_data(file_path):
    if not file_path:
        raise FileNotFoundError("传入的文件值为空:<{}>".format(file_path))
    if not os.path.exists(file_path):
        raise FileNotFoundError("传入的文件不存在:<{}>".format(file_path))
    # 处理文件格式
    handle_excel_fmt(file_path)
    # 正式读取文件
    pf = pd.read_excel(file_path)
    return pf


def date_fmt(date_str):
    try:
        date_str = datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")
    except Exception as e:
        print("日期错误:<{}>".format(date_str))
        raise ValueError("时间处理有点问题，但不是很大~:<{}>, err={}".format(date_str, str(e)))
    return date_str


def filter_date(excel_data):
    date_list = set()
    for row in excel_data.itertuples():
        (is_confirm, date) = check_row(row)
        if is_confirm:
            try:
                date = date_fmt(date)
            except ValueError as ve:
                print(ve)
                continue
            date_list.add(date)
    return list(date_list)


def filter_data_by_excel(file_path):
    # 1、获取数据excel表格
    excel_data = get_excel_data(file_path)
    # 2、过滤数据
    date_list = filter_date(excel_data)
    # 将日期进行排序
    date_list.sort()
    # 3、返回日期列表
    return date_list


# END$>

# TEST?>
# pf = pd.read_excel(in_file_path)
# print(pf.columns)
print(filter_data_by_excel(in_file_path))
