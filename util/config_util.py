#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Description 读取Config配置工具

import os
import configparser

DEFAULT = './config.ini'
TYPE_ENUM = [
    "INI",
    "YAML",
    "XML"
]


def get_ini_info(file_path, encoding):
    # 创建一个配置文件对象
    config = configparser.ConfigParser()
    # 读取配置
    try:
        config.read(file_path, encoding=encoding)
    except Exception as e:
        raise RuntimeError("配置文件读取异常！\n<{}>".format(e))
    # 获取所有的section
    sections = config.sections()
    # 将配置整合为字典并返回
    config_dict = dict([(section, dict(config.items(section))) for section in sections])
    return config_dict


def get_config(config=DEFAULT, file_type='INI', encoding='utf-8'):
    """
    获取配置文件配置
    :param config: 配置文件地址，默认为 './config.ini'
    :param file_type: 配置文件类型，默认为 INI。支持类型['INI', 'YAML', 'XML']
    :param encoding: 读取配置文件使用的编码格式，默认 UTF-8
    :return: config_dict: 返回配置文件字典
    """
    # 判断是否找得到配置文件
    if not os.path.exists(config):
        raise FileNotFoundError("找不到配置文件！<{}>".format(config))
    # 配置文件类型是否正确
    if file_type.upper() not in TYPE_ENUM:
        raise TypeError("配置文件类型错误！<{}>".format(file_type))

    # 判断调用那个处理配置文件的方法
    config_dict = dict()
    flag = file_type.upper()

    if flag == TYPE_ENUM[0]:
        config_dict = get_ini_info(config, encoding)
    elif flag == TYPE_ENUM[1]:
        pass
    elif flag == TYPE_ENUM[2]:
        pass

    return config_dict
