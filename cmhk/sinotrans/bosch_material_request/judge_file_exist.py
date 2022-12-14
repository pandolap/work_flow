#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# 判断文件是否存在
import os


# 入参

def judge_file_exist(target_path):
    is_file_exist = False
    if target_path and os.path.exists(target_path):
        is_file_exist = True
    return is_file_exist


is_download = judge_file_exist(file_path)
