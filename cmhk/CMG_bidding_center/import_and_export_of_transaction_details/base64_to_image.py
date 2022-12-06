#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Description 验证码图片转换

from util.config_util import get_config

import base64
import datetime
import os
import re

# ARGS
config = get_config().get("config")


# START:

# Tips: 获取当前运行文件夹
def get_current_runtime_dir():
    """
    获取当前运行文件夹
    :return: current_run_dir 当前运行文件夹
    """
    # 1 获取流程输出目录
    output_path = os.path.join(config.get('home_dir'), 'output')
    # 2 获取当前运行的输出目录
    current_run_date = datetime.datetime.now().strftime('%Y%m%d')
    current_run_dir = os.path.join(output_path, current_run_date)
    # 3 返回当前运行文件夹
    return current_run_dir


# Tips: base64 => picture file
def decode_image(base64_code):
    """
    将base64编码下的图片转换为图片文件
    :param base64_code: base64编码
    :return: out_img_path 输出的图片文件地址
    """
    # 提起信息
    result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", base64_code, re.DOTALL)
    if result:
        ext = result.groupdict().get("ext")
        data = result.groupdict().get("data")
    else:
        raise Exception("程序异常-图片转换异常: base64编码转换图片失败 %s" % base64_code)

    # base64解码
    img_obj = base64.urlsafe_b64decode(data)

    # 二进制文件保存
    file_name = "captcha_img.{}".format(ext)
    out_img_path = os.path.join(get_current_runtime_dir(), file_name)
    # 删除上次产生的图片
    if os.path.exists(out_img_path):
        os.remove(out_img_path)
    with open(out_img_path, "wb") as f:
        f.write(img_obj)
    return out_img_path


# Tips: picture file => base64
def encode_image(image_path):
    """
    将图片转换为base64编码格式
    :param image_path: 图片位置
    :return: base64编码格式
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError("程序异常-图片缺失: 图片路径不存在")
    # 文件获取
    (path, image_file) = os.path.split(image_path)
    # 文件名
    (file_name, ext) = os.path.splitext(image_file)
    with open(image_path, "rb") as f:
        img_obj = f.read()
    # base64编码
    data = base64.b64encode(img_obj).decode()
    base64_code = "data:image/{};base64,{}".format(ext[1:], data)
    return base64_code

# END;

# TEST?>
