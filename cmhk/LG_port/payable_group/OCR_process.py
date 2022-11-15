#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import os
import re
import traceback

DEBUG = __name__ == '__main__'
ocr_list = []

if DEBUG:
    dir_name = r'E:\work\RPA\中间文件\flow\辽港\4'
    flow_json = os.path.join(dir_name, '审批流.json')
    ocr_json = os.path.join(dir_name, 'ocr.json')
    with open(flow_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data['data']['advice'] = ''
    data['data']['verifyResult'] = ''

    with open(ocr_json, 'r', encoding='utf-8') as f:
        ocr_sub_list = json.load(f)
        for item in ocr_sub_list:
            # ['response']['data']['identify_results']
            d = {
                'response': {
                    'data': {
                        'identify_results': item
                    }
                }
            }
            ocr_list.append(d)
else:
    data = json.loads(flow)

log_dir = data['config'].get('log_dir')
home_dir = data['config'].get('home_dir')
No = data['data']['baseInfo']['单据编号']
invoice_dir = os.path.join(os.path.join(log_dir, 'ocr与审批流运行数据'), No)
if not os.path.exists(invoice_dir):
    os.makedirs(invoice_dir)
baseInfo = data['data']['baseInfo']

pre_log_file = os.path.join(invoice_dir, No + '_pre.json')
with open(pre_log_file, 'w', encoding='utf-8') as f:
    json.dump(data, f)

# Todo url_dict_new 是所有图片的链接 return result.images.N
url_dict_new = data['data'].get('imgN', [])

# 记录 ocr时间
from datetime import datetime

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
with open(os.path.join(log_dir, 'OCR记录.txt'), 'a', encoding='gbk') as f:
    record = ['[', now, ']', '图片数量%s' % len(url_dict_new), '\n']
    f.write(''.join(record))

# Todo advice 是之前所有的意见
advice = data['data'].get('verifyResult', '')
flow_advice = advice
inside_pattern = re.compile(r'([^【】]*)(【提示：机器人试运行，(【[^【】]*】[^【】]*)】)(.*)')
inside_pattern_rs = inside_pattern.search(advice)
if inside_pattern_rs:
    advice = inside_pattern.sub(r'\1\3\4', advice)

# Todo costBearingcompany 是费用承担公司 深圳妈港仓码有限公司
costBearingcompany = baseInfo.get('公司')

# Todo receivingBank 是收款银行 中国工商银行股份有限公司深圳梅林支行
receivingBank = baseInfo.get('收款银行')

# Todo payee 是收款人  深圳柏汇自动化设备有限公司
payee = baseInfo.get('收款人')

# Todo collectionAccount 收款账户   4000026209200366760
collectionAccount = baseInfo.get('收款账户')

# Todo moneyFee 合计税额   106.99
moneyFee = baseInfo.get('合计税额')

# Todo feeSum 应付金额  	0
feeSum = baseInfo.get('应付金额')

# Todo finalPay 付款金额
finalPay = baseInfo.get('付款金额', '')

import requests
import re
from requests_toolbelt import MultipartEncoder
import openpyxl
import pandas as pd
import numpy as np
import uuid


def imageJson(url, count=5, ocr_result=None, img_content=None):
    if count < 0:
        invoice_err_pic = os.path.join(invoice_dir, 'invoice_%s.jpg' % uuid.uuid1())
        invoice_err_record = os.path.join(invoice_dir, '出错图片记录.txt')
        if img_content and ocr_result:
            with open(invoice_err_pic, 'wb') as fb:
                fb.write(img_content)
        info_list = [invoice_err_pic, json.dumps(ocr_result)]

        with open(invoice_err_record, 'a', encoding='utf-8') as f:
            f.write(','.join(info_list) + '''\n''')
        return ocr_result
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/"
                      "537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Saf"
                      "ari/537.36",
    }
    image_content = requests.get(url, headers=headers, timeout=15).content

    m = MultipartEncoder(
        fields={
            'file': ('images.jpg', image_content, 'text/plain'),
            'uuid': '2563f6b39b6d42c29d28ec3eb8e1d00f',
            'checkInvoice': 'True',
            'ifOcrType': 'False',
        }
    )
    try:
        omg = requests.post(url="http://ocr.pre.ninetechone.com/fileOCRAndcheckInvoice", data=m,
                            headers={'Content-Type': m.content_type})
        # return omg.json()
        rs = omg.json()
        if rs.get('message', '').find('error') > -1:
            return imageJson(url, count=count - 1, ocr_result=rs, img_content=image_content)
        if rs.get('error', 0) > 0:
            if rs.get('message', '') == 'Invalid imageFile parameter, maxsize 8MB':
                return rs
            return imageJson(url, count=count - 1, ocr_result=rs, img_content=image_content)
        return rs
    except:
        count = count - 1
        info = traceback.format_exc()
        return imageJson(url, count, ocr_result=info)


# Todo url_dict_new 是所有图片的链接 return result.images.N
# Todo advice 是之前所有的意见
# Todo costBearingcompany 是费用承担公司 深圳妈港仓码有限公司
# Todo receivingBank 是收款银行 中国工商银行股份有限公司深圳梅林支行
# Todo payee 是收款人  深圳柏汇自动化设备有限公司
# Todo collectionAccount 收款账户   4000026209200366760
# Todo moneyFee 合计税额   106.99
# Todo feeSum 应付金额  	0
totalSum = 0
taxSum = 0
listExcel = []
advice_first = advice

bearing_flag = None  # 费用承担公司标识
taxnumber_flag = None  # 税号标识
seal_flag = None  # 盖章标识
formname_flag = None  # 发票联标识
receivebank_flag = None  # 收款银行标识
seller_flag = None  # 销售方标识
collectionAccount_flag = None  # 收款账户标识
flight_flag = None  # 机票仓位标识
seat_flag = None  # 货车仓位标识
question_list = []
log_list = []
seller_bank_account_flag = None
# 抵扣联判断列表
credit_union_flag = False
# 开票时间列表
invoice_time_error_flag = False
# 付款金额(总)
pay_sum = 0
# 合计税额(总)
tax_sum = 0
# 是否有发票
invoice_exists = False

# try:
# for i in url_dict['images']['N']:
for url_index, url in enumerate(url_dict_new):
    # url = i['url']  # 拿到每一条票据的url地址
    url_index += 1
    try:
        if not DEBUG:
            omg = imageJson(url)
        else:
            omg = ocr_list[url_index - 1]

        if omg.get('error') and omg.get('message', '') == 'Invalid imageFile parameter, maxsize 8MB':
            advice += "【第{}张影像图片大小超过8M，识别不了】".format(url_index)
            continue
        log_list.append(omg['response']['data']['identify_results'])
        for item in omg['response']['data']['identify_results']:
            type = item['type']
            if type == "0000":
                # advice = advice + "没有检测到发票；"
                pass
            if type == "1001" or type == "1002" or type == "1003" or type == "1004":  # 增值税普通发票
                invoice_exists = True
                # 2022/01/15 检查是否有抵扣联, 开票时间跟当前时间比较年份 --------------------------------------------------------
                invoice_item = item.get('details', dict())
                if invoice_item.get('form_name') == '抵扣联':
                    credit_union_flag = True
                try:
                    invoice_time = datetime.strptime(invoice_item.get('date'), '%Y年%m月%d日')
                except:
                    invoice_time = datetime.now()
                    advice += '【第%s张发票时间有遮挡】' % url_index
                now = datetime.now()
                if now.year > invoice_time.year:
                    invoice_time_error_flag = True

                # 总金额和税额比较
                # ocr:
                pay = invoice_item.get('total', '').replace(',', '')
                if pay == '':
                    advice += '【第%s张发票付款金额识别不出来】' % url_index
                    pay = 0
                else:
                    pay = round(float(pay), 2)

                pay_tax = invoice_item.get('tax', '').replace(',', '')
                if pay_tax == '':
                    advice += '【第%s张发票税额识别不出来】' % url_index
                    pay_tax = 0
                else:
                    pay_tax = round(float(pay_tax), 2)

                pay_sum += pay
                tax_sum += pay_tax

                # 2022/01/15 检查是否有抵扣联, 开票时间跟当前时间比较年份 --------------------------------------------------------

                # 购买方名称
                buyer = item['details'].get('buyer', '')
                if buyer == '':
                    advice += '第%s张发票购买方名称识别不出来' % url_index
                else:
                    buyer = buyer.replace('（', '').replace('）', '').replace('(', '').replace(')', '')

                # hlt添加、总分公司对应
                sub_company_col = 5
                father_company_col = 3
                company_dict = {}
                wb = openpyxl.load_workbook(os.path.join(home_dir, '辽港母分公司对应表.xlsx'))
                table = wb.get_sheet_by_name('Sheet1')
                max_row = table.max_row
                for irow in range(max_row):
                    irow += 1
                    relation = {table.cell(irow, sub_company_col).value: table.cell(irow, father_company_col).value}
                    company_dict.update(relation)
                if costBearingcompany in company_dict.keys():
                    costBearingcompany = company_dict[costBearingcompany]
                costBearingcompany = costBearingcompany.replace('（', '').replace('）', '').replace('(', '').replace(
                    ')', '')
                # advice = advice.replace("该单没有发票；","")
                buyer = buyer.replace(' ', '')
                costBearingcompany = costBearingcompany.replace(' ', '')
                if buyer == costBearingcompany:
                    print("购买方名称与费用承担公司一致；")
                    bearing_flag = 0
                else:
                    # advice = advice + "【购买方名称与费用承担公司不一致】；"
                    bearing_flag = 1
                    question_list.append(url_index)
                # 纳税人识别号
                buyer_tax_id = item['details'].get('buyer_tax_id', '')
                if buyer_tax_id == '':
                    advice += '【第%s张发票纳税人识别号识别不出来】' % url_index
                excel_data = pd.read_excel(os.path.join(home_dir, '辽港纳税人识别号.xlsx'))
                excelSerise = pd.Series(excel_data['企业名称'])
                excelNp = np.array(excelSerise)
                for value in excelNp:
                    listExcel.append(value)
                if buyer in listExcel:
                    if buyer_tax_id == excel_data['税号'][listExcel.index(buyer)]:
                        # advice = advice + "税号一致；"
                        taxnumber_flag = 0
                    else:
                        # advice = advice + "【税号不一致】；"
                        taxnumber_flag = 1
                        question_list.append(url_index)

                try:
                    # 发票盖章
                    company_seal = item['details']['company_seal']
                    if company_seal == "1":
                        # advice = advice + "第{}张影像中发票有盖章；".format(url_index)
                        seal_flag = 0
                    elif company_seal == "0":
                        # advice = advice + "【第{}张影像中发票没有盖章】；".format(url_index)
                        seal_flag = 1
                        question_list.append(url_index)
                except:
                    # advice = advice + "【第{}张影像中发票没有盖章】；".format(url_index)
                    seal_flag = 1
                    question_list.append(url_index)
                try:
                    # 发票联
                    form_name = item['details'].get('form_name')
                    if form_name:
                        # advice = advice + "第{}张影像中发票有发票联；".format(url_index)
                        formname_flag = 0
                    else:
                        # advice = advice + "【第{}张影像中发票没有发票联】；".format(url_index)
                        if type != '1003':  # 电子发票-普票可能没有”发票联“三个字，这是正常的
                            formname_flag = 1
                            question_list.append(url_index)
                        else:
                            formname_flag = 0
                except:
                    # advice = advice + "【第{}张影像中发票没有发票联】；".format(url_index)
                    if type != '1003':  # 电子发票-普票可能没有”发票联“三个字，这是正常的
                        formname_flag = 1
                        question_list.append(url_index)

            if type == "1001" or type == "1002" or type == "1003" or type == "1004":
                invoice_exists = True
                # 价税合计
                total = item['details'].get('total', 0)
                if total == '':
                    total = 0
                totalSum = totalSum + round(float(total), 2)
                # 销售方名称
                seller = item['details']['seller'].strip()
                try:
                    # 销售方开户行及账号
                    seller_bank_account = item['details']['seller_bank_account']
                    # 销售方开户行
                    try:
                        seller_bank = re.findall(r"\d+", seller_bank_account)[0].strip()
                    except:
                        seller_bank = seller_bank_account
                    if ":" in seller_bank:
                        seller_bank = seller_bank.replace(':', '')
                    # 银行关键字
                    bankCompany = ["中国银行", "中行", "农业银行", "农行", "工商银行", "工行", "建设银行", "建行", "招商银行", "招行"]

                    if seller_bank == receivingBank:
                        print("收款银行与发票影像中的销售方开户行一致")
                    else:
                        for bankItem in bankCompany:
                            if bankItem in seller_bank:
                                if bankItem in receivingBank:
                                    receivebank_flag = 0
                                    print("收款银行与发票影像中的销售方开户行一致")
                                else:
                                    # advice = advice + "第{}张影像中收款银行与发票影像中的销售方开户行不一致；".format(url_index)
                                    receivebank_flag = 1
                                    question_list.append(url_index)
                    # 付款人母分公司对应
                    sub_company_col = 5
                    father_company_col = 3
                    company_dict = {}
                    wb = openpyxl.load_workbook(os.path.join(home_dir, '辽港母分公司对应表.xlsx'))
                    table = wb.get_sheet_by_name('Sheet1')
                    max_row = table.max_row
                    for irow in range(max_row):
                        irow += 1
                        relation = {table.cell(irow, sub_company_col).value: table.cell(irow, father_company_col).value}
                        company_dict.update(relation)
                    if payee in company_dict.keys():
                        payee = company_dict[payee]

                    payee = payee.replace('（', '').replace('）', '').replace('(', '').replace(')', '')
                    seller = seller.replace('（', '').replace('）', '').replace('(', '').replace(')', '')
                    if payee == seller:
                        seller_flag = 0
                        print("第{}张影像中收款人与发票中的销售方名称一致".format(url_index))
                    else:
                        # advice = advice + "第{}张影像中收款人与发票中的销售方名称不一致；".format(url_index)
                        seller_flag = 1
                        question_list.append(url_index)

                    # if receivingBank == seller_bank:
                    #     print("收款银行与发票影像中的销售方开户行一致")
                    # else:
                    #     advice = advice + "收款银行与发票影像中的销售方开户行不一致；"

                    # 销售方账号
                    try:
                        seller_account = re.findall(r"\d+\.?\d*", seller_bank_account)[0]
                        if seller_account.strip().find(collectionAccount.strip()) > -1:
                            collectionAccount_flag = 0
                            print("收款账户与发票影像中的销售方账号一致")
                        else:
                            # advice = advice + "第{}张影像中发票收款账户与发票影像中的销售方账号不一致；".format(url_index)
                            collectionAccount_flag = 1
                            question_list.append(url_index)
                    except Exception as e:
                        # print(e)
                        collectionAccount_flag = 1
                        question_list.append(url_index)
                except Exception as e:
                    # advice = advice + "第{}张影像中机器人无法获取销售方开户行及账号值；".format(url_index)
                    seller_bank_account_flag = 1
                    question_list.append(url_index)

            if type == "1001":  # 增值税专用发票
                invoice_exists = True
                # 税额
                tax = item['details']['tax']
                if "," in tax:
                    tax = tax.replace(",", "")
                if tax == '':
                    tax = 0
                taxSum = taxSum + float(tax)  # 累加专项发票

            if type == "1044":  # 机票或者行程单
                invoice_exists = True
                # 仓位
                flights = item['details']['flights']
                for omg in flights:
                    seat = omg.get('seat', '')
                    if seat == '':
                        advice += '【第%s张影像，机票未识别到座位等级】' % url_index
                        flight_flag = 2
                    elif "F" in seat or "A" in seat or "C" in seat or "D" in seat:
                        # advice = advice + "第{}张影像中机票或行程单超仓；".format(url_index)
                        flight_flag = 1
                        question_list.append(url_index)
                    else:
                        # advice = advice + "第{}张影像中机票或行程单正常；".format(url_index)
                        flight_flag = 0

            if type == "1042":  # 火车票、高铁票
                invoice_exists = True
                # 仓位
                toSeat = item['details'].get('seat', '')
                if toSeat == '':
                    advice += '【第%s张影像，火车票或高铁票未识别到座位等级】' % url_index
                    seat_flag = 2
                elif "一等座" in toSeat or "商务座" in toSeat:
                    # advice = advice + "第{}张影像中火车票或高铁票超仓；".format(url_index)
                    seat_flag = 1
                    question_list.append(url_index)
                else:
                    seat_flag = 0
                    # advice = advice + "第{}张影像中火车票或高铁票正常；".format(url_index)

                    # if type != "1001" or type != "1002" or type != "1003" or type != "1004":
            #     advice = advice + "该单没有发票；"

    except Exception as e:
        print(e)
        print(traceback.format_exc())
        advice += "第{}张影像调用ocr接口失败；".format(url_index)

# HLT修改后逻辑
if bearing_flag == 0:
    advice += '购买方名称与费用承担公司一致；'
elif bearing_flag == 1:
    advice += '【购买方名称与费用承担公司不一致】；'
if taxnumber_flag == 0:
    advice += '税号一致；'
elif taxnumber_flag == 1:
    advice += '【税号不一致】；'
if seal_flag == 0:
    advice += '发票有盖章；'
elif seal_flag == 1:
    advice += '【发票没有有盖章】；'
if formname_flag == 0:
    advice += '发票有发票联；'
elif formname_flag == 1:
    advice += '【发票没有发票联】；'
if receivebank_flag == 0:
    advice += '收款银行与发票影像中的销售方开户行一致；'
elif receivebank_flag == 1:
    advice += '【收款银行与发票影像中的销售方开户行不一致】；'
if seller_flag == 0:
    advice += '收款人与发票中的销售方名称一致；'
elif seller_flag == 1:
    advice += '【收款人与发票中的销售方名称不一致】；'
if collectionAccount_flag == 0:
    advice += '收款账户与发票影像中的销售方账号一致；'
elif collectionAccount_flag == 1:
    advice += '【收款账户与发票影像中的销售方账号不一致】；'
if flight_flag == 0:
    advice += '机票或行程单正常；'
elif flight_flag == 1:
    advice += '【机票或行程单超仓】；'
if seat_flag == 0:
    advice += '火车票或高铁票正常；'
elif seat_flag == 1:
    advice += '【火车票或高铁票超仓】；'
if seller_bank_account_flag == 1:
    advice += '【接口未识别到销售方开户行及账号的值】；'

# 2021/1/15 ------------------------------
if credit_union_flag:
    advice += '【影像附件中发票含抵扣联】；'
if invoice_time_error_flag:
    advice += '【发票不为本年度发票】；'

# web:
finalPay = finalPay.replace(',', '')
final_pay = round(float(finalPay), 2)
moneyFee = moneyFee.replace(',', '')
finalPayTax = moneyFee
final_pay_tax = round(float(finalPayTax), 2)

if invoice_exists:
    if round(pay_sum, 2) != round(final_pay, 2):
        delta = abs(round(final_pay - pay_sum, 2))
        advice += '【总金额不一致, 差额%s】；' % str(delta)
    if round(taxSum, 2) != round(final_pay_tax, 2):
        delta = abs(round(final_pay_tax - taxSum, 2))
        advice += '【税额不一致, 差额%s】；' % str(delta)
# 2021/1/15 ------------------------------


question_list = list(set(question_list))
if "不一致" in advice or "没有" in advice or "超仓" in advice:
    if len(question_list) == 0:
        pass
    else:
        a = ""
        for i in question_list:
            i = str(i)
            a += i + ','
        a = a[:-1]
        advice += '【请检查第{}张影像】；'.format(a)

# if advice_first == advice:
#     advice = advice + '【没有检测到发票】；'
listIata = totalSum

# 原有逻辑
# if "发票有盖章" in advice or "发票没有盖章" in advice:
#     advice = advice.replace("没有检测到发票；", "")
# else:
#     advice = advice + "没有检测到发票；"
#
# if "没有发票联；" in advice:
#     advice += "没有检测到发票；"


# 核对明细中的税额与专票增值税额
try:
    moneyFee = float(moneyFee)
except:
    moneyFee = 0
try:
    feeSum = float(feeSum)
except:
    feeSum = 0

try:
    if round(float(taxSum), 2) == round(float(moneyFee), 2):
        print("专票税额正常")
    elif round(float(taxSum), 2) == 0:
        print("专票税额正常")
    else:
        advice = advice + "【专票税额待核查】；"
except:
    pass

# 核对明细中的应付金额与所有发票的价税合计
try:
    if round(float(feeSum), 2) <= round(float(totalSum), 2):
        # float(totalSum)
        print("应付金额正常")
    elif round(float(totalSum), 2) == 0:
        print("应付金额正常")
    else:
        advice = advice + "【应付金额待核查】；"
except:
    pass

print(advice)

# except Exception as e:
#     print(e)
#     advice = advice + "没有检测到发票；"
# advice = advice.split("；")
# advice = list(set(advice))
# setAdvice = "；".join(advice)


if "没有检测到发票；" not in advice:
    taxSum = round(float(taxSum), 2)
    totalSum = round(float(totalSum) * 100) / 100.0
    if invoice_exists:
        advice = advice + "发票金额：" + str(totalSum) + ",专票税额：" + str(taxSum)
else:
    advice = advice.replace("没有检测到发票；", "")
    advice = advice.replace("【没有检测到发票】；", '')

if not invoice_exists:
    advice += "【没有检测到发票】；"
# 临时逻辑
if payee in ['中交（天津）疏浚工程有限公司', '中交天津航道局有限公司', '上海振华重工（集团）股份有限公司', '中交第一航务工程勘察设计院有限公司', '中交水运规划设计院有限公司', '中交一航局第一工程有限公司',
             '中交第一航务工程局有限公司'] or "中交" in payee:
    advice += "【暂停付款，打回本地】;"

data['data']['verifyResult'] = advice

approveopinions = data['data'].get('verifyResult', '')

# 摘要
abstract_list = baseInfo.get('abstract_list')
# 费用说明
fee_desc = baseInfo.get('fee_desc')
zip_abs_fee = zip(abstract_list, fee_desc)
new_abstract_list = list(map(lambda x: len(x[0].strip()) > 0 and x[0].strip() or x[1].strip(), zip_abs_fee))

# 摘要判断是否超过12个字，并且判断是否关联预付款单
abstract_length_error_list = list(map(lambda x: len(x) > 12, new_abstract_list))
abstract_relation_list = list(map(lambda x: x.find('结转') > -1 or x.find('核销') > -1, new_abstract_list))

if True in abstract_length_error_list:
    approveopinions += '【摘要字数大于十二字】；'
if True in abstract_relation_list:
    topay_no = baseInfo.get('预付款单号')
    if topay_no == '...' or '':
        approveopinions += '【单据未关联预付款单】；'

approveopinions = re.sub(r'[；，,]{2,}', '；', approveopinions)
approveopinions = re.sub(r'(.*?)【(审批流程无误；)】(.*)', r'\1\2\3', approveopinions)

p = re.compile('【(.*?)】')
L = p.findall(approveopinions)

for item in L:
    newItem = item.replace('；', '，').strip('，')
    approveopinions = approveopinions.replace(item, newItem)

approveopinions = approveopinions.replace('找不到封面页；请核实；', '【找不到封面页，请核实】；')

pattern1 = re.compile(r'([^【】]*)(【[^【】]*?】)([^【】]*)')
pattern2 = re.compile(r'(机器人试运行，审批意见：)(.*)')
pattern3 = re.compile(r'；{2,}')

L = []
for i in pattern1.finditer(approveopinions):
    L.append(i.group(2))

approveopinions = pattern1.sub(r'\1\3', approveopinions)
approveopinions = pattern2.sub(r'\1%s；\2' % ''.join(L), approveopinions)
approveopinions = pattern3.sub('；', approveopinions).strip(',').strip('，')
approveopinions = approveopinions.replace('【提示：机器人试运行，；】', '')
data['data']['verifyResult'] = approveopinions


def record_runtime_data(runtime_data, name):
    with open(os.path.join(invoice_dir, name) + '.json', 'w', encoding='utf-8') as f:
        json.dump(runtime_data, f)


now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
with open(os.path.join(log_dir, 'OCR记录.txt'), 'a', encoding='gbk') as f:
    f.write('单据编号: ' + No + '\n')
    f.write('\n'.join(url_dict_new) + '\n')
    f.write(advice + '\n')
    record_runtime_data(log_list, 'ocr')
    record_runtime_data(data, '审批流')
    record = ['[', now, ']', '图片数量%s' % len(url_dict_new), '处理完成\n']
    f.write(''.join(record))
flow = json.dumps(data)