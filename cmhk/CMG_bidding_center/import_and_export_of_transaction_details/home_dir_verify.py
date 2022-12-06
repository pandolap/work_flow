#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from util.config_util import get_config
import sys
import os
from datetime import datetime

# ARGS

config_dict = get_config().get("config")


# START:
def init_runtime_dir(output_dir):
    current_date = datetime.now().strftime("%Y%m%d")
    # 当前运行目录
    current_date_dir = os.path.join(output_dir, current_date)
    if not os.path.exists(current_date_dir):
        os.makedirs(current_date_dir)
    # 日志目录
    logs_dir = os.path.join(current_date_dir, "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    # 旧数据目录
    old_detail_dir = os.path.join(current_date_dir, "old_detail")
    if not os.path.exists(old_detail_dir):
        os.makedirs(old_detail_dir)
    # 交易详情目录
    transaction_details_dir = os.path.join(current_date_dir, "transaction_details")
    if not os.path.exists(transaction_details_dir):
        os.makedirs(transaction_details_dir)


def home_setting_verify():
    """
    校验主目录以及一些流程运行必须的配置文件
    """
    # 检查主目录是否存在
    home_dir = config_dict.get("home_dir")
    if not os.path.exists(home_dir):
        raise Exception("业务异常：配置主目录不存在，请检查配置文件是否存在 %s" % home_dir)
    # 检查导入模板文件是否存在
    template_url = os.path.join(home_dir, r"input\银行账户交易明细导入模板.xlsx")
    if not os.path.exists(template_url):
        raise Exception("业务异常：导入模板文件缺失，流程无法执行 %s" % template_url)
    # 检查输出目录是否存在
    output_dir = os.path.join(home_dir, "output")
    output_back_dir = os.path.join(home_dir, "output_back")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(output_back_dir):
        os.makedirs(output_back_dir)

    zip_dir = os.path.join(output_back_dir, datetime.now().strftime("%Y%m%d"))
    if not os.path.exists(zip_dir):
        os.makedirs(zip_dir)
    # 导入附带的python脚本库文件
    lib_dir = os.path.join(home_dir, r'input\package')
    if not os.path.exists(lib_dir):
        raise Exception("业务异常：配置目录中的库文件缺失，流程异常，请联系运维人员 %s" % lib_dir)
    # 加载一下运行目录
    init_runtime_dir(output_dir)
    if lib_dir not in sys.path:
        sys.path.insert(0, lib_dir)
    from rpa_recorder import set_home_dir
    # 设置主目录
    set_home_dir(config_dict)
    # 打印一下系统路径日志
    print(sys.path)


# RUN
home_setting_verify()

# END;

# TEST?>
