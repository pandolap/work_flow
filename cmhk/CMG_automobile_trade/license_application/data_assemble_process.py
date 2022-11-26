#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# 入参
import re

contract_data_list = [{'合同单号': '220230QMJK87SD0460LC', '签订日期': '2022-09-29', '总金额': '366259.00', '规格型号': [
    ['2022 RAM 1500 TRX CREW CAB 4X4', '2022 RAM 1500 TRX CREW CAB 4X4', '1', 'THE UNITED STATES', '\nCAD 131770.00',
     '\nCAD 131770.00'],
    ['2022 TOYOTA  TUNDRA', '2022 TOYOTA  TUNDRA', '1', 'THE UNITED STATES', '\nCAD 84150.00', '\nCAD 84150.00'],
    ['2022 TOYOTA  TUNDRA', '2022 TOYOTA  TUNDRA', '1', 'THE UNITED STATES', '\nCAD 80550.00', '\nCAD 80550.00'],
    ['2022 Ford Bronco', '2022 Ford Bronco', '1', 'THE UNITED STATES', '\nCAD 69789.00', '\nCAD 69789.00']]}]
list_data = [[{'贸易国': '加拿大', '原产地国': '美国', '报关口岸': '天津', '商品编码': 8704310000.0, '币种': '加币', '规格型号': '丰田 坦途', '台数': 1.0,
               '单价': 53990.0, '外贸合同号': '220230QMJK87SD0460LC', '到港日期': '2022-11-09', '贸易商英文': 'CARMAX AUTO GROUP LTD',
               '贸易商中文': '卡马克斯汽车集团有限公司', '生产商英文': 'SOHU INC', '生产商中文': '思虎公司', '生产国': '美国'}], [
                 {'贸易国': '加拿大', '原产地国': '美国', '报关口岸': '天津', '商品编码': 8704310000.0, '币种': '加币', '规格型号': '丰田 坦途',
                  '台数': 1.0, '单价': 53990.0, '外贸合同号': '220230QMJK87SD0460LC', '到港日期': '2022-11-09',
                  '贸易商英文': 'CARMAX AUTO GROUP LTD', '贸易商中文': '卡马克斯汽车集团有限公司', '生产商英文': 'SOHU INC', '生产商中文': '思虎公司',
                  '生产国': '美国'}]]

# start
licence_list = []
missing = []

currency_dict = {
    '记帐瑞士法郎': 'ASF',
    '奥地利先令': 'ATS',
    '澳大利亚元': 'AUD',
    '贸易比利时法郎': 'BEF',
    '巴西雷亚尔': 'BRL',
    '加拿大元': 'CAD',
    '瑞士法郎': 'CHF',
    '人民币元': 'CNY',
    '德国马克': 'DEM',
    '丹麦克朗': 'DKK',
    '阿尔及利亚第纳尔': 'DZD',
    '欧元': 'EUR',
    '芬兰马克': 'FIM',
    '法国法郎': 'FRF',
    '英镑': 'GBP',
    '港元': 'HKD',
    '印度尼西亚卢比': 'IDR',
    '印度卢比': 'INR',
    '伊朗里亚尔': 'IRR',
    '意大利里拉': 'ITL',
    '约旦第纳尔': 'JOD',
    '日元': 'JPY',
    '韩国元': 'KRW',
    '科威特第纳尔': 'KWD',
    '澳门元': 'MOP',
    '墨西哥比索': 'MXN',
    '马来西亚林吉特': 'MYR',
    '荷兰盾': 'NLG',
    '挪威克朗': 'NOK',
    '尼泊尔卢比': 'NPR',
    '新西兰元': 'NZD',
    '菲律宾比索': 'PHP',
    '巴基斯坦卢比': 'PKR',
    '俄国卢布': 'RUR',
    '特别提款权': 'SDR',
    '瑞典克朗': 'SEK',
    '新加坡元': 'SGD',
    '苏联卢布': 'SUR',
    '泰国铢': 'THB',
    '台湾元': 'TWD',
    '坦桑尼亚先令': 'TZS',
    '美元': 'USD'
}


def check_currency(in_currency):
    h_flag = in_currency[0]
    if u'\u0041' <= h_flag <= u'\u005a' or u'\u0061' <= h_flag <= u'\u007a':
        if in_currency in currency_dict.values():
            return in_currency
        else:
            raise Exception('币种类型错误：%s' % in_currency)
    else:
        currency_out = currency_dict.get(in_currency, in_currency[0])
        return currency_out


def proces_amount_merge(invoice_list):
    """
    检查传进来的申请单列表中是否有单价相同并且相同型号的数据，进行合并后返回新的列表
    :param invoice_list: 待处理的申请单列表
    :return: 合并后的列表
    """
    # 获取列表长度
    list_length = len(invoice_list)
    if list_length == 0:
        raise Exception('程序异常-数据整合：传入的清单为空')
    if list_length == 1:
        return invoice_list
    # 合并后的新列表
    merge_list = []
    # 存放重复的set集合
    give_list = []

    for i in range(list_length):
        flag = False
        gives = set()
        # 如果当前选择的比对下标再相同数据集中就跳过该下标
        for give in give_list:
            if i in give:
                flag = True
                break
        if flag:
            continue
        for j in range(list_length - 1, i, -1):
            # 如果对比下标出现再set中则跳过当前循环
            if j in gives:
                continue
            # 如果比对相同，将两个下标存入set中，使之后的循环忽略
            if invoice_list[i].get('规格型号') == invoice_list[j].get('规格型号') \
                    and invoice_list[i].get('单价') == invoice_list[j].get('单价'):
                gives.add(i)
                gives.add(j)
        product_sum = 0
        # 聚合相同的数据台数之和
        for x in gives:
            product_sum += invoice_list[x].get('台数')
        # 如果有相同的数据
        if len(gives) > 0:
            # 加入相同数据的数据集
            give_list.append(gives)
            # 统计到的台数进行赋值
            invoice_list[i]['台数'] = product_sum
        # 将最终的数据加入新的列表中
        merge_list.append(invoice_list[i])
    # 返回新的列表
    return merge_list


for list_ in list_data:
    temp_list = list_[0]
    contract_no = temp_list.get('外贸合同号')
    contract = {}
    for cont in contract_data_list:
        if cont.get('合同单号') in contract_no:
            contract = cont
            break
    if contract != {}:
        trading_country = temp_list.get('贸易国')
        country_origin = temp_list.get('原产地国')
        place_clearance = temp_list.get('报关口岸')
        product_code = temp_list.get('商品编码')
        unit_price = temp_list.get('单价')
        is_card = len(list_)
        currency = check_currency(temp_list.get('币种'))

        arrival_date = temp_list.get('到港日期')

        for cont in contract_data_list:
            if cont.get('合同单号') == contract_no:
                contract = cont
                break
        # 品牌
        specs_list = contract.get('规格型号')
        specs = ''
        for spc in specs_list:
            spci = '.'.join(re.findall(r'\d+', str(spc[-1])))
            if float(unit_price) == float(spci):
                specs = spc[0]
                break

        tmp = {
            '贸易国': trading_country,
            '外贸合同号': contract_no,
            '清单数据': proces_amount_merge(list_),
            '合同数据': contract,
            '原产地国': country_origin,
            '报关口岸': place_clearance,
            '商品编码': product_code,
            '一证': is_card,
            '币种': currency,
            '到港日期': arrival_date,
            '签订日期': contract.get('签订日期'),
            '总金额': contract.get('总金额'),
            '贸易商英文': temp_list.get('贸易商英文'),
            '贸易商中文': temp_list.get('贸易商中文'),
            '生产商英文': temp_list.get('生产商英文'),
            '生产商中文': temp_list.get('生产商中文'),
            '生产国': temp_list.get('生产国'),
            '品牌': specs
        }

        licence_list.append(tmp)
    else:
        missing.append(temp_list.get('外贸合同号'))

missing = list(set(missing))

print('许可证列表' + str(licence_list))
print('缺失合同列表：' + str(missing))
# end
