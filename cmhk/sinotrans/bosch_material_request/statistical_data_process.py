#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# 统计数据计算

import os
import shutil

import openpyxl
import pandas as pd
from datetime import datetime
import win32com.client as win32
from openpyxl import load_workbook
import numpy as np
from openpyxl.styles import Font, Border, Alignment, Side
from openpyxl.utils.dataframe import dataframe_to_rows

from util.config_util import get_config

# 入参
dirs = {'input': r'C:\\RPA\\中外运_博世叫料\\input', 'output': r'C:\\RPA\\中外运_博世叫料\\output',
        'runtime': r'C:\\RPA\\中外运_博世叫料\\output\\20221219', 'output_back': r'C:\\RPA\\中外运_博世叫料\\output_back',
        'runtime_back': r'C:\\RPA\\中外运_博世叫料\\output_back\\20221219', 'log': r'C:\\RPA\\中外运_博世叫料\\output\\20221219\\log',
        'screenshot': r'C:\\RPA\\中外运_博世叫料\\output\\20221219\\err_img',
        'download': r'C:\\RPA\\中外运_博世叫料\\output\\20221219\\download',
        'supply_order': r'C:\\RPA\\中外运_博世叫料\\output\\20221219\\order'}

# 邮箱附件地址
attach_path = r"C:\RPA\中外运_博世叫料\output\20221215\download\邮箱附件.xlsx"
#
supplier_email = {
    "DL": "aoyucs@163.com",
    "MYS": "Fupj@szmys.com",
    "YT": "53237761@qq.com",
    "WZXC": "cssales2@szwzxc.com",
}

file_dict = {
    "attach": r"C:\RPA\中外运_博世叫料\output\20221219\download\20221209_SAP_97506873.xlsx",
    "export": r"C:\\RPA\\中外运_博世叫料\\output\\20221219\\download\\111平台-BSZZ01-库存即时报表（自用）.xlsx",
    "template": r"C:\\RPA\\中外运_博世叫料\\output\\20221219\\原材料入库模板.xlsx",
    "supply": r"C:\\RPA\\中外运_博世叫料\\output\\20221219\\供应商送货单.xlsx",
    "material": r"C:\\RPA\\中外运_博世叫料\\output\\20221219\\原材料需求叫料.xlsx"
}

abbr_dict = {
    "鼎立": "DL",
    "王子新材": "WZXC",
    "美盈森": "MYS",
    "裕同": "YT"
}

print(supplier_email)


# 检测传入的文件是否存在
def check_file_exist(*target_files):
    if target_files:
        res = [str(file) for file in target_files if file is None or os.path.exists(file) is False]
        if res:
            return False, ",".join(res)
        else:
            return True, None
    else:
        return False, target_files


# 将dataframe数据组合成二维数据
def copy_process(df_copy):
    # 处理将要拷贝的数据
    compose = [np.array(df_copy.columns)]
    # 拼接主体数据
    compose.extend(df_copy.values)
    return compose


# 对原有数据进行覆写
def form_override(data, target_file, sheet_name=None):
    # 检测文件的正确性
    (is_exist, files) = check_file_exist(target_file)
    if data and is_exist and sheet_name:
        if isinstance(data, list):
            wb = openpyxl.load_workbook(target_file)
            try:
                # 判断是否为默认的sheet页
                if sheet_name:
                    sheet = wb[sheet_name]
                else:
                    sheet = wb.active
                # 获取数据的行数
                row_max = len(data)
                # 进行数据覆写
                for row in range(0, row_max):
                    for col in range(0, len(data[row])):
                        # 写入一个单元格
                        sheet.cell(row=row + 1, column=col + 1, value=data[row][col])
                # 将数据保存
                wb.save(target_file)
            except Exception as e:
                raise Exception("数据写入失败|<{}>".format(e))
            finally:
                # 关闭文件传输
                wb.close()
        else:
            raise TypeError("传入的覆写数据类型错误")
    else:
        raise ValueError("覆写数据未空或是目标文件错误")


# 对附件数据进行处理
def attachment_process(attach_file, tool_file):
    # 检测文件的正确性
    (is_exist, files) = check_file_exist(attach_file, tool_file)
    if is_exist:
        # 将附件的A和C列删除，当天的数据还未统计完成所以应该剔除C列
        df = pd.read_excel(attach_file, usecols="B,D:Q")
        # 拷贝数据转换
        copy_data = copy_process(df)
        # 将数据写入目标文件
        form_override(copy_data, tool_file, "需求")
    else:
        if files:
            raise FileNotFoundError("下载的邮箱附件未找到|<{}>".format(files))
        else:
            raise ValueError("传入的文件值为空|<{}>".format(files))


# 刷新表格文件
def excel_refresh(target_excel):
    (is_exist, files) = check_file_exist(target_excel)
    # 检测文件稳定性
    if is_exist:
        app = win32.DispatchEx("Excel.Application")
        # 设置为不可见
        app.Visible = False
        # 设置为不警告
        app.DisplayAlerts = False
        try:
            wb = app.Workbooks.Open(target_excel)
            wb.RefreshAll()
            app.CalculateUntilAsyncQueriesDone()
            wb.Save()
        except Exception as e:
            raise IOError("文件刷新失败|<{}>".format(e))
        finally:
            app.Quit()
    else:
        raise FileNotFoundError("找不到将要刷新的文件|<{}>".format(target_excel))


# 系统库存导出数据写入 => 进化 = 通用拷贝表格数据方法
def copy_excel_data(from_file, to_file, to_sheet, copy_area=None):
    """
    将源自A表中的n列数据拷贝到B表中
    :param from_file: 数据来源文件
    :param to_file: 数据去向文件
    :param to_sheet: 拷贝到的表格sheet名默认为第一个
    :param copy_area: 拷贝来源的范围列入："A,C,D:Q"
    """
    # 检测文件的正确性
    (is_exist, files) = check_file_exist(from_file, to_file)
    if is_exist:
        # 读取导出数据【物料代码】和【未分配】
        df = pd.read_excel(from_file, usecols=copy_area)
        # 处理拷贝数据
        copy_data = copy_process(df)
        # 将数据写入目标文件
        form_override(copy_data, to_file, to_sheet)
    else:
        if files:
            raise FileNotFoundError("文件未找到|<{}>".format(files))
        else:
            raise ValueError("传入的文件值为空|<{}>".format(files))


def create_export_data(order_no, supplier_type, goods_code, receipt, stock_local):
    # 初始化单挑入库数据实例
    template_entity = {
        "货主代码": "BSZZ",
        "外部订单号": order_no,
        "订单类型": "YLRK",
        "供应商名称": supplier_type,
        "货品代码": goods_code,
        "预期收货数量": receipt,
        "包装单位": "EA",
        "库位": stock_local,
        "批次状态": "A",
        "物料状态": "N"
    }
    return template_entity


def subtotal_data(supplier_name, supplier_abbr, group_data):
    # 4、获取需求订单数据（订单数量 - 半成品库存）
    # 获取当前日期字符串
    current_time = datetime.now().strftime("%Y%m%d")
    # 3批次列表
    export_data = []
    for row in group_data.itertuples():
        # 货品代码
        goods_code = row[0][0]
        # 库位
        stock_local = row[0][3]
        if stock_local == 0:
            stock_local = "L01"
        # 预期收货数量
        stock = int(row[0][1])
        # 批次1-4
        batch_1_4 = int(getattr(row, "_1")) - stock
        if batch_1_4 > 0:
            no = "{}{}{}".format(current_time, supplier_abbr, "1-4")
            export_data.append(create_export_data(no, supplier_name, goods_code, batch_1_4, stock_local))
        # 批次5-9
        batch_5_9 = int(getattr(row, "_2")) - batch_1_4
        if batch_5_9 > 0:
            no = "{}{}{}".format(current_time, supplier_abbr, "5-9")
            export_data.append(create_export_data(no, supplier_name, goods_code, batch_5_9, stock_local))
        # 批次10-14
        batch_10_14 = int(getattr(row, "_3")) - batch_5_9
        if batch_10_14 > 0:
            no = "{}{}{}".format(current_time, supplier_abbr, "10-14")
            export_data.append(create_export_data(no, supplier_name, goods_code, batch_10_14, stock_local))
    return export_data


def load_template(file_path, data):
    df = pd.read_excel(file_path, header=1)
    for row in data:
        df.loc[len(df)] = row
    print(df)
    out_value = df.values
    idx = len(out_value)
    wb = openpyxl.load_workbook(file_path)
    sheet = wb.active

    for i in range(0, idx):
        for j in range(0, len(out_value[i])):
            cell = sheet.cell(row=2 + i + 1, column=j + 1, value=out_value[i][j])
            set_cell_style_by_export(cell)
    wb.save(file_path)


def generate_order_by_supply(order, data, supply_file):
    data_list = []
    # 获取需要的数据
    row_idx = 0
    for row in data:
        order_no = row.get("外部订单号")
        if order_no != order:
            continue
        row_idx += 1
        entity = [row_idx]
        code = row.get("货品代码")
        entity.append(code)
        supply = row.get("供应商名称")
        entity.append(supply)
        amount = row.get("预期收货数量")
        entity.append(amount)
        entity.append("PCS")
        stock_local = row.get("库位")
        entity.append(stock_local)
        entity.append("")
        data_list.append(entity)

    # 写入供货单
    wb = openpyxl.load_workbook(supply_file)
    sheet = wb.active

    # 单号
    sheet.cell(row=2, column=1, value=order)
    idx = len(data_list)
    for i in range(0, idx):
        for j in range(0, len(data_list[i])):
            sheet.row_dimensions[3 + i + 1].height = "25"
            cell = sheet.cell(row=3 + i + 1, column=j + 1, value=data_list[i][j])
            set_cell_style_by_export(cell)

    # 结尾
    sheet.row_dimensions[3 + idx + 1].height = "25"
    sheet.cell(row=3 + idx + 1, column=1, value="送货人：")
    sheet.cell(row=3 + idx + 1, column=5, value="收货人：")
    # 保存
    wb.save(supply_file)
    wb.close()
    return supply_file


def generate_supply_order(supply_name, supply_data, supply_file, to_dir):
    sort_data = sorted(supply_data, key=lambda x: x.get("外部订单号"))
    no_list = set([data.get("外部订单号") for data in sort_data])
    supply_list = []
    for no in no_list:
        # 生成文件名
        out_file_name = "{}供货单{}.xlsx".format(supply_name, no)
        out_path = os.path.join(to_dir, out_file_name)
        shutil.copyfile(supply_file, out_path)
        supply_list.append(generate_order_by_supply(no, supply_data, out_path))

    return supply_list


def set_cell_style_by_export(cell):
    # 字体
    font = Font(size=11, vertAlign='baseline')
    # 边框
    side = Side(border_style='thin', color='000000')
    border = Border(left=side, right=side, top=side, end=side)
    # 对齐
    align = Alignment(horizontal='center', vertical='center')
    # cell
    cell.font = font
    cell.border = border
    cell.alignment = align
    return cell


def make_storage_template(tool, template, supply_file, to_dir):
    # 1、拿去BOM数据
    df = pd.read_excel(tool, sheet_name="BOM")
    # 2、制作数据透视表
    df_pivot = pd.pivot_table(df, index=["子件料号二级", "半成品库存", "供应商", "库位"],
                              values=["1-4日订单数量\n（加急）", "5-9日订单数量", "10-14日订单数量"],
                              aggfunc={"1-4日订单数量\n（加急）": np.sum, "5-9日订单数量": np.sum, "10-14日订单数量": np.sum},
                              margins=False)
    # 3、按供应商分类数据
    export_data = []
    # 供货单文件字典
    supply_list = dict()
    for k, v in abbr_dict.items():
        supplier_type = k
        if k == "王子新材":
            supplier_type = "王子"
        group_data = df_pivot.query("供应商 == ['{}']".format(supplier_type))
        tmp = subtotal_data(k, v, group_data)
        file_list = generate_supply_order(k, tmp, supply_file, to_dir)
        supply_list.setdefault(k, file_list)
        export_data.extend(tmp)
    sort_data = sorted(export_data, key=lambda x: x.get("外部订单号"))
    # 导入模板
    load_template(template, sort_data)
    return supply_list


def statistical_data(files, in_dirs):
    """
    $统计中心：主方法
    :param files: 使用的文件映射表
    :param in_dirs: 使用的文件加映射
    :return: supply_file_dict 供应商单地址映射
    """
    # 校验文件稳定性
    (is_exist, msg) = check_file_exist(*list(files.values()))

    if is_exist:
        # 1、首先获取叫料工具表格
        material_tool = files.get("material")
        # 2、获取附件表格进行处理
        attach_excel = files.get("attach")
        # 拷贝表格的数据
        copy_excel_data(attach_excel, material_tool, "需求", "B,D:Q")
        # 3、获取系统库存导出数据进行处理
        export_excel = files.get("export")
        # 同样也是拷贝表格的数据
        copy_excel_data(export_excel, material_tool, "系统库存导出数据", "B,T")
        # 4、对工具表格进行刷数据
        excel_refresh(material_tool)
        # 5、制作导入模板和供货单
        template_file = files.get("template")
        supply_file = files.get("supply")
        to_dir = in_dirs.get("supply_order")
        # 开始生成模板和文件
        supply_file_dict = make_storage_template(material_tool, template_file, supply_file, to_dir)
        # 将供应商和映射文件列表返回
        return supply_file_dict
    else:
        raise FileNotFoundError("程序异常-缺少必要文件无法执行|<{}>".format(msg))


print(statistical_data(file_dict, dirs))

# ===============需求数据写入=============== #
# pf = pd.read_excel(r"C:\Users\Administrator\Downloads\测试包\20221209_SAP_97506873.xlsx", usecols="B,D:Q")
# book = load_workbook(r"C:\Users\Administrator\Downloads\原材料需求叫料11.30.xlsx")
# sheet = book["需求"]
# # 处理一下数据将列数据和body数据进行整合
# copy_data = [np.array(pf.columns)]
# copy_data.extend(pf.values)
# idx = len(copy_data)
# for i in range(0, idx):
#     for j in range(0, len(copy_data[i])):
#         sheet.cell(row=i+1, column=j+1, value=copy_data[i][j])
# book.save(r"C:\Users\Administrator\Downloads\原材料需求叫料11.30.xlsx")
# ======================================== #