#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import shutil
import pandas as pd
from datetime import datetime


def read_setting(setting_file):
    # 获取邮箱
    df = pd.read_excel(setting_file, header=1, sheet_name="邮箱")
    mail_dict = dict()
    for row in df.itertuples():
        supply_name = getattr(row, "供货商名称")
        mail_box = getattr(row, "邮箱")
        mail_dict.setdefault(supply_name, mail_box)
    # 获取缩写
    df = pd.read_excel(setting_file, header=1, sheet_name="缩写")
    abbrs = dict()
    for row in df.itertuples():
        supply_name = getattr(row, "供货商名称")
        abbr = getattr(row, "缩写")
        abbrs.setdefault(supply_name, abbr)
    return mail_dict, abbrs


def check_dir(target_dir, is_create=False, is_overwrite=True):
    # 判断路径是否存在
    if not target_dir or not os.path.exists(target_dir):
        if is_create:
            # 创建
            os.makedirs(target_dir)
        else:
            # 异常通知
            raise NotADirectoryError("未找到目录：<{}>".format(target_dir))
    else:
        # 是否覆盖目录，默认为覆盖
        if is_overwrite:
            # 删除原有目录
            shutil.rmtree(target_dir)
            # 创建新的目录
            os.makedirs(target_dir)


def runtime_dir_create(target_dir):
    # 获得当前时间串
    current_date_str = datetime.now().strftime("%Y%m%d")
    # 拼接目标目录
    current_dir = os.path.join(target_dir, current_date_str)
    check_dir(current_dir, True)
    return current_dir


def init(work_dir):
    # 创建一个目录字典
    dirs = dict()
    # 流程输出目录
    output_dir = os.path.join(work_dir, "output")
    check_dir(output_dir, True, False)
    current_dir = runtime_dir_create(output_dir)
    # 输出备份目录
    output_back_dir = os.path.join(work_dir, "output_back")
    check_dir(output_back_dir, True, False)
    current_back_dir = os.path.join(output_back_dir, "output_{}".format(datetime.now().strftime("%Y%m%d-%H%M%S")))
    check_dir(current_back_dir, True)
    # 运行截图目录
    err_img_dir = os.path.join(current_dir, "err_img")
    check_dir(err_img_dir, True)
    # 判断是否有运行日志
    runtime_log_path = os.path.join(current_dir, "runtime.log")
    download_dir = os.path.join(current_dir, "download")
    if os.path.exists(runtime_log_path):
        # 下载文件目录
        is_flow_success = False
        with open(runtime_log_path, encoding="utf-8") as f:
            log_text = f.read()
        last_row = log_text.split("\n")[-1]
        if "执行完成" in last_row:
            is_flow_success = True
        if is_flow_success:
            check_dir(download_dir, True)
        else:
            check_dir(download_dir, True, False)
    else:
        # 下载文件目录
        check_dir(download_dir, True)

    # 将路径写入字典中
    dirs.setdefault("input", os.path.join(work_dir, "input"))
    dirs.setdefault("output", output_dir)
    dirs.setdefault("runtime", current_dir)
    dirs.setdefault("output_back", output_back_dir)
    dirs.setdefault("runtime_back", current_back_dir)
    dirs.setdefault("screenshot", err_img_dir)
    dirs.setdefault("download", download_dir)

    # copy模板文件
    input_dir = os.path.join(work_dir, "input")
    _template = os.path.join(input_dir, "原材料入库模板.xlsx")
    _material = os.path.join(input_dir, "原材料需求叫料.xlsx")
    _setting = os.path.join(input_dir, "供货商邮箱配置.xlsx")

    template = os.path.join(current_dir, "原材料入库模板.xlsx")
    material = os.path.join(current_dir, "原材料需求叫料.xlsx")
    setting = os.path.join(current_dir, "供货商邮箱配置.xlsx")

    shutil.copyfile(_template, template)
    shutil.copyfile(_material, material)
    shutil.copyfile(_setting, setting)

    files = {
        "template": template,
        "material": material,
        "setting": setting
    }
    return dirs, files


def check_work_dir(in_config):
    # 检测主要目录是否存在
    # 获取配置的工作目录地址
    work_dir = in_config.get("work_dir")
    try:
        # 主工作目录
        check_dir(work_dir, is_overwrite=False)
        # 流程输入目录
        input_dir = os.path.join(work_dir, "input")
        check_dir(input_dir, is_overwrite=False)
    except NotADirectoryError as de:
        raise Exception("程序异常-工作目录检查|{e}".format(e=de))
    except Exception as e:
        raise Exception("程序异常-工作目录检查-未知错误|{e}".format(e=e))
    return init(work_dir)


# 获取文件和文件夹映射
(dir_dict, file_dict) = check_work_dir(config)
# 获取邮箱和缩写映射
(supplier_email, abbr_dict) = read_setting(file_dict.get("setting"))

config_dict = {}
pass
