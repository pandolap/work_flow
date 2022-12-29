#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# 数据备份
import os
import zipfile

# 入参
dir_dict = {
    "input": r"C:\\RPA\\中外运_博世叫料\\input",
    "output": r"C:\\RPA\\中外运_博世叫料\\output",
    "runtime": r"C:\\RPA\\中外运_博世叫料\\output\\20221228",
    "output_back": r"C:\\RPA\\中外运_博世叫料\\output_back",
    "runtime_back": r"C:\\RPA\\中外运_博世叫料\\output_back\\output_20221228-133654",
    "log": r"C:\\RPA\\中外运_博世叫料\\output\\20221228\\log",
    "screenshot": r"C:\\RPA\\中外运_博世叫料\\output\\20221228\\err_img",
    "download": r"C:\\RPA\\中外运_博世叫料\\output\\20221228\\download",
    "supply_order": r"C:\\RPA\\中外运_博世叫料\\output\\20221228\\order"
}


def zip_folder(target_file_path: str, backup_path: str) -> None:
    """
    备份文件夹
    :param target_file_path: 被压缩的文件夹地址
    :param backup_path: 目标压缩文件具体路径
    """
    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, dir_name, file_names in os.walk(target_file_path):
            f_path = path.replace(target_file_path, "")
            for file_name in file_names:
                zf.write(os.path.join(path, file_name), os.path.join(f_path, file_name))


def runtime_data_backup(dirs: dict) -> None:
    # 获取当前运行目录
    runtime_dir = dirs.get("runtime")
    # 获取当前运行备份目录
    backup_dir = dirs.get("runtime_back")
    # 获取当前是否已经有了备份
    backup_file = os.path.join(backup_dir, "backup_data.zip")
    idx = 1
    while os.path.exists(backup_file):
        backup_file = os.path.join(backup_dir, "backup_data.{}.zip".format(idx))
    # 进行备份
    zip_folder(runtime_dir, backup_file)
    pass


runtime_data_backup(dir_dict)
