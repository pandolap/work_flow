#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import os
import re
import xlrd

data = json.loads(flow)

data["data"]["other"] = []


def get_org_code():
    home_dir = data['config']['home_dir']
    wb = xlrd.open_workbook(os.path.join(home_dir, "悬浮码比对表格.xlsx"))
    sht = wb.sheet_by_index(0)
    arr = []
    for n, r in enumerate(range(sht.nrows)):
        if n == 0:
            continue
        b_col = sht.cell(r, 1).value
        c_col = sht.cell(r, 2).value
        if not b_col or not c_col:
            break
        arr.append([b_col, c_col])

    return arr


def check_org_code(arr, web_code):
    rs = list(filter(lambda x: x[0] == web_code, arr))
    if len(rs) > 0:
        return rs[0][1]
    return web_code


def check_code():
    global data
    number = data["data"]["baseInfo"]["单据编号"].split("-")[0]
    bank_name = data['data']['baseInfo'].get('付款银行')
    if bank_name.find('财务公司') > -1:
        return

    floatCode = data['data']['attr_value']
    # if floatCode.find('-') > -1:
    #    floatCode = floatCode.split('-')[0]
    floatCode = re.findall(r'\d+', floatCode)[0]
    arr = get_org_code()
    floatCode = check_org_code(arr, floatCode)
    if data['data']['attr_value'] == '22410002':
        pass
    elif number != floatCode:
        data["data"]["other"].append("【悬浮编码不一致；】")


check_code()


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
        # verityflow[i[0]]=i[1]
        i[0] = i[0].strip()
        if i[0] in ["本地财务1", "本地财务2"]:
            handle_v = []
            excel1[i[0].strip()] = i[1].strip()
            if "、" in i[1]:
                handle_v = i[1].split("、")
            elif "/" in i[1]:
                handle_v = i[1].split("/")
            else:
                handle_v = i[1]
            for j, k in webdata1.items():
                # if j in i[0]:
                k = k.strip()
                if j == i[0]:
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
                advice.append('【' + i + excel1[i] + "待核查；】")
        for i in webdata1.keys():
            if i not in excel1.keys():
                advice.append('【' + i + webdata1[i] + "待核查；】")
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
    flow['data']['advice'].insert(0, '\n审批流：')


rs = handle_data(data)
if rs:
    compareApproval(data)
# data['data']['advice'].insert(0, '审批流：\n')
data['data']['verifyResult'] = '机器人预审：\n' + data['data'].get('ocr', '【没有检测到发票】；') + ''.join(
    data['data']['advice']) + '\n' + ''.join(data['data']['other'])
# data['data']['verifyResult'] = '机器人预审：\n' +  data['data']['verifyResult'] + ''.join(data['data']['advice'])
# +'\n'+''.join(data['data']['other'])

log_dir = data['config']['log_dir']
flow_dir = os.path.join(log_dir, '审批流')
target_dir = os.path.join(flow_dir, data["data"]["baseInfo"]["单据编号"])
if not os.path.exists(target_dir):
    os.makedirs(target_dir)
target_file = os.path.join(target_dir, 'flow.json')
with open(target_file, 'w', encoding='utf-8') as f:
    json.dump(data, f)
flow = json.dumps(data)
