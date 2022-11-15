#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import re

data = json.loads(flow)

value = data['element']['values']
department = value["部门/职位"].rsplit("/")[0].split(")")[1]
position = value["部门/职位"].split("/")[1]
value["部门"] = department
value["职位"] = position
if value['收款账户'] == '***':
    value['收款账户'] = ' '
if '应付金额' not in value.keys():
    value['应付金额'] = 0
# data["data"]["datainfo"]=value["付款账号"]
# data["data"]["info1"]=value["事由"]
# data["data"]["info2"]=value["费用项目"]
# data["data"]["value"]=value["扣款金额"]

flow = json.dumps(data)
