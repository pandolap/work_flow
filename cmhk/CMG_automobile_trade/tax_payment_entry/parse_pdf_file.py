#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import cv2
import numpy as np
import os
import requests

img_path = r"D:\RPA\缴税\图片"
customs_clearance_no = '021220221000024757'
excel_bill_list = []
data_list = [{}]


def remove_temp_file(file_list, file_name):
    """
    剔除文件列表中包含给定名称的文件
    :param file_list: 文件列表
    :param file_name: 给定剔除的文件名
    :return: 没有返回值，直接对原列表进行修改
    """
    if file_list is not None and len(file_list) > 0:
        for file in file_list[:]:
            if file_name in file:
                os.remove(os.path.join(img_path, file))
                file_list.remove(file)
    else:
        pass


def intercept_pic(pic_path, custom_area, out_path='./'):
    """
    使用opencv库截取指定图片区域输出到指定位置
    :param pic_path: 图片地址
    :param custom_area: 指定的图片区域。例如：['100:200', '400:500']
    :param out_path: 截图输出的地址
    :return: 返回截图位置
    """
    if not os.path.exists(pic_path):
        raise Exception("图片地址失效")
    if custom_area is None or () == custom_area:
        raise Exception("自定义截图范围缺失")
    try:
        img = cv2.imdecode(np.fromfile(pic_path, dtype=np.uint8), 1)
        # h, w, c = img.shape
        img_snip = img[custom_area[0]:custom_area[1], custom_area[2]:custom_area[3]]
        out_img_path = os.path.join(out_path, "tmp.jpg")
        if os.path.exists(out_img_path):
            os.remove(out_img_path)
        cv2.imencode('.jpg', img_snip)[1].tofile(out_img_path)
        del img
        return out_img_path
    except Exception:
        raise Exception("截取图片失败")


def get_ocr_data(img_file, retry_count=5):
    """
    调用OCR接口识别图片信息并返回
    :param retry_count: 重试次数，默认为5次
    :param img_file: 图片文件
    :return: 接口响应的信息
    """
    request_url = "http://trial.web.glority.cn:8000/classify?type=20"
    param = {"image_file": img_file}

    req_count = 0
    while req_count < retry_count:
        response = requests.post(request_url, files=param)
        res = response.json()
        if res.get('response', None):
            return res
        else:
            req_count += 1
    raise Exception("OCR接口异常")


def parse_img(image_path):
    """
    解析图片信息并返回
    :param image_path: 待解析的图片地址
    :return: 解析后的信息
    """
    if os.path.exists(image_path):
        with open(image_path, 'rb') as f:
            # 获取ocr解析数据
            res = get_ocr_data(f, 5)

            val = res.get("response")[0].get("text2")
            return val
    else:
        raise Exception("解析图片路径错误")


def get_data_detach(data):
    """
    将传入的字典数据进行键值分离
    :param data: 字典类型数据
    :return: (key, value) 键值对
    """
    if not isinstance(data, dict):
        raise Exception('打印报关单-传入的数据不符合要求')
    try:
        file_name = list(data.keys())[0]
        bill_data = data.get(file_name)
    except:
        raise Exception('打印报关单-单表数据异常无法解析')
    return file_name, bill_data


def get_data():
    """
    获取数据的主方法。将OCR解析到的数据存入全局数据中。
    :return:无返回值
    """
    abs_file_path = os.path.abspath(img_path)
    file_list = os.listdir(img_path)
    # 剔除残留的临时图片文件
    remove_temp_file(file_list, "tmp")

    res_data = []
    for file in file_list:
        if customs_clearance_no in file:
            rel = {}
            now_path = os.path.join(abs_file_path, file)
            # 完税价格
            out = intercept_pic(now_path, (735, 765, 785, 885), abs_file_path)
            v1 = parse_img(out)
            rel.setdefault("完税价格", v1)
            print("完税价格：" + v1)
            # 税种
            out = intercept_pic(now_path, (135, 168, 228, 580), abs_file_path)
            v2 = parse_img(out)
            rel.setdefault("税种", v2)
            print("税种：" + v2)
            # 税款金额
            out = intercept_pic(now_path, (402, 433, 228, 580), abs_file_path)
            v3 = parse_img(out)
            rel.setdefault("税款金额", v3)
            print("税款金额：" + v3)
            res_data.append(rel)
    print(res_data)

    for excel in excel_bill_list:
        (current_excel_name, excel_data) = get_data_detach(excel)
        for bill in excel_data:
            if bill['报关单号'] == customs_clearance_no:
                bill['单据信息'] = res_data
                bill['所属文件'] = current_excel_name
                data_list.append(bill)
                break


# 执行
get_data()
