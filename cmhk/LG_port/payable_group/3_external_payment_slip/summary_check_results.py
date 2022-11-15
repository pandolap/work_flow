#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json

with open(r"") as f:
    flow = f.read()

data = json.loads(flow)

# 审批意见
result = data['data'].get('result', ['提示：机器人试运行，【根据费用类型找不到审批流】；'])

if data['data']['组织编码不匹配'] == 'Y':
    result.append('付款账户与单据编号中的组织编码不匹配；')

data['data']['verifyResult'] = ''.join(result)

flow = json.dumps(data)
