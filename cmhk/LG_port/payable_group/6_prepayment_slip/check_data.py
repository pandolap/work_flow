#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import re
import time
import pandas as pd
import os
import traceback
import datetime

with open(r"C:\Users\Administrator\Downloads\20230203_测试\测试数据\3790-JK-20230202-0001\3790-JK-20230202-0001_预付款单审批流.json", encoding='utf-8') as f:
    flow = f.read()

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
            flow["data"]["advice"].append('机器人审批意见：【审批矩阵找不到该公司】；')
        # else:
        # flow["data"]["advice"].append('提示：机器人试运行，【流程异常，请检查单据】；')
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
        flow["data"]["advice"].append("审批流程无误")
    else:
        for i in flow["data"]["advice"]:
            if "审批记录" in i:
                continue
            flow["data"]["advice"].append("审批流程无误")
            break


# 对往来户、供货商/客户，对收款人字段名称的检查

def check_field(standard: str, tested: str) -> tuple:
    if not (standard and tested):
        raise Exception("比较字符串时，入参为空")
    # 对两个字段进行去空格处理
    standard = standard.strip()
    tested = tested.strip()
    # 将两个字段进行逐字比对
    # 首先比较字段的长度
    standard_len = len(standard)
    tested_len = len(tested)
    idx = 1
    is_flag = False
    if standard_len != tested_len:
        is_flag = True
    compare_len = min(standard_len, tested_len)
    for i in range(0, compare_len):
        if standard[i] != tested[i]:
            is_flag = True
            break
        else:
            idx += 1
    return is_flag, idx


add_approval = []
wrong_opinion = []

# 校验客商名称集合
merchant_name = {}
exclude_name = ['集团公共客商', '', ' ', '\xa0']
payee = baseInfo.get('收款人')
supplier = list(filter(lambda supply: supply not in exclude_name, baseInfo.get('供货商', [])))
if supplier:
    merchant_name.setdefault('供货商', supplier)
# customer = list(filter(lambda cust: cust not in exclude_name, baseInfo.get('客户', [])))
# if customer:
#     merchant_name.setdefault('客户', customer)
# contacts = baseInfo.get('往来户')
# if contacts and '集团公共客商' != contacts:
#     merchant_name.setdefault('往来户', [contacts])
is_name_correct = True
if merchant_name:
    for k, v in merchant_name.items():
        for item in v:
            (is_, diff_place) = check_field(payee, item)
            if is_:
                is_name_correct = False
                wrong_opinion.append('【请核查{}中第{}字】'.format(k, diff_place))
                break

if is_name_correct:
    add_approval.append('客商名称准确')

payment_bank = baseInfo.get('付款银行', '')
offline_payment_details = os.path.join(home_dir, '线下付款明细.xls')
offline_details = pd.read_excel(offline_payment_details)
query_result = offline_details.query('单据编号=="{}"'.format(No))
is_china_bank = payment_bank.startswith('中国银行股份有限公司')
is_cmhk = payment_bank.startswith('招商局集团财务有限公司')
pay_comment = ""
if len(query_result) > 0:
    if is_china_bank or is_cmhk:
        wrong_opinion.append('【线下付款银行未修改】')
    else:
        pay_comment = '线下付款准确；'
else:
    if is_china_bank or is_cmhk:
        pay_comment = '线上付款；'
    else:
        wrong_opinion.append('【补充线下付款申请】')

if pay_comment:
    add_approval.append(pay_comment)

try:
    # data["data"]["advice"] = []
    number = re.findall("\d+", data["element"]["text"].split("-")[3])[0]
    if number != data["data"]["baseInfo"]["付款账号"].split("-")[1]:
        data["data"]["advice"].append("组织编号不一致；")
    handle_data(data)
    compareApproval(data)
    if '审批流程无误' in data["data"]["advice"]:
        data['data']['verifyResult'] = '机器人审批意见：' + ''.join(data['data']['advice'])
    else:
        data['data']['verifyResult'] = '机器人审批意见：' + '【' + ''.join(data['data']['advice']) + '】'
    # 将新增审批意见添加
    data['data']['verifyResult'] += '；' + '；'.join(wrong_opinion) + '；' + '；'.join(add_approval)

except Exception as e:
    print(e)
    data['data']['verifyResult'] = '机器人审批意见：流程异常，请检查日志'

flow = json.dumps(data)
