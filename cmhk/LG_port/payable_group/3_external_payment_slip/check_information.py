#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import os
import re
import pandas as pd

# ARGS:
with open(r"C:\Users\Administrator\Downloads\今日测试\15080008-GXAP-20221118-0023\审批流.json", encoding='utf-8') as f:
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
    result.append('提示：机器人审批意见：【网页取数异常，超时未取到网页审批流表格】；')

if data['data']['not_find_company']:
    result.append('提示：机器人审批意见：【审批矩阵找不到该公司】；')
verifyflows = data['data'].get('verifyflow', [])


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


# 校验客商名称集合
merchant_name = {}
exclude_name = ['集团公共客商', '', ' ', '\xa0']
payee = itemDict.get('收款人')

supplier = list(filter(lambda supply: supply not in exclude_name, itemDict.get('供货商', [])))
if supplier:
    merchant_name.setdefault('供货商', supplier)
customer = list(filter(lambda cust: cust not in exclude_name, itemDict.get('客户', [])))
if customer:
    merchant_name.setdefault('客户', customer)
contacts = itemDict.get('往来户')
if contacts and '集团公共客商' != contacts:
    merchant_name.setdefault('往来户', [contacts])

if merchant_name:
    for k, v in merchant_name.items():
        for item in v:
            (is_, diff_place) = check_field(payee, item)
            if is_:
                result.append('【请核查{}中第{}字】'.format(k, diff_place))
                break


# 增加 由预付款单推出对外付款单审核要点
# subsist_no = itemDict.get('预付款单号')
# pay_amount = itemDict.get('付款金额')
# total_payable_amount = itemDict.get('合计应付金额')
#
# if float(pay_amount) == 0.0:
#     if subsist_no not in ['', ' ', '...']:
#         result.append('【请核查总金额, 差额{}】'.format(total_payable_amount))


# 核对线下付款
def get_original_num(title_text: str) -> str:
    """
    获取原单编号
    :param title_text: 当前单据标题
    :return: 原单编号
    """
    begin_idx = title_text.find("原单编号")
    before_idx = title_text.rfind(")")
    if begin_idx != -1 and before_idx != -1:
        _num = title_text[begin_idx:before_idx]
        res_ = re.findall(r"\d+-\w+-\d+-\d+", _num)
        if len(res_) > 0:
            original_num = res_[0]
            return original_num
        else:
            return ""
    else:
        return ""


payment_bank = itemDict.get("付款银行", "")
offline_payment_details = os.path.join(home_dir, '线下付款明细.xls')
offline_details = pd.read_excel(offline_payment_details)
invoice_title = data['data']['current_title']
original_no = get_original_num(invoice_title)
query_result = offline_details.query('单据编号=="{}"'.format(original_no))
is_china_bank = payment_bank.startswith('中国银行股份有限公司')
is_cmhk = payment_bank.startswith('招商局集团财务有限公司')
pay_comment = ""
if len(query_result) > 0:
    if is_china_bank or is_cmhk:
        result.append('【线下付款银行未修改】')
    else:
        pay_comment = '线下付款准确；'
else:
    if is_china_bank or is_cmhk:
        pay_comment = '线上付款；'
    else:
        result.append('【补充线下付款申请】')

# 改动

resultSet = {}
approval_flow = []

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

else:
    result.append(data['data']['advice'][0])

if len(result) > 0 and result[0].startswith('提示'):
    # 去掉提示
    result[0] = result[0][3:]
    data['data']['result'] = result
elif len(resultSet) > 0:
    if approval_flow:
        resultSet = ['【' + ','.join(list(resultSet)) + ' (' + '-'.join(approval_flow) + ')' + '】']
    else:
        resultSet = ['【' + ','.join(list(resultSet)) + '】']
    resultSet.insert(0, '机器人审批意见：')

    is_merchant = True
    if len(result) > 0:
        for res in result:
            if '请核查' in res:
                is_merchant = False
            resultSet.append(res)

    if is_merchant:
        resultSet.append('客商名称准确；')

    resultSet.append(pay_comment)

    data['data']['result'] = resultSet

else:
    if len(result) > 0:
        is_merchant_inspect_exist = False
        is_approval_process = False
        for res in result:
            if '请核查' in res:
                is_merchant_inspect_exist = True
            if '未找到' in res:
                is_approval_process = True
        if is_approval_process:
            if is_merchant_inspect_exist:
                hint = ['机器人审批意见：{}；'.format('；'.join(result)) + pay_comment]
            else:
                hint = ['机器人审批意见：{}；客商名称准确；'.format('；'.join(result)) + pay_comment]
        else:
            if is_merchant_inspect_exist:
                hint = ['机器人审批意见：{}；审批流程无误；'.format('；'.join(result)) + pay_comment]
            else:
                hint = ['机器人审批意见：{}；审批流程无误；客商名称准确；'.format('；'.join(result)) + pay_comment]
        data['data']['result'] = hint
    else:
        data['data']['result'] = ['机器人审批意见：审批流程无误；客商名称准确；' + pay_comment]

    # for i in resultSet:
    #     i = i.strip()
    # print(data['data']['result'] )
# else:
#     if data['data']['not_find_company']:
#         data['data']['result'] = ['机器人审批意见：【审批矩阵找不到该公司】；']
flow = json.dumps(data)
