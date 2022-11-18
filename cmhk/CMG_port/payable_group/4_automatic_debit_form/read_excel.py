#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import xlrd
import re
import os
import json

data = json.loads(flow)
home_dir = data['config'].get('home_dir')

# with open(r"E:\work\RPA\中间文件\flow\06510005-GXAP-20220214-0002\flow.json", 'r', encoding='utf-8') as f:
#     data = json.load(f)
# home_dir = r'E:\work\RPA\中间文件\港口一期'

specialFeeFile = os.path.join(home_dir, '特殊费用类型汇总.xlsx')
verifyFlowFile = os.path.join(home_dir, '各公司费用报销标准及审批流程.xlsx')
positionFile = os.path.join(home_dir, '职位汇总.xlsx')


def isManager(position):
    wb = xlrd.open_workbook(positionFile)
    sh = wb.sheet_by_name('Sheet1')
    for i in range(sh.ncols):
        if position in sh.col_values(i, 2):
            return sh.cell_value(1, i)


# fee_pattern = re.compile(r'([A-Za-z\d_]+)([^A-Za-z\d]*)')
def get_excel_data(path2, path3, flow):
    flow['data']['advice'] = []
    if not all(
            [flow["data"]["baseInfo"]["公司"], flow["data"]["baseInfo"]["部门"],
             flow["data"]["baseInfo"]["职位"], flow["data"]["baseInfo"]["扣款金额"],
             flow["data"]["baseInfo"]["费用项目"]]):
        flow["data"]["advice"].append("网页基本数据缺失；")
        flow["control"]["is_normal"] = False
        return
    feeNameCode = flow['data']['baseInfo'].get('费用项目').replace('\n', '')
    # g = fee_pattern.search(feeNameCode)
    # 费用编码
    # code = g.group(1).strip()
    code = feeNameCode
    # 费用名称
    # feeName = g.group(2).strip()
    # if feeName.find('_') > -1:
    #     feeName = feeName.split('_')[1].strip()
    # if '（' in feeName:
    #     feeName = feeName.split('（')[0].strip()

    flow['data']['exceldata'] = []

    wb2 = xlrd.open_workbook(path2)
    try:
        sh2 = wb2.sheet_by_name(flow['data']['baseInfo']['公司'].strip())
    except:
        flow['data']['advice'].append('审批异常：当前单据公司' + flow['data']['baseInfo']['公司'] + '不在审批流表格内，请检查；')
        flow['control']['is_normal'] = 1
        return

    # 定位人员类别开始行，结束行，所在列
    rowstart = ''
    colindex = ''
    colindex1 = ''
    for i in range(sh2.nrows):
        for j in range(sh2.ncols):
            if sh2.cell_value(i, j) == '人员类别':
                rowstart = i
                colindex = j
                break
        if rowstart and colindex:
            break
    for i in range(rowstart + 2, sh2.nrows):
        if i == sh2.nrows - 1:
            rowend = sh2.nrows
            # if sh2.cell_value(i, colindex) == '':
            # rowend = i
            break
    for i in range(sh2.nrows):
        for j in range(sh2.ncols):
            if sh2.cell_value(i, j) == '归口部门2':
                colindex1 = j
                break
        if colindex1:
            break

    # 处理费用类型
    cost_type = ''
    cost_tlist = []
    wb3 = xlrd.open_workbook(path3)
    sh3 = wb3.sheet_by_name('汇总费用类型表')
    company_dict = dict()

    for sh_name in wb3.sheet_names():
        if sh_name == '汇总费用类型表':
            continue
        sh = wb3.sheet_by_name(sh_name)
        company_dict[sh_name] = sh.col_values(1, 1)

    cost_type_list = []
    re_obj = re.compile(r'[a-zA-Z0-9_.-]+')
    web_company = flow['data']['baseInfo']['公司'].strip()
    excel_table = []
    excel_header = []
    for i in range(4):
        excel_header.append(sh3.cell_value(0, i))

    for r in range(1, sh3.nrows):
        excel_item = dict()
        for c in range(4):
            excel_item[excel_header[c]] = sh3.cell_value(r, c)
        excel_table.append(excel_item)

    first_search_list = list(filter(lambda x: code.find(x['费用类型编码']) > -1, excel_table))
    if len(first_search_list) > 0:
        second_search_list = list(filter(lambda x: x['适用范围'] == web_company, first_search_list))
        if len(second_search_list) == 0:
            for upper_company_name, lower_company_list in company_dict.items():
                # 判断第一次筛选的数据是否有全体公司
                for_all_list = list(filter(lambda x: x['适用范围'] == '全体公司', first_search_list))
                if len(for_all_list) > 0:
                    cost_type = for_all_list[0]['特殊费用类型分类']

                # 接着判断该公司是否在子公司集合里面
                if web_company in lower_company_list:
                    third_search_list = list(filter(lambda x: x['适用范围'] == upper_company_name, first_search_list))
                    if len(third_search_list) > 0:
                        # 匹配到数据, 特殊费用类型
                        cost_type = third_search_list[0]['特殊费用类型分类']
                    break
        else:
            cost_type = second_search_list[0]['特殊费用类型分类']

    # for i in range(1, sh3.nrows):
    #     if flow['data']['baseInfo']['公司'].strip() == sh3.cell_value(i, 0):
    #         if code.find(sh3.cell_value(i, 2)) > -1:
    #             cost_type = sh3.cell_value(i, 1)
    #             break
    #     else:
    #         if flow['data']['baseInfo']['公司'].strip() in sh3.col_values(9):
    #             if code.find(sh3.cell_value(i, 2)) > -1:
    #                 cost_type = sh3.cell_value(i, 1)
    #                 break
    #         else:
    #             for i in range(1, 11):
    #                 if code.find(sh3.cell_value(i, 2)) > -1:
    #                     cost_type = sh3.cell_value(i, 1)
    if cost_type:
        special = 1
    else:
        special = 0
        for i in range(rowstart + 2, rowend):
            if sh2.cell_value(i, 0) != '' and sh2.cell_value(i, 0) not in cost_type_list:
                cost_type_list.append(sh2.cell_value(i, 0))
        if cost_type_list:
            for i in range(len(cost_type_list)):
                handle_data = re.sub(r'[\u4e00-\u9fa5（）()、\n]+', ' ',
                                     cost_type_list[i])
                if handle_data == ' ':
                    cost_tlist.append(cost_type_list[i])
                    continue
                for k in handle_data.split(' '):
                    if k and k != '_':
                        try:
                            if code == re_obj.search(k).group():
                                cost_type = cost_type_list[i]
                                break
                        except:
                            cost_type = cost_type_list[i]
                            continue

    row_start = ''
    position = flow['data']['baseInfo']['职位'].strip()
    position = isManager(position)
    for i in range(rowstart + 2, rowend):
        dept = flow['data']['baseInfo']['部门'].strip()
        if sh2.cell_value(i, 0) in cost_tlist and dept == sh2.cell_value(i, 1) and sh2.cell_value(i,
                                                                                                  colindex) == position:
            row_start = i
            break
        elif cost_type in sh2.cell_value(i, 0) and dept == sh2.cell_value(i, 1) and sh2.cell_value(i,
                                                                                                   colindex) == position:
            row_start = i
            break
    if not row_start:
        for i in range(rowstart + 2, rowend):
            if special == 1:
                if '特殊费用类型' == sh2.cell_value(i, 0) and flow['data']['baseInfo']['部门'].strip() == sh2.cell_value(i,
                                                                                                                 1) and sh2.cell_value(
                        i, colindex) == position:
                    row_start = i
                    break
                if flow['data']['baseInfo']['部门'].strip() == sh2.cell_value(i, 1) and sh2.cell_value(i,
                                                                                                     colindex) == position:
                    row_start = i
                    break
    if not row_start:
        flow['data']['advice'].append('审批异常：费用类型或部门或职位不存在；')
        return

    # 提取审批流
    exapproval = []
    re_int = re.compile('\d+')
    price = flow['data']['baseInfo']['扣款金额'].replace(',', '')
    for i in range(colindex + 1, sh2.ncols):
        try:
            data = int(re_int.search(sh2.cell_value(rowstart + 1, i)).group())
            if data != 1 or data != 2:
                if float(price) > data:
                    if (sh2.cell_value(row_start, i) == '安全生产经费') and ('非特殊费' in sh2.cell_value(row_start, 0)):
                        continue
                    elif (sh2.cell_value(row_start, i) == '安全生产经费') and ('非特殊费' not in sh2.cell_value(row_start, 0)):
                        exapproval.append(
                            [sh2.cell_value(rowstart, i).replace('\n', ''),
                             sh2.cell_value(row_start, i - 1)])
                    elif sh2.cell_value(row_start, i) != '' and sh2.cell_value(
                            row_start, i) != '/' and sh2.cell_value(
                        rowstart + 1, i) != '':
                        exapproval.append(
                            [sh2.cell_value(rowstart, i).replace('\n', ''),
                             sh2.cell_value(row_start, i)])
        except:
            if (sh2.cell_value(row_start, i) == '安全生产经费') and ('非特殊费' in sh2.cell_value(row_start, 0)):
                continue
            elif (sh2.cell_value(row_start, i) == '安全生产经费') and ('非特殊费' not in sh2.cell_value(row_start, 0)):
                exapproval.append(
                    [sh2.cell_value(rowstart, i).replace('\n', ''),
                     sh2.cell_value(row_start, i - 1)])
            elif (sh2.cell_value(row_start, i) != '' and sh2.cell_value(row_start, i) != '/' and sh2.cell_value(
                    rowstart + 1, i) != ''):
                exapproval.append(
                    [sh2.cell_value(rowstart, i).replace('\n', ''),
                     sh2.cell_value(row_start, i)])
    a = []

    if special == 0:
        for i in exapproval:
            if '预算审批' in i[0] and i[1] != flow['data']['baseInfo']['提单人']:
                a.append(i)
            elif '归口部门' in i[0]:
                continue
            else:
                a.append(i)
    else:
        for i in exapproval:
            if '预算审批' in i[0] and i[1] != flow['data']['baseInfo']['提单人']:
                a.append(i)
            else:
                a.append(i)
    flow['data']['exceldata'] = a


get_excel_data(verifyFlowFile, specialFeeFile, data)

flow = json.dumps(data)
