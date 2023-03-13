#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

# 入参
config_dict = {}


# start
def check_path(path):
    """
    校验地址，如果不存在则创建
    :param path: 地址路径
    """
    if path is None or path == '':
        raise Exception('程序异常-校验地址为空')
    if not os.path.exists(path):
        os.makedirs(path)


check_path(config_dict['base_path'])
check_path(config_dict['temp_path'])
check_path(config_dict['img_path'])
check_path(config_dict['log_path'])
check_path(config_dict['err_img_path'])
# end
