#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# 入参
missing = ''

# start
context = """
Dear 业务老师，
\n\t汽贸单证中心RPA流程-许可证申请运行结束，流程运行成功。
"""

if len(missing) > 0:
    context += "\t本次运行，解析文件有如下单号未找到匹配合同：\n"
    for con in missing:
        context += '\t' + str(con) + '\n'
# end
