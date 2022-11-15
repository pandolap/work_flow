#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import os
import pandas as pd

data = json.loads(flow)

home_dir = data['config'].get('home_dir')
specialFeeFile = os.path.join(home_dir, '特殊费用表.xlsx')
verifyFlowFile = os.path.join(home_dir, '审批矩阵表.xlsx')
postFile = os.path.join(home_dir, '职位.xlsx')

element = data['data']['baseInfo']

company = element.get('公司')
feeNameCode = element.get('费用项目').split(' ')
# 费用编码
code = feeNameCode[1].strip()
# 费用名称
feeName = feeNameCode[0].strip()
if feeName.find('_') > -1:
    feeName = feeName.split('_')[1].strip()
department = element.get('部门')
# 获取职位映射
manType = element.get('职位')
if manType is not None:
    post_table = pd.read_excel(postFile, header=1)
    post_dict = post_table.to_dict()
    for k, v in post_dict.items():
        if manType in v.values():
            manType = k
            break

control = data['control']
control['run'] = 'api_flowinfo'
control['arguments'] = [specialFeeFile, verifyFlowFile, company, department, manType, code, feeName]

log_dir = data['config'].get('log_dir')
No = data['data']['baseInfo']['单据编号']
invoice_dir = os.path.join(os.path.join(log_dir, 'ocr与审批流运行数据'), No)
if not os.path.exists(invoice_dir):
    os.makedirs(invoice_dir)


def record_runtime_data(runtime_data, name):
    with open(os.path.join(invoice_dir, name) + '.json', 'w', encoding='utf-8') as f:
        json.dump(runtime_data, f)


record_runtime_data(data, '查找审批流前.json')
flow = json.dumps(data)
