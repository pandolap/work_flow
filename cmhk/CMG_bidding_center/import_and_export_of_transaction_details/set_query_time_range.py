#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Description 设置查询时间范围
from util.config_util import get_config
from datetime import datetime, timedelta
import os

# ARGS!>

config = get_config().get("config")


# START:>

def get_query_time_range(info):
    max_range = int(info.get("query_max_range"))
    current_time = datetime.now()
    last_time = current_time - timedelta(days=max_range)
    current_time = current_time.strftime("%Y-%m-%d")
    last_time = last_time.strftime("%Y-%m-%d")

    return last_time, current_time


# END$>
out_file_name = "111.xlsx"
(last_time, current_time) = get_query_time_range(config)

print(last_time)
print(current_time)


def get_current_runtime_dir(config_dict):
    """
    获取当前运行文件夹
    :return: current_run_dir 当前运行文件夹
    """
    # 1 获取流程输出目录
    output_path = os.path.join(config_dict.get('home_dir'), 'output')
    # 2 获取当前运行的输出目录
    current_run_date = datetime.now().strftime('%Y%m%d')
    current_run_dir = os.path.join(output_path, current_run_date)
    # 3 返回当前运行文件夹
    return current_run_dir


current_run_dir = get_current_runtime_dir(config)
out_dir_path = os.path.join(current_run_dir, "old_detail", out_file_name)
# print(os.path.join(out_dir_path, out_file_name))
print(out_dir_path)
