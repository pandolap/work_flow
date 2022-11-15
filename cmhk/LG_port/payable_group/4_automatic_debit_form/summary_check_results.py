#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import re

data = json.loads(flow)

approveopinions = data['data'].get('verifyResult', '')
# approveopinions = re.sub(r'；+', '；', approveopinions)
approveopinions = re.sub(r'[；，,]{2,}', '；', approveopinions)


def insert_list_to_list(src_list, new_list, pos):
    if not new_list:
        return src_list
    pre = src_list[:pos]
    aft = src_list[pos:]
    return [*pre, *new_list, *aft]


def adjust_target(advice):
    import re
    p = re.compile(r'(?P<pre>[^【】]*)(?P<target>【[^【】]*】)*(?P<aft>[^【】]*)')
    result = []
    for s in advice.split('\n'):
        normal_list = []
        target_list = []
        for match in p.finditer(s):
            pre = match.group('pre') or ''
            target = match.group('target') or ''
            aft = match.group('aft') or ''
            normal_list.append(pre)
            normal_list.append(aft)
            target_list.append(target)

        if len(normal_list) > 0:
            if normal_list[0].find('机器人') > -1:
                head_list = list(map(lambda x: len(x) > 0 and x + '，' or '', normal_list[0].split('，')))
                normal_list = [*head_list, *normal_list[1:]]
                row = ''.join(insert_list_to_list(normal_list, target_list, 1))
                result.append(row)
            else:
                row = ''.join(insert_list_to_list(normal_list, target_list, 0))
                result.append(row)
        else:
            result.append(''.join(target_list))
    result = list(filter(lambda x: len(x) > 0, result))
    result = '\n'.join(result).replace('，；', '；')
    return result


# approveopinions = adjust_target(approveopinions)

data['element'] = {
    'element_position': '#approveopinions',
    'frame_position': [{'tag': 'iframe', 'num': 1}, {'tag': 'iframe', 'num': 0}, {'tag': 'frame', 'num': 1}],
    'value': approveopinions
}
data['control']['timeout'] = 10

flow = json.dumps(data)
