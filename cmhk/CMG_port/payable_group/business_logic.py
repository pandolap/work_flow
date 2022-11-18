#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import re

# itemDict = {'单据编号': '123', '付款金额': '500'}
# with open(r"C:\Users\leo\Desktop\data.json", 'r') as f:
#     data = json.load(f)

data = json.loads(flow)
with open(r'D:/data.json', 'w') as f:
    json.dump(data, f)

if data["data"]["baseInfo"]["单据编号"].split("-")[0] != data['data']['attr_value']:
    data["data"]["advice"].append("悬浮编码不一致；")


def handle_data(flow):
    webapproal = []
    if not flow["element"]["approval"]:
        flow["data"]["advice"].append("审批异常：审批记录不存在，请检查；")
        return
    for i in flow["element"]["approval"]:
        if "加签" in i[0]:
            continue
        if i not in webapproal:
            webapproal.append(i)
    flow["element"]["approval"] = webapproal


handle_data(data)


def compareApproval(flow):
    if not flow["data"]["exceldata"]:
        return
    advice = []
    webdata = []
    webdata1 = {}
    verityflow = {}
    for j in flow["element"]["approval"]:
        if "本部财务1" in j[0]:  # 字符替换
            j[0] = j[0].replace("部", "地")
        if j[0] not in ["部门领导1", "部门领导2", "本地财务1", "本地财务2"]:
            webdata.append(j[1])  # 合并的人
        else:
            webdata1[j[0]] = j[1]
    # if "部门领导" not in "".join(webdata1.keys()):
    #     advice.append("缺少部门领导；")
    # elif "本地财务" not in "".join(webdata1.keys()):
    #     advice.append("缺少本地财务；")
    for i in flow["data"]["exceldata"]:
        # verityflow[i[0]]=i[1]
        if i[0] in ["部门领导1", "部门领导2", "本地财务1", "本地财务2"]:
            if "、" in i[1]:
                handle_v = i[1].split("、")
            elif "/" in i[1]:
                handle_v = i[1].split("/")
            else:
                handle_v = i[1]
            for j, k in webdata1.items():
                if i[0] == j:
                    if k not in handle_v:
                        if i[1]:
                            advice.append("缺少" + i[0] + "；")
                    break
                # else:
                #     if "部门领导" in i[0] and "部门领导" not in j:
                #         advice.append("缺少部门领导；")
                #     elif "本地财务" in i[0] and "本地财务" not in j:
                #         advice.append("缺少本地财务；")
        else:
            if "、" in i[1]:
                handle_v = i[1].split("、")
            elif "/" in i[1]:
                handle_v = i[1].split("/")
            else:
                handle_v = i[1]
            if isinstance(handle_v, list):
                # exdata += handle_v
                if not set(handle_v).intersection(webdata):
                    advice.append("缺少" + i[0] + "；")
            elif isinstance(handle_v, str):
                # exdata.append(handle_v)
                if handle_v not in webdata:
                    advice.append("缺少" + i[0] + "；")
    if not advice:
        advice.append("审批流程无误")
    print(advice)
    advice.insert(0, '机器人试运行，审批意见：')
    for i in advice:
        i.strip()
    flow['data']['advice'] = advice


compareApproval(data)
data['data']['verifyResult'] = ''.join(data['data']['advice'])
flow = json.dumps(data)
