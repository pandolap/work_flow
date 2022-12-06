#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from util.config_util import get_config

import os
import datetime

# ARGS

config_dict = get_config().get("config")


# START:

# Tips: 获取当前运行文件夹
def get_current_runtime_dir():
    """
    获取当前运行文件夹
    :return: current_run_dir 当前运行文件夹
    """
    # 1 获取流程输出目录
    output_path = os.path.join(config_dict.get('home_dir'), 'output')
    # 2 获取当前运行的输出目录
    current_run_date = datetime.datetime.now().strftime('%Y%m%d')
    current_run_dir = os.path.join(output_path, current_run_date)
    # 3 返回当前运行文件夹
    return current_run_dir


# Tips: 获取异常截图地址
def get_err_image_path():
    """
    获取异常截图地址
    :return: err_image_path 异常截图地址
    """
    err_image_path = os.path.join(get_current_runtime_dir(), 'err_screenshot.png')
    return err_image_path

# END;

# TEST?>
