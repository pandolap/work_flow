#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import xlrd
import json
import traceback
import os

# ARGS:
with open(r"") as f:
    flow = f.read()
# ------------------

inArg = json.loads(flow)
data = inArg['data']
control = inArg['control']

# 部门
DPT = ''
# 费用类型
FTP = ''
# 人员类型
MTP = ''


# 按公司名获取特殊费用类型编码信息，判断网页上的费用编码是否在里面
def getFeeType(filename, sheetname, code):
    wb = xlrd.open_workbook(filename)
    if sheetname not in [i.name for i in wb.sheets()]:
        print('特殊类型表找不到表格')
        return None, None
    sh = wb.sheet_by_name(sheetname)

    L = []
    name = ''
    for i in range(1, sh.nrows):
        if sh.cell(i, 0).value:
            name = sh.cell(i, 0).value
        L.append({'name': name, 'value': sh.cell(i, 1).value})

    for xItem in L:
        if xItem['value'] == code:
            return True, xItem['name']
    return False, None


# 按公司名取出流程表数据
def getFlowData(filename, sheetname):
    global DPT, MTP, FTP
    wb = xlrd.open_workbook(filename)
    if sheetname not in [i.name for i in wb.sheets()]:
        print('流程表找不到表格')
        return '【审批矩阵找不到该公司】'

    sh = wb.sheet_by_name(sheetname)
    L = []

    if sh.nrows < 4:
        return

    header1 = [i.value for i in sh.row(1)]
    header2 = [i.value or '' for i in sh.row(2)]
    header = ['_'.join(i) for i in zip(header1, header2)]

    for h in reversed(header):
        if h.find('部门') > -1:
            DPT = h
        if h.find('费用类型') > -1:
            FTP = h
        if h.find('人员类别') > -1:
            MTP = h

    for i in range(3, sh.nrows):
        x = dict(zip(header, [i.value for i in sh.row(i)]))
        L.append(x)

    oldDept = ''
    oldFeeType = ''
    for item in L:
        dept = item.get(DPT, '').strip()
        if len(dept) > 0:
            oldDept = dept
        else:
            item[DPT] = oldDept

        feeType = item.get(FTP, '').strip()
        if len(feeType) > 0:
            oldFeeType = feeType
        else:
            item[FTP] = oldFeeType

    return L


# 取出流程
def getFlow(data, department, feeType, feeTypeName, manType=None):
    print(FTP, MTP, DPT)
    # 审批提示
    # res = inArg['data']['result']
    inArg['data']['result'] = []
    # 匹配出的流程集合
    L = []
    # 提示链集合
    # 费用类型 - 部门 - 人员类别 - 职位 - 具体人员
    tips = []
    # 1、匹配费用类型
    if feeType[0]:
        # feeType (bool, str)
        # T: 特殊费用类型
        L = list(filter(lambda x: (x[FTP].find(feeTypeName) > -1 or x[FTP].find(feeType[1]) > -1), data))
        tips.append(feeType[1])
    else:
        # F: 普通费用类型
        L = list(filter(lambda x: x[FTP].startswith('普通费用'), data))
        tips.append(feeTypeName)
    if len(L) == 0:
        inArg['data']['advice'].append('【费用类型未找到（普通费用类型）】')
    else:
        # 2、匹配部门
        L = list(filter(lambda x: x[DPT].find(department) > -1, L))
        tips.append(department)
        if len(L) == 0:
            inArg['data']['advice'].append('【部门未找到（%s）】' % '-'.join(tips))
        else:
            # 3、匹配人员类别
            if manType:
                L = list(filter(lambda x: x[MTP] == manType, L))
                tips.append(manType)
            if len(L) == 0:
                inArg['data']['advice'].append('【人员类别未找到（%s）】' % '-'.join(tips))
    return L


data['not_find_company'] = 0


# 获取报销流程接口
def api_flowinfo(specialFeeFile, flowFile, company, department, manType, code, feeTypeName):
    rs = getFeeType(specialFeeFile, company, code)
    flow_result = getFlowData(flowFile, company)
    if flow_result == '【审批矩阵找不到该公司】':
        data['not_find_company'] = 1
        return []
    else:
        return getFlow(flow_result, department, rs, feeTypeName, manType)


# 根据传入控制数据决定运行哪个函数
runDict = {
    'api_flowinfo': api_flowinfo
}

try:
    data['verifyflow'] = runDict.get(control['run'])(*control.get('arguments', []))
except Exception as e:
    with open(r'C:\RPA\log', 'a') as f:
        f.write(traceback.format_exc())
    data['verifyflow'] = []
control['arguments'] = []
flow = json.dumps(inArg)
