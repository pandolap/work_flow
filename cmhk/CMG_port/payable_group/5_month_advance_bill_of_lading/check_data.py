#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import re, xlrd, os

data = json.loads(flow)

if data["data"]["baseInfo"]["贷方科目"] == "":
    data["data"]["advice"].append("贷方科目待核查；")

if data["data"]["baseInfo"]["业务期间"] and data["data"]["baseInfo"]["单据日期"]:
    if data["data"]["baseInfo"]["业务期间"].split("-")[1] != data["data"]["baseInfo"]["单据日期"].split("-")[1]:
        data["data"]["advice"].append("【日期月份不一致】；")
else:
    data["data"]["advice"].append("【日期月份不一致】；")


def handle_data(flow):
    webapproal = []
    if not flow["element"]["approval"]:
        flow["data"]["advice"].append("审批异常：【审批记录不存在，请检查】；")
        return False
    for i in flow["element"]["approval"]:
        if "加签" in i[0]:
            continue
        if i not in webapproal:
            webapproal.append(i)
    flow["element"]["approval"] = webapproal
    return True


def compareApproval(flow):
    if not flow["data"]["exceldata"]:
        return
    advice = []
    webdata = []
    webdata1 = {}
    verityflow = {}
    excel1 = {}
    for j in flow["element"]["approval"]:
        if "本部财务1" in j[0]:  # 字符替换
            j[0] = j[0].replace("部", "地")
        if j[0] not in ["本地财务1", "本地财务2", "本地财务"]:
            webdata.append(j[1].strip())  # 合并的人
        else:
            webdata1[j[0].strip()] = j[1].strip()

    for i in flow["data"]["exceldata"]:
        if i[0] in ["本地财务1", "本地财务2"]:
            excel1[i[0].strip()] = i[1].strip()
            if "、" in i[1]:
                handle_v = i[1].split("、")
            elif "/" in i[1]:
                handle_v = i[1].split("/")
            else:
                handle_v = i[1]
            for j, k in webdata1.items():
                if j in i[0]:
                    if k not in handle_v:
                        if i[1]:
                            advice.append('【' + i[0] + i[1] + "待核查】；")
                    break
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
                    advice.append('【' + i[0] + i[1] + "待核查】；")
            elif isinstance(handle_v, str):
                # exdata.append(handle_v)
                if handle_v not in webdata:
                    advice.append('【' + i[0] + i[1] + "待核查】；")
    # if set(excel1).intersection(webdata1.keys()):
    if "本地财务" in webdata1.keys():
        for i in excel1.keys():
            if excel1[i] != webdata1["本地财务"]:
                advice.append('【' + i + excel1[i] + "待核查】；")
    else:
        for i in excel1.keys():
            if i not in webdata1.keys():
                advice.append('【' + i + excel1[i] + "待核查】；")
        for i in webdata1.keys():
            if i not in excel1.keys():
                advice.append('【' + i + webdata1[i] + "待核查】；")
    # a=set(list(webdata1.keys())) - set(excel1)
    # b=[c for c in a]
    # if "部门领导" not in b:
    #     for i in b:
    #         advice.append(i+ "不存在；")
    if not advice:
        advice.append("审批流程无误")
    for i in advice:
        i.strip()
    flow['data']['advice'] = flow['data']['advice'] + advice


rs = handle_data(data)
if rs:
    compareApproval(data)
data['data']['advice'].insert(0, '\n审批流：')
if data['data']['verifyResult'].strip() == '机器人预审：':
    data['data']['verifyResult'] = '机器人预审：\n【没有检测到发票】'

data['data']['verifyResult'] = data['data']['verifyResult'] + '\n' + ''.join(data['data']['advice'])
flow = json.dumps(data)
