#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# 入参
exception_dict = {}
message = ""


# start
def exception_dealing(msg):
    global exception_dict
    if msg is None or msg == '':
        short_name = '其他错误'
    if msg.find('Element not found') > -1:
        short_name = 'Element not found'
    else:
        short_name = msg[:20]

    exception_dict[short_name] = exception_dict.get(short_name, 0) + 1

    rs = dict()
    for k, v in exception_dict.items():
        if v > 2:
            rs['exception_name'] = short_name
            rs['retry'] = False
            rs['exception_detail'] = msg
            break
    return rs


result = exception_dealing(message)
# end
