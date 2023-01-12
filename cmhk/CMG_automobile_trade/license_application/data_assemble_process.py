#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# 入参
import re

contract_data_list = [{'合同单号': '220082QMJK87ZS0449TTLC', '签订日期': '2022-03-24', '总金额': '1370500.00', '规格型号': [[' Audi TT Coupe 40 TFSI（Lbis white/Cloth black）', 1, 38800, 38800], [' Audi TT Coupe 40 TFSI（Navarra Blue/Cloth black）', 3, 39300, 117900], [' Audi TT Coupe 40 TFSI（Floretttsilber/Cloth black）', 1, 39300, 39300], [' Audi TT Coupe 40 TFSI（Red/Cloth black）', 5, 39300, 196500], [' Audi TT Coupe 40 TFSI（Lbis white/Cloth black）', 2, 40200, 80400], [' Audi TT Coupe 40 TFSI（Black/Cloth black）', 4, 40800, 163200], [' Audi TT Coupe 40 TFSI（Navarra Blue/Cloth black）', 6, 40800, 244800], [' Audi TT Coupe 40 TFSI（Floretttsilber/Cloth black）', 2, 40800, 81600], [' Audi TT Coupe 40 TFSI（Red/Cloth black）', 10, 40800, 408000]]}, {'合同单号': '220250QMJK87ZS0487TT', '签订日期': '2022-11-04', '总金额': '111525.00', '规格型号': [['2022 MERCEDES BENZ S500\n', 'W1K6G6DB9NA152788', 'Germany', 1, 'USD 111,525.00', 'USD 111,525.00']]}, {'合同单号': '220264QMJK87ZS0464TT', '签订日期': '2022-11-28', '总金额': '159400.00', '规格型号': [['TOYOTA GRANVIA 3.5L PETROL A/T', 'JTNYM8AP0P8002453 ', 'JAPAN', 1, 'USD 51,700.00', 'USD 51,700.00'], ['TOYOTA GRANVIA 3.5L PETROL A/T', 'JTNYM8APXP8002413', 'JAPAN ', 1, 'UAD 51,700.00', 'USD 51,700.00'], ['TOYOTA GRANVIA 3.5L PETROL A/T', 'JTNYM3AP0P8002469', 'JAPAN', 1, ' USD 56,000.00', ' USD 56,000.00']]}, {'合同单号': '220252QMJK87ZS0466TT', '签订日期': '2022-11-08', '总金额': '268208.78', '规格型号': [['2023 CHEVROLET CHEYENNE ZR2', '3GCUD9EL0PG102904', 'THE UNITED STATES', 1, 66955.9, 66955.9], ['2023 CHEVROLET CHEYENNE ZR2', '3GCUD9EL9PG103453', 'THE UNITED STATES', 1, 67433.5, 67433.5], ['2023 CHEVROLET CHEYENNE ZR2', '3GCUD9EL9PG104182', 'THE UNITED STATES', 1, 66842.73, 66842.73], ['2023 CHEVROLET CHEYENNE ZR2', '3GCUD9EL1PG102295', 'THE UNITED STATES', 1, 66976.65, 66976.65]]}, {'合同单号': '220254QMJK87ZS0466TT', '签订日期': '2022-11-16', '总金额': '135066.96', '规格型号': [['2023 CHEVROLET CHEYENNE ZR2', '3GCUD9EL2PG104511', 'MEXICO', 1, 66616.39, 66616.39], ['2023 CHEVROLET CHEYENNE ZR2', '3GCUD9EL6PG104365', 'MEXICO', 1, 68450.57, 68450.57]]}, {'合同单号': '220271QMJK87ZS0464TT', '签订日期': '2023-12-14', '总金额': '159400.00', '规格型号': [['TOYOTA GRANVIA 3.5L PETROL A/T', 'JTNYM8AP4P8002522', 'JAPAN', 1, 51700, 51700], ['TOYOTA GRANVIA 3.5L PETROL A/T', 'JTNYM3AP4P8002488', 'JAPAN', 1, 51700, 51700], ['TOYOTA GRANVIA 3.5L PETROL A/T', 'JTNYM8APXP8002492', 'JAPAN', 1, 56000, 56000]]}]


list_data = [[{'贸易国': '墨西哥', '原产地国': '墨西哥', '报关口岸': '天津', '商品编码': 8704310000, '币种': 'USD', '规格型号': '雪佛兰CHEYENNE ZR2', '台数': 1, '单价': 66955.9, '外贸合同号': '220252QMJK87ZS0466TT', '到港日期': '2023-01-17', '贸易商英文': 'MEXICO AUTOMOBILE IMPORT AND EXPORT LEASING COMPANY S.A DE C.V', '贸易商中文': '墨西哥汽车进出口租赁公司', '生产商英文': '暂无', '生产商中文': '暂无', '生产国': '暂无'}, {'贸易国': '墨西哥', '原产地国': '墨西哥', '报关口岸': '天津', '商品编码': 8704310000, '币种': 'USD', '规格型号': '雪佛兰CHEYENNE ZR2', '台数': 1, '单价': 67433.5, '外贸合同号': '220252QMJK87ZS0466TT', '到港日期': '2023-01-17', '贸易商英文': 'MEXICO AUTOMOBILE IMPORT AND EXPORT LEASING COMPANY S.A DE C.V', '贸易商中文': '墨西哥汽车进出口租赁公司', '生产商英文': '暂无', '生产商中文': '暂无', '生产国': '暂无'}, {'贸易国': '墨西哥', '原产地国': '墨西哥', '报关口岸': '天津', '商品编码': 8704310000, '币种': 'USD', '规格型号': '雪佛兰CHEYENNE ZR2', '台数': 1, '单价': 66842.73, '外贸合同号': '220252QMJK87ZS0466TT', '到港日期': '2023-01-17', '贸易商英文': 'MEXICO AUTOMOBILE IMPORT AND EXPORT LEASING COMPANY S.A DE C.V', '贸易商中文': '墨西哥汽车进出口租赁公司', '生产商英文': '暂无', '生产商中文': '暂无', '生产国': '暂无'}, {'贸易国': '墨西哥', '原产地国': '墨西哥', '报关口岸': '天津', '商品编码': 8704310000, '币种': 'USD', '规格型号': '雪佛兰CHEYENNE ZR2', '台数': 1, '单价': 66976.65, '外贸合同号': '220252QMJK87ZS0466TT', '到港日期': '2023-01-12', '贸易商英文': 'MEXICO AUTOMOBILE IMPORT AND EXPORT LEASING COMPANY S.A DE C.V', '贸易商中文': '墨西哥汽车进出口租赁公司', '生产商英文': '暂无', '生产商中文': '暂无', '生产国': '暂无'}], [{'贸易国': '墨西哥', '原产地国': '墨西哥', '报关口岸': '天津', '商品编码': 8704310000, '币种': 'USD', '规格型号': '雪佛兰CHEYENNE ZR2', '台数': 1, '单价': 66616.39, '外贸合同号': '220254QMJK87ZS0466TT', '到港日期': '2023-01-17', '贸易商英文': 'MEXICO AUTOMOBILE IMPORT AND EXPORT LEASING COMPANY S.A DE C.V', '贸易商中文': '墨西哥汽车进出口租赁公司', '生产商英文': '暂无', '生产商中文': '暂无', '生产国': '暂无'}, {'贸易国': '墨西哥', '原产地国': '墨西哥', '报关口岸': '天津', '商品编码': 8704310000, '币种': 'USD', '规格型号': '雪佛兰CHEYENNE ZR2', '台数': 1, '单价': 68450.57, '外贸合同号': '220254QMJK87ZS0466TT', '到港日期': '2023-01-17', '贸易商英文': 'MEXICO AUTOMOBILE IMPORT AND EXPORT LEASING COMPANY S.A DE C.V', '贸易商中文': '墨西哥汽车进出口租赁公司', '生产商英文': '暂无', '生产商中文': '暂无', '生产国': '暂无'}], [{'贸易国': '美国', '原产地国': '德国', '报关口岸': '天津', '商品编码': 8703236110, '币种': 'USD', '规格型号': '奔驰S500', '台数': 1, '单价': 111525.0, '外贸合同号': '220250QMJK87ZS0487TT', '到港日期': '2022-12-31', '贸易商英文': 'IBEE TRADING INC', '贸易商中文': '艾比贸易公司', '生产商英文': 'MAZZ AUTOSPORTS INC', '生产商中文': '麦哲汽车运动有限公司', '生产国': '美国'}], [{'贸易国': '阿联酋', '原产地国': '日本', '报关口岸': '江阴、天津', '商品编码': 8703241310, '币种': 'USD', '规格型号': '丰田GRANVIA', '台数': 1, '单价': 51700.0, '外贸合同号': '220264QMJK87ZS0464TT', '到港日期': '2023-01-10', '贸易商英文': 'CAR TO POINT AUTOMOBILE FZE.', '贸易商中文': '车对点汽车有限公司', '生产商英文': '暂无', '生产商中文': '暂无', '生产国': '暂无'}, {'贸易国': '阿联酋', '原产地国': '日本', '报关口岸': '江阴、天津', '商品编码': 8703241310, '币种': 'USD', '规格型号': '丰田GRANVIA', '台数': 1, '单价': 56000.0, '外贸合同号': '220264QMJK87ZS0464TT', '到港日期': '2023-01-10', '贸易商英文': 'CAR TO POINT AUTOMOBILE FZE.', '贸易商中文': '车对点汽车有限公司', '生产商英文': '暂无', '生产商中文': '暂无', '生产国': '暂无'}, {'贸易国': '阿联酋', '原产地国': '日本', '报关口岸': '江阴、天津', '商品编码': 8703241310, '币种': 'USD', '规格型号': '丰田GRANVIA', '台数': 1, '单价': 51700.0, '外贸合同号': '220264QMJK87ZS0464TT', '到港日期': '2023-01-12', '贸易商英文': 'CAR TO POINT AUTOMOBILE FZE.', '贸易商中文': '车对点汽车有限公司', '生产商英文': '暂无', '生产商中文': '暂无', '生产国': '暂无'}], [{'贸易国': '阿联酋', '原产地国': '日本', '报关口岸': '江阴、天津', '商品编码': 8703241310, '币种': 'USD', '规格型号': '丰田GRANVIA', '台数': 1, '单价': 51700.0, '外贸合同号': '220271QMJK87ZS0464TT', '到港日期': '2023-01-12', '贸易商英文': 'CAR TO POINT AUTOMOBILE FZE.', '贸易商中文': '车对点汽车有限公司', '生产商英文': '暂无', '生产商中文': '暂无', '生产国': '暂无'}, {'贸易国': '阿联酋', '原产地国': '日本', '报关口岸': '江阴、天津', '商品编码': 8703241310, '币种': 'USD', '规格型号': '丰田GRANVIA', '台数': 1, '单价': 56000.0, '外贸合同号': '220271QMJK87ZS0464TT', '到港日期': '2023-01-12', '贸易商英文': 'CAR TO POINT AUTOMOBILE FZE.', '贸易商中文': '车对点汽车有限公司', '生产商英文': '暂无', '生产商中文': '暂无', '生产国': '暂无'}, {'贸易国': '阿联酋', '原产地国': '日本', '报关口岸': '江阴、天津', '商品编码': 8703241310, '币种': 'USD', '规格型号': '丰田GRANVIA', '台数': 1, '单价': 51700.0, '外贸合同号': '220271QMJK87ZS0464TT', '到港日期': '2023-01-12', '贸易商英文': 'CAR TO POINT AUTOMOBILE FZE.', '贸易商中文': '车对点汽车有限公司', '生产商英文': '暂无', '生产商中文': '暂无', '生产国': '暂无'}], [{'贸易国': '德国', '原产地国': '匈牙利', '报关口岸': '天津', '商品编码': 8703234110, '币种': 'EUR', '规格型号': '奥迪TT', '台数': 1, '单价': 40200.0, '外贸合同号': '220082QMJK87ZS0449TTLC-2', '到港日期': '2023-01-08', '贸易商英文': 'REMAX Autohandels GmbH', '贸易商中文': '瑞麦克斯汽车销售有限公司', '生产商英文': 'MAZZ AUTOSPORTS INC', '生产商中文': '麦哲汽车运动有限公司', '生产国': '美国'}, {'贸易国': '德国', '原产地国': '匈牙利', '报关口岸': '天津', '商品编码': 8703234110, '币种': 'EUR', '规格型号': '奥迪TT', '台数': 1, '单价': 40800.0, '外贸合同号': '220082QMJK87ZS0449TTLC-2', '到港日期': '2023-01-08', '贸易商英文': 'REMAX Autohandels GmbH', '贸易商中文': '瑞麦克斯汽车销售有限公司', '生产商英文': 'MAZZ AUTOSPORTS INC', '生产商中文': '麦哲汽车运动有限公司', '生产国': '美国'}, {'贸易国': '德国', '原产地国': '匈牙利', '报关口岸': '天津', '商品编码': 8703234110, '币种': 'EUR', '规格型号': '奥迪TT', '台数': 1, '单价': 40800.0, '外贸合同号': '220082QMJK87ZS0449TTLC-2', '到港日期': '2023-01-08', '贸易商英文': 'REMAX Autohandels GmbH', '贸易商中文': '瑞麦克斯汽车销售有限公司', '生产商英文': 'MAZZ AUTOSPORTS INC', '生产商中文': '麦哲汽车运动有限公司', '生产国': '美国'}, {'贸易国': '德国', '原产地国': '匈牙利', '报关口岸': '天津', '商品编码': 8703234110, '币种': 'EUR', '规格型号': '奥迪TT', '台数': 1, '单价': 40800.0, '外贸合同号': '220082QMJK87ZS0449TTLC-2', '到港日期': '2023-01-08', '贸易商英文': 'REMAX Autohandels GmbH', '贸易商中文': '瑞麦克斯汽车销售有限公司', '生产商英文': 'MAZZ AUTOSPORTS INC', '生产商中文': '麦哲汽车运动有限公司', '生产国': '美国'}, {'贸易国': '德国', '原产地国': '匈牙利', '报关口岸': '天津', '商品编码': 8703234110, '币种': 'EUR', '规格型号': '奥迪TT', '台数': 1, '单价': 40800.0, '外贸合同号': '220082QMJK87ZS0449TTLC-2', '到港日期': '2023-01-08', '贸易商英文': 'REMAX Autohandels GmbH', '贸易商中文': '瑞麦克斯汽车销售有限公司', '生产商英文': 'MAZZ AUTOSPORTS INC', '生产商中文': '麦哲汽车运动有限公司', '生产国': '美国'}, {'贸易国': '德国', '原产地国': '匈牙利', '报关口岸': '天津', '商品编码': 8703234110, '币种': 'EUR', '规格型号': '奥迪TT', '台数': 1, '单价': 40800.0, '外贸合同号': '220082QMJK87ZS0449TTLC-2', '到港日期': '2023-01-08', '贸易商英文': 'REMAX Autohandels GmbH', '贸易商中文': '瑞麦克斯汽车销售有限公司', '生产商英文': 'MAZZ AUTOSPORTS INC', '生产商中文': '麦哲汽车运动有限公司', '生产国': '美国'}], [{'贸易国': '德国', '原产地国': '匈牙利', '报关口岸': '天津', '商品编码': 8703234110, '币种': 'EUR', '规格型号': '奥迪TT', '台数': 1, '单价': 40800.0, '外贸合同号': '220082QMJK87ZS0449TTLC-2', '到港日期': '2023-01-08', '贸易商英文': 'REMAX Autohandels GmbH', '贸易商中文': '瑞麦克斯汽车销售有限公司', '生产商英文': 'MAZZ AUTOSPORTS INC', '生产商中文': '麦哲汽车运动有限公司', '生产国': '美国'}, {'贸易国': '德国', '原产地国': '匈牙利', '报关口岸': '天津', '商品编码': 8703234110, '币种': 'EUR', '规格型号': '奥迪TT', '台数': 1, '单价': 40800.0, '外贸合同号': '220082QMJK87ZS0449TTLC-2', '到港日期': '2023-01-08', '贸易商英文': 'REMAX Autohandels GmbH', '贸易商中文': '瑞麦克斯汽车销售有限公司', '生产商英文': 'MAZZ AUTOSPORTS INC', '生产商中文': '麦哲汽车运动有限公司', '生产国': '美国'}]]

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
            tmp_list = re.findall(r'\d+', str(spc[-2]))
            if len(tmp_list) > 2:
                spc_ = ''.join(tmp_list[:-1])
                spc_end = tmp_list[-1]
                tmp_list = [spc_, spc_end]
            spci = '.'.join(tmp_list)
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
