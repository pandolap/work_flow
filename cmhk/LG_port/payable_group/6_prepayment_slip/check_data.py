#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import re
import time
import os
import traceback
import datetime

data = json.loads(flow)

log_dir = data['config'].get('log_dir')
home_dir = data['config'].get('home_dir')
No = data['data']['baseInfo']['单据编号']
invoice_dir = os.path.join(os.path.join(log_dir, 'ocr与审批流运行数据'), No)
if not os.path.exists(invoice_dir):
    os.makedirs(invoice_dir)
baseInfo = data['data']['baseInfo']

pre_log_file = os.path.join(invoice_dir, No + '_预付款单审批流.json')
with open(pre_log_file, 'w', encoding='utf-8') as f:
    json.dump(data, f)


def handle_data(flow):
    webapproal = []
    if not flow["element"]["approval"]:
        return
    for i in flow["element"]["approval"]:
        if "加签" in i[0]:
            continue
        if i not in webapproal:
            webapproal.append(i)
    flow["element"]["approval"] = webapproal

def compareApproval(flow):
    if not flow["element"]["approval"]:
        flow["data"]["advice"].append("【流程异常，请检查单据】；")
        return
    if not flow["data"]["verifyflow"]:
        if data['data']['not_find_company']:
            flow["data"]["advice"].append('提示：机器人试运行，【审批矩阵找不到该公司】；')
        #else:
            #flow["data"]["advice"].append('提示：机器人试运行，【流程异常，请检查单据】；')
        return
    webdata = []
    exdata = []
    re_obj = re.compile(">\d+")
    for i in flow["element"]["approval"]:
        if i[0] not in ["部门领导1", "部门领导2", "本地财务1", "本地财务2", "本部财务1"]:
            webdata.append(i[1])

    for k, v in flow["data"]["verifyflow"][0].items():
        if v != "" and k not in ['费用类型_按金额判断', '部门_', '人员类别_', '报销人填单及扫描_', '_',
                                 '费用类型_'] or k.split("_")[0] in ["部门领导1",
                                                                 "部门领导2",
                                                                 "本地财务1",
                                                                 "本地财务2",
                                                                 "本部财务1"]:
            if "、" in v:
                handle_v = v.split("、")
            elif "/" in v:
                handle_v = v.split("/")
            else:
                handle_v = v
            if k.split("_")[0] in ["部门领导1", "部门领导2", "本地财务1", "本地财务2", "本部财务1"]:
                for i in flow["element"]["approval"]:
                    if i[0] in ["部门领导1", "部门领导2", "本地财务1", "本地财务2", "本部财务1"]:
                        if i[0] == k.split("_")[0]:
                            if i[1] not in handle_v:
                                if v:
                                    flow["data"]["advice"].append(v + "不在审批记录；")
                            break
            else:
                try:
                    if float(flow["data"]["baseInfo"]["预付金额"]) > int(
                            re_obj.search(k).group().replace(">", "")):
                        if isinstance(handle_v, list):
                            exdata += handle_v
                            if not set(handle_v).intersection(webdata):
                                flow["data"]["advice"].append(v + "不在审批记录；")
                        elif isinstance(handle_v, str):
                            exdata.append(handle_v)
                            if handle_v not in webdata:
                                flow["data"]["advice"].append(v + "不在审批记录；")
                except:
                    if isinstance(handle_v, list):
                        exdata += handle_v
                        if not set(handle_v).intersection(webdata):
                            flow["data"]["advice"].append(v + "不在审批记录；")
                    elif isinstance(handle_v, str):
                        exdata.append(handle_v)
                        if handle_v not in webdata:
                            flow["data"]["advice"].append(v + "不在审批记录；")
    if not flow["data"]["advice"]:
        flow["data"]["advice"].append("审批流程无误；")
    else:
        for i in flow["data"]["advice"]:
            if "审批记录" in i:
                continue
            flow["data"]["advice"].append("审批流程无误；")
            break

try:
    #data["data"]["advice"] = []
    number = re.findall("\d+", data["element"]["text"].split("-")[3])[0]
    if number != data["data"]["baseInfo"]["付款账号"].split("-")[1]:
        data["data"]["advice"].append("组织编号不一致；")
    handle_data(data)
    compareApproval(data)
    if '审批流程无误' in data["data"]["advice"]:
        data['data']['verifyResult'] =  '机器人试运行，审批意见：' + ''.join(data['data']['advice'])
    else:
        data['data']['verifyResult'] =  '机器人试运行，审批意见：' + '【' + ''.join(data['data']['advice']) + '】'

except:
    data['data']['verifyResult'] = '机器人试运行，审批意见：流程异常，请检查日志'

flow = json.dumps(data)
