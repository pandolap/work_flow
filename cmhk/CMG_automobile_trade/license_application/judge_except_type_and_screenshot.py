#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os

# 入参
config_dict = {}
exception_dict = {}

# start
home_dir = config_dict.get('base_path', '')
err_pic_path = os.path.join(home_dir, 'err.png')

flag = True
for k, v in exception_dict.items():
    if k.startswith('业务异常'):
        flag = False
        break
# end
