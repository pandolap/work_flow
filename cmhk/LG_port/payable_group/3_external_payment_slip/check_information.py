#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import os
import re

# ARGS:
with open(r"") as f:
    flow = f.read()

data = json.loads(flow)
log_dir = data['config'].get('log_dir')
home_dir = data['config'].get('home_dir')
No = data['data']['baseInfo']['单据编号']
invoice_dir = os.path.join(os.path.join(log_dir, 'ocr与审批流运行数据'), No)
if not os.path.exists(invoice_dir):
    os.makedirs(invoice_dir)


def record_runtime_data(runtime_data, name):
    with open(os.path.join(invoice_dir, name) + '.json', 'w', encoding='utf-8') as f:
        json.dump(runtime_data, f)


record_runtime_data(data, '获取网页表格.json')

webData = data['data']
attr_value = webData.get('attr_code', '')
org_code = attr_value.split('-')[0]
itemDict = webData['baseInfo']
invoiceNo = itemDict.get('单据编号')
spendMoney = itemDict.get('付款金额')

data['data']['组织编码不匹配'] = 'N'
if not invoiceNo.startswith(org_code):
    data['data']['组织编码不匹配'] = 'Y'

# 整理获取得表格
web_table_header = [i.strip() for i in data['data']['web_table_header']]
web_table_data = data['data']['web_table_data']
web_flow_data = list(map(lambda x: dict(zip(web_table_header, x)), web_table_data))

result = []
if len(web_flow_data) == 0:
    result.append('提示：机器人试运行，审批意见：【网页取数异常，超时未取到网页审批流表格】；')

if data['data']['not_find_company']:
    result.append('提示：机器人试运行，审批意见：【审批矩阵找不到该公司】；')
verifyflows = data['data'].get('verifyflow', [])
# 改动
if len(verifyflows) > 0:
    verifyflow = verifyflows[0]

    # 审批流链条
    approval_flow = []
    lts = ['_费用类型', '_部门', '_人员类别', '人员类别_', '费用类型_', '部门_']
    for key in verifyflow:
        if key in lts:
            approval_flow.append(verifyflow.get(key))

    p = re.compile(r'^审批\d+?.*')
    p1 = re.compile(r'>(\d+)')
    commonList = []

    for verifyflow_key, verifyflow_value in verifyflow.items():
        commonSearchResult = p.search(verifyflow_key)
        vItem = dict()
        if commonSearchResult:
            vItem['man'] = verifyflow_value
        else:
            continue

        moneySearchResult = p1.search(verifyflow_key)
        if moneySearchResult:
            money = int(moneySearchResult.group(1))
            vItem['money'] = money
        commonList.append(vItem)

    commonList.sort(key=lambda x: x.get('money', 0), reverse=True)

    # 先找有对应名字的
    resultSet_valid = set()  # 不能更改
    resultSet = set()  # 可做二次核对
    excelManSet = set()
    webManSet = set([i['审批人'] for i in web_flow_data])

    # pprint(web_flow_data)
    # pprint(verifyflows)
    for k1, v1 in verifyflow.items():
        for name in ['归口部门', '部门领导', '预算审批', '本地财务']:
            if k1.find(name) > -1:
                excelManSet.add(v1)
                flag = False

                for flowItem in web_flow_data:
                    node = flowItem['审批节点']
                    if node.find('本部财务') > -1:
                        node = node.replace('本部财务', '本地财务')

                    # if node.find(name) > -1:
                    #     webManSet.add(flowItem['审批人'])

                    if k1.find(node) > -1:
                        if v1.find(flowItem['审批人']) > -1:
                            flag = True
                            break
                        else:
                            flag = False

                if not flag and v1:
                    resultSet_valid.add(v1)

    # 再找名字不对应的
    for xItem in commonList:
        # 找不到为False, 添加到审批意见；找到为True，不添加审批意见
        flag = True
        if xItem.get('money') is not None:
            # 金额超过才审
            if float(spendMoney) > xItem.get('money'):
                for flowItem in web_flow_data:
                    if flowItem['审批人'] != xItem['man']:
                        flag = False

                    else:
                        flag = True
                        break

            else:
                if xItem['man'] in excelManSet:
                    excelManSet.remove(xItem['man'])
        else:
            # 每单比审
            for flowItem in web_flow_data:
                if flowItem['审批人'] != xItem['man']:
                    flag = False
                else:
                    flag = True
                    break
        if not flag:
            resultSet.add(xItem['man'])

    if '' in excelManSet:
        excelManSet.remove('')

    subSet = excelManSet - webManSet
    newSet = set()
    for ns in subSet:
        if ns.find('、') > -1:
            itemSet = set(ns.split('、'))
            intersection = itemSet.intersection(webManSet)
            if len(intersection) == 0:
                newSet.add(ns)
        elif ns.find('\n') > -1:
            itemSet = set(ns.split('\n'))
            intersection = itemSet.intersection(webManSet)
            if len(intersection) == 0:
                newSet.add(ns)
        else:
            if ns not in webManSet:
                newSet.add(ns)

    for rset in resultSet:
        if rset.find('、') > -1:
            itemSet = set(rset.split('、'))
            intersection = itemSet.intersection(webManSet)
            if len(intersection) == 0:
                newSet.add(rset)
        elif rset.find('\n') > -1:
            itemSet = set(rset.split('\n'))
            intersection = itemSet.intersection(webManSet)
            if len(intersection) == 0:
                newSet.add(rset)
        else:
            if rset not in webManSet:
                newSet.add(rset)

    # 在做多一次金额校验
    removeList = []
    for man in newSet:
        if not man:
            continue
        notInList = list(filter(lambda x: x.get('money') and float(spendMoney) > float(x.get('money')), commonList))
        notInMen = [i['man'] for i in notInList]
        if man in notInMen:
            removeList.append(man)

    for x in removeList:
        newSet.remove(x)

    # 加上之前不可变的 result_valid
    newSet = newSet.union(resultSet_valid)
    resultSet = {'%s不在审批流中；' % i for i in newSet}
    if '不在审批流中；' in resultSet:
        resultSet.remove('不在审批流中；')

    if len(result) > 0 and result[0].startswith('提示'):
        data['data']['result'] = result
    elif len(resultSet) > 0:
        if approval_flow:
            resultSet = ['【' + ','.join(list(resultSet)) + ' (' + '-'.join(approval_flow) + ')' + '】']
        else:
            resultSet = ['【' + ','.join(list(resultSet)) + '】']
        resultSet.insert(0, '机器人试运行，审批意见：')
        data['data']['result'] = resultSet
    else:
        data['data']['result'] = ['机器人试运行，审批意见：审批流程无误；']
    # for i in resultSet:
    #     i = i.strip()
    # print(data['data']['result'] )
else:
    if data['data']['not_find_company']:
        data['data']['result'] = ['机器人试运行，审批意见：【审批矩阵找不到该公司】；']
flow = json.dumps(data)
