#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re
import json
import time
import hmac
import base64
import hashlib
import requests
from requests_toolbelt import MultipartEncoder

DEBUG = __name__ == '__main__'

# 获取工作流中的数据
data = json.loads(flow)

# 审批意见分类

correct_approval = ''
err_approval = ''

SIGN_SK = '5e278fb467e94d2e9c9241183c6ac0c5'
SIGN_AK = '27e28e8ea93b44d69c21d39189a7e775'


def get_header() -> dict:
    timestamp = int(time.time() * 1000)
    data = '\ntimestamp:' + str(timestamp)
    hashing = hmac.new(bytes(SIGN_SK, encoding='utf-8'), bytes(data.strip('&'), encoding='utf-8'),
                       hashlib.sha1).digest()
    sign = base64.b64encode(hashing)
    headers = {'timestamp': str(timestamp), 'Authorization': SIGN_AK + ':' + bytes.decode(sign)}
    return headers


def ocr_res_export(target_path: str, result: dict) -> None:

    pass


def get_images_result(asset_code: str) -> dict:
    """ 获取影像图片信息 """
    url1 = f'https://gip.cmft.com/gip-api/v1/images/{asset_code}'
    headers = get_header()
    res = requests.get(url1, headers=headers)
    if res.status_code == 200:
        return res.json()
    return {"识别失败": res.text}


def get_ocr_text(img_url: str) -> dict:
    if DEBUG:
        request_url = 'https://openapi.cmft.com/gateway/general1/1.0.0/api/pdfrec'
    else:
        request_url = 'http://openapi.cmft.com:8080/gateway/general1/1.0.0/api/pdfrec'

    payload = MultipartEncoder(
        fields={
            'file': ('img.jpg', requests.get(img_url).content),
            'content': 'multipart/form-data'
        }
    )

    print(payload.content_type)
    header = {
        'Authorization': 'ACCESSCODE 142717D9360287ED5BD1D03E1B6805D2',
        'x-Gateway-APIKey': 'b9180959-bb39-4f58-935a-bacc6a80d16c',
        'Content-Type': payload.content_type,
    }

    response = requests.post(request_url, data=payload, headers=header)
    return response.json()


def get_record_info(rx_no):
    if rx_no:
        res_out = get_images_result('E{}'.format(rx_no))
        url_list = []
        if res_out.get('code') == 'Y':
            url = None
            res_body = res_out.get('body')
            images_data = res_body.get('images')[0]
            for img in images_data.get('sameTypeList'):
                if img.get('treeId', 'A004') == 'A006':
                    url = img.get('url')
                    url_list.append(url)
            if len(url_list) > 0:
                return True, url_list
            else:
                return False, None
        else:
            return False, None
    else:
        return False, None


def forecast_match_amount(arg):
    res_amount = 0.0
    if arg:
        args = re.findall(r'\d+', arg)
        if len(args) == 1:
            res_amount = float(args[0])
        else:
            mantissa = len(args[-1])
            if mantissa == 2:
                # 正常小数位
                res_amount = float('{}.{}'.format(''.join(args[:-1]), args[-1]))
            else:
                # 拼接整数
                res_amount = float(''.join(args))
    return res_amount


def get_image_amount(urls):
    is_selected = None
    info_list = []
    # 成交金额
    deal_amount = 0.0
    # 预算金额
    budget_amount = 0.0
    for url in urls:
        res = get_ocr_text(url)
        if res.get('code', 'N') == 'Y':
            ocr_detail = res.get('details', '')[0]
            lines = ocr_detail.get('context').get('lines')
            for line in lines:
                if '中选' in line:
                    is_selected = True
                    break
                if '备案' in line:
                    is_selected = False
                    break
            if is_selected == None:
                continue
            else:
                info_list = lines
                break
    if is_selected:
        # 中选
        is_budget = False
        is_deal = False
        for line in info_list:
            if '成交金额' in line:
                is_deal = True
            if '预算价' in line:
                is_budget = True
            if is_deal:
                if re.findall(r'\d+', line):
                    deal_amount = forecast_match_amount(line)
                    is_deal = False
            if is_budget:
                if re.findall(r'\d+', line):
                    budget_amount = forecast_match_amount(line)
                    is_budget = False
    else:
        # 备案
        is_budget = False
        is_deal = False
        for line in info_list:
            if '预算价' in line:
                is_budget = True
            if "合同金额" in line:
                is_deal = True
            if is_deal:
                if re.findall(r'\d+', line):
                    deal_amount = forecast_match_amount(line)
                    is_deal = False
            if is_budget:
                if re.findall(r'\d+', line):
                    budget_amount = forecast_match_amount(line)
                    is_budget = False

    return is_selected, deal_amount, budget_amount


def amount_update(amount):
    try:
        if amount:
            res = 0.0
        else:
            res = float(amount)
    except Exception:
        is_decimal_point = False
        if ',' in amount:
            amount = amount.replace(',', '')
        if '，' in amount:
            amount = amount.replace('，', '')
        if '.' in amount:
            is_decimal_point = True
            amount = amount.replace('.', '')
        if is_decimal_point:
            amount = "{}.{}".format(amount[:-2], amount[-2:])
        res = float(amount)
    return res


# 首先获取将要调用接口的单号编码
base_info = data.get('data').get('baseInfo')
invoice_no = base_info.get('单据编号', '')

(selected_filed, ocr_list) = get_record_info(invoice_no)
deal = None

if selected_filed:
    (is_select, deal, budget) = get_image_amount(ocr_list)
    deal = amount_update(deal)
    budget = amount_update(budget)
    # 比较
    if is_select == True:
        # 中选
        pass
    elif is_select == False:
        # 备案
        if float(budget) == 0.0:
            err_approval += '【未提取到预算金额，请人工校验】；'
        else:
            if float(budget) >= float(deal):
                correct_approval += '不超出预算；'
            else:
                err_approval += '【超出预算】；'
    else:
        # 山野没有
        selected_filed = False

# 其次获取法务信息
this_pay = base_info.get('本次支付金额', '')
total_pay = base_info.get('累计支付金额', '')

if this_pay == '' and total_pay == '':
    err_approval += '【未查到法务信息】；'
else:
    if this_pay == '':
        this_pay = 0
    if total_pay == '':
        total_pay = 0
    legal = float(this_pay) + float(total_pay)
    correct_approval += '含本单合计：{}元；'.format(str(round(legal, 2)))
    if selected_filed:
        if float(deal) < legal:
            err_approval += '【超额支付】；'
        else:
            correct_approval += '未超额支付；'
    else:
        pass

# 将审批结果加入工作流中
data['data']['verifyResult'] += err_approval + correct_approval

flow = json.dumps(data)
