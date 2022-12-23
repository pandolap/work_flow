#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# 工作目录配置初始化及检查

import os
from datetime import datetime
import shutil

import json
from util.config_util import get_config

# 入参
# config = config_dict
config = get_config().get("config")


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


def flow_init(work_dir):
    # 创建一个目录字典
    dirs = dict()
    # 流程输出目录
    output_dir = os.path.join(work_dir, "output")
    check_dir(output_dir, True, False)
    current_dir = runtime_dir_create(output_dir)
    # 输出备份目录
    output_back_dir = os.path.join(work_dir, "output_back")
    check_dir(output_back_dir, True, False)
    current_back_dir = runtime_dir_create(output_back_dir)
    # 当前运行日志目录
    log_dir = os.path.join(current_dir, "log")
    check_dir(log_dir, True)
    # 运行截图目录
    err_img_dir = os.path.join(current_dir, "err_img")
    check_dir(err_img_dir, True)
    # 下载文件目录
    download_dir = os.path.join(current_dir, "download")
    check_dir(download_dir, True)
    # 供货单目录
    order_dir = os.path.join(current_dir, "order")
    check_dir(order_dir, True)
    # 将路径写入字典中
    dirs.setdefault("input", os.path.join(work_dir, "input"))
    dirs.setdefault("output", output_dir)
    dirs.setdefault("runtime", current_dir)
    dirs.setdefault("output_back", output_back_dir)
    dirs.setdefault("runtime_back", current_back_dir)
    dirs.setdefault("log", log_dir)
    dirs.setdefault("screenshot", err_img_dir)
    dirs.setdefault("download", download_dir)
    dirs.setdefault("supply_order", order_dir)

    # copy模板文件
    input_dir = os.path.join(work_dir, "input")
    _template = os.path.join(input_dir, "原材料入库模板.xlsx")
    _supply = os.path.join(input_dir, "供应商送货单.xlsx")
    _material = os.path.join(input_dir, "原材料需求叫料.xlsx")
    template = os.path.join(current_dir, "原材料入库模板.xlsx")
    supply = os.path.join(current_dir, "供应商送货单.xlsx")
    material = os.path.join(current_dir, "原材料需求叫料.xlsx")
    shutil.copyfile(_supply, supply)
    shutil.copyfile(_template, template)
    shutil.copyfile(_material, material)

    files = {
        "template": template,
        "supply": supply,
        "material": material
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
    return flow_init(work_dir)


# 执行
(dir_dict, file_dict) = check_work_dir(config)

print(json.dumps(dir_dict, indent=2, ensure_ascii=False))
