#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os

# 入参
config_dict = {}

# start
home_dir = config_dict.get('base_path')
if home_dir is None:
    raise Exception('业务异常-配置目录检查：主目录为空，请检查主目录的配置')
if home_dir.find(':') < 0:
    raise Exception('业务异常-配置目录检查：主目录不合法，请检查主目录的配置')
contract_dir = os.path.join(home_dir, '合同')
list_dir = os.path.join(home_dir, '清单')
if not os.path.exists(contract_dir) or not os.path.exists(list_dir):
    raise Exception('业务异常-配置目录检查：清单或合同文件缺失不合法，请检查相关文件的配置')
# end
