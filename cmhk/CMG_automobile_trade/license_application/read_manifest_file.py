#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os.path
import re

import pandas as pd
import openpyxl
import math
import win32com.client as win32
import datetime

# 入参
list_dir = r'D:\RPA\许可证\清单'
list_data = []


# start
def excel_convert(excel_path, to_file_type):
    """
    根据输入的Excel文件地址以及转换后缀将文件转换为对应的文件格式
    :param excel_path: 文件路径
    :param to_file_type: 文件类型后缀，仅支持 { 'xls', 'xlsx' }
    :return: 转换后的文件路径
    """
    # 参数检查
    if not os.path.exists(excel_path):
        raise Exception("程序异常-method(excel_convert):转换Excel文件路径错误")
    if '.xls' not in excel_path and '.xlsx' not in excel_path:
        raise Exception("程序异常-method(excel_convert):传入文件非Excel")
    if to_file_type is None or to_file_type == '':
        raise Exception("程序异常-method(excel_convert):转换Excel文件类型缺失")
    if 'xls' not in to_file_type or 'xlsx' not in to_file_type:
        raise Exception("程序异常-method(excel_convert):Excel转换类型错误")
    # 打开文件
    excel = win32.gencache.EnsureDispatch('Excel.Application')
    excel.Visible = False
    wb = excel.Workbooks.Open(excel_path)
    out_excel_path = ''
    # 判断具体转换格式
    file_type = excel_path.split(".")[-1]
    if 'xls' == to_file_type and file_type != 'xls':
        out_excel_path = excel_path[:-1]
        if not os.path.exists(out_excel_path):
            wb.SaveAs(out_excel_path, FileFormat=56)
    elif 'xlsx' == to_file_type and file_type != 'xlsx':
        out_excel_path = excel_path + 'x'
        if not os.path.exists(out_excel_path):
            wb.SaveAs(out_excel_path, FileFormat=51)
    # 关闭原始文件
    wb.Close()
    excel.Application.Quit()
    if out_excel_path:
        return out_excel_path
    else:
        return excel_path


def check_nan(ex_val, mark):
    if pd.isna(ex_val):
        raise Exception('列表数据异常；第%d行数据有空值' % int(mark + 1))
    else:
        return ex_val


def filter_excel_hidden_row(file_path):
    """
    使用pandas将表格文件中的隐藏文件全部删除
    :param file_path: 文件地址
    :return: 返回已经去除隐藏文件的excel对象
    """
    if file_path is None or not os.path.exists(file_path):
        raise Exception("程序异常-method(filter_excel_hidden_row):EXCEL文件地址出错")

    try:
        work_book = openpyxl.load_workbook(file_path)
        sheet_name = work_book.sheetnames[0]
        sheet = work_book[sheet_name]
        hidden_row_ids = [row - 2 for row, dimension in sheet.row_dimensions.items() if dimension.hidden]
        df = pd.read_excel(file_path)
        df.drop(hidden_row_ids, axis=0, inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df
    except:
        raise Exception(f"程序异常-method(filter_excel_hidden_row):${file_path}文件打开失败")


def check_chinese(text_str):
    """
    判断传入的文本中是否含有中文
    :param text_str: 检查文本
    :return: 含有中文返回True,反之返回False
    """
    if not text_str:
        raise Exception('程序异常-判断是否含有中文：传入文本为空')
    if re.search(u'[\u4300-\u9fa5]', text_str):
        return True
    else:
        return False


def is_english(text_str):
    """
    判断是否为英文
    :param text_str: 检查文本
    :return: 是英文T,反之F
    """
    if u'\u0041' <= text_str <= u'\u005a' or u'\u0061' <= text_str <= u'\u007a':
        return True
    else:
        return False


def parse_zh_and_en(text_str):
    """
    将文本按照英文和中文分割起来
    :param text_str: 检查文本
    :return: (中文,英文)
    """
    # 先判断是英文开头还是中文开头
    header_char = text_str[0]
    is_chinese = check_chinese(header_char)

    if is_chinese:
        # 中文开头
        flag_idx = 0
        for i, h_str in enumerate(text_str):
            if not check_chinese(h_str):
                flag_idx = i
                break
        ch_t = text_str[0:flag_idx]
        en_t = text_str[flag_idx:]
        # 确定英文开头
        en_idx = 0
        for i, h_str in enumerate(en_t):
            if is_english(h_str):
                en_idx = i
                break
        en_t = en_t[en_idx:].strip()
    else:
        # 英文开头
        flag_idx = 0
        for i, h_str in enumerate(text_str):
            if check_chinese(h_str):
                flag_idx = i
                break
        en_t = text_str[0:flag_idx - 1]
        ch_t = text_str[flag_idx:]
        en_t = en_t.strip()

    return ch_t, en_t


def parse_data(path):
    # 转换文件格式，如果是xls就转化为xlsx，如果是xlsx就不进行转换
    file_path = excel_convert(path, 'xlsx')
    # 去除掉隐藏数据
    con = filter_excel_hidden_row(file_path)
    data = con.values

    # 过滤掉无用数据
    for idx, val in enumerate(data):
        if pd.isna(val[2]):
            data = data[0:idx]
            break

    res_data = []
    group_data = []
    try:
        for col, row in enumerate(data):
            if not math.isnan(row[0]) and not math.isnan(row[12]) and group_data:
                res_data.append(group_data)
                group_data = []
            # 分割国外贸易商中英文名称
            trader_context = check_nan(row[16], col)
            (trader_zh, trader_en) = parse_zh_and_en(trader_context)

            # 分割国外生产商中英文名称
            manufacture_context = check_nan(row[17], col)
            (manufacture_zh, manufacture_en) = parse_zh_and_en(manufacture_context)

            # 将暂无替换成当前时间
            tmp_date = check_nan(row[15], col)
            if tmp_date == '暂无':
                tmp_date = datetime.datetime.now()
            if isinstance(tmp_date, str):
                char_flag = ''
                for num in tmp_date:
                    if not num.isdigit():
                        char_flag = num
                        break
                tmp_str = tmp_date.split(char_flag)
                if len(tmp_str) != 3:
                    raise Exception('日期解析错误：%s' % tmp_date)
                tmp_date = datetime.date(int(tmp_str[0]), int(tmp_str[1]), int(tmp_str[2]))
            # 装载单条数据
            entity = {
                '贸易国': check_nan(row[2], col),
                '原产地国': check_nan(row[3], col),
                '报关口岸': check_nan(row[4], col),
                '商品编码': check_nan(row[5], col),
                '币种': check_nan(row[8], col),
                '规格型号': check_nan(row[9], col),
                '台数': check_nan(row[10], col),
                '单价': check_nan(row[11], col),
                '外贸合同号': check_nan(row[14], col),
                '到港日期': tmp_date.strftime('%Y-%m-%d'),
                '贸易商英文': trader_en,
                '贸易商中文': trader_zh,
                '生产商英文': manufacture_en,
                '生产商中文': manufacture_zh,
                '生产国': check_nan(row[18], col)
            }
            group_data.append(entity)

        if group_data:
            res_data.append(group_data)
        return res_data
    except Exception as e:
        raise Exception(f'业务异常-读取清单文件失败:{e}')


file_names = os.listdir(list_dir)
list_path = os.path.join(list_dir, file_names[0])
list_data = parse_data(list_path)
print('解析到的清单数据：' + str(list_data))
# end
