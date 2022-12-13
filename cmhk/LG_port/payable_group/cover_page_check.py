#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import time
import json
import requests
import pandas as pd
from datetime import datetime
from requests_toolbelt import MultipartEncoder

# 接口地址
INTERFACE_URL = "https://openapi.cmft.com/gateway/general1/1.0.0/api/pdfrec"
INTERFACE_URL_BACKUP = "https://openapi.cmft.com:8080/gateway/general1/1.0.0/api/pdfrec"

# DEBUG: 使用测试文件进行测试
with open(r"C:\Users\Administrator\Downloads\48500008-GXAP-20221208-0024\48500008-GXAP-20221208-0024_pre.json") as f:
    flow = f.read()

# 获取流程中的数据流
data = json.loads(flow)


# 1、获取影像链接
def get_image_url(data_source):
    # 获取OCR链接和页面公司名称
    img_urls = data_source.get("data").get("imgN")
    cover_url = None
    is_exist_img = False
    # 判断链接是否存在
    if img_urls:
        is_exist_img = True
        cover_url = img_urls[0]
    return is_exist_img, cover_url


# 2、OCR识别
def download_img(cover_url, target_dir):
    res = requests.get(cover_url)
    if res.status_code != 200:
        raise Exception("链接请求失败<{}>".format(cover_url))
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    img_file_path = os.path.join(target_dir, '封面页{date}.jpg'.format(date=now_str))
    with open(img_file_path, "wb") as mf:
        mf.write(res.content)
    return img_file_path


def ocr_interface_call(cover_path, retry=5):
    # 二进制方式打开封面图片
    with open(cover_path, "rb") as mf:
        image_file = mf.read()
    # 请求负载数据
    payload = MultipartEncoder(
        fields={
            "file": ("image.jpg", image_file),
            "content": "multipart/form-data"
        }
    )
    # 请求头
    header = {
        "Authorization": "ACCESSCODE 142717D9360287ED5BD1D03E1B6805D2",
        "x-Gateway-APIKey": "b9180959-bb39-4f58-935a-bacc6a80d16c",
        "Content-Type": payload.content_type,
    }
    res = None
    # 重试
    while retry:
        # 发送请求
        res = requests.post(INTERFACE_URL, data=payload, headers=header)
        retry -= 1
        # 请求没有成功
        if res.status_code != 200:
            res = None
            time.sleep(1)
            continue
        # 识别结果错误
        if json.loads(res.content).get("code") == "N":
            time.sleep(1)
            continue
        break
    # 判断接口是否调用正常
    if res is None:
        raise Exception("OCR异常，接口调用失败")
    else:
        res = json.loads(res.content)
    # 判断结果是否识别成功
    if res.get("code") == "Y":
        return res.get("details")[0]
    else:
        raise Exception("封面页异常，接口返回信息<{}>".format(res.get("message")))


# 3、读取表格
def read_excel(excel_path, sheet_name):
    return pd.read_excel(excel_path, header=0, sheet_name=sheet_name)


# 4、检测
def excel_data_fmt(excel_data):
    if pd.isna(excel_data):
        return ""
    return excel_data.strip()


def check_data(company_data, interface_info, web_company):
    # 循环检测数据
    comment = ""
    for row in company_data.itertuples():
        excel_company = excel_data_fmt(getattr(row, "组织名称"))
        if web_company == excel_company:
            description = excel_data_fmt(getattr(row, "是否股份"))
            if "招商局港口" in interface_info[0]:
                comment = "【封面打印有误；请检查；】"
                break
            if "股份" in description and "辽港股份" in interface_info[0]:
                comment = "打印封面正确；"
                break
            elif "太平湾" in description and "招商局太平湾" in interface_info[0]:
                comment = "打印封面正确；"
                break
            else:
                comment = "打印封面正确；"
                break
    if comment == "":
        comment = "【封面打印有误；请检查；】"
    return comment


# 初始化
def init(data_source):
    web_company = data_source.get("data").get("baseInfo").get("公司")
    log_dir = data_source.get("config").get("log_dir")
    no = data_source.get("data").get("baseInfo").get("单据编号")
    invoice_dir = os.path.join(os.path.join(log_dir, 'ocr与审批流运行数据'), no)
    if not os.path.exists(invoice_dir):
        os.makedirs(invoice_dir)
    home_dir = data_source.get("config").get("home_dir")
    excel_path = os.path.join(home_dir, "辽港公司名单.xlsx")
    return web_company, invoice_dir, excel_path


# 备份OCR结果
def ocr_data_backup(ocr_data, target_dir):
    cover_ocr_file = os.path.join(target_dir, '封面页OCR识别数据.json')
    with open(cover_ocr_file, "w", encoding='utf-8') as mf:
        json.dump(ocr_data, mf)


def ocr_check(data_flow):
    # 获取数据流中需要的值
    (web_company, invoice_dir, excel_path) = init(data_flow)
    # 获取影像链接
    (is_exist_img, cover_url) = get_image_url(data_flow)
    if is_exist_img:
        # 下载图片
        img_path = download_img(cover_url, invoice_dir)
        # 调用OCR接口
        res = ocr_interface_call(img_path)
        # 备份识别结果
        ocr_data_backup(res, invoice_dir)
        # 取出核心数据
        res_list = res.get("lines")
        # 读取表格
        pf = read_excel(excel_path, "辽港集团")
        # 监测数据
        approval_comment = check_data(pf, res_list, web_company)
    else:
        approval_comment = "【封面打印有误；请检查；】"
    # 填写审批意见
    data_flow['data']['verifyResult'] = data_flow['data']['verifyResult'] + " {}".format(approval_comment)
    return data_flow


# 运行
flow = json.dumps(ocr_check(data))
