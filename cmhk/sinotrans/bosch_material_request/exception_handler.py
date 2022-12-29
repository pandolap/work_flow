#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# 异常处理

# 会传入的参数

ex_msg = ""
is_business_ex = False
exception_dict = {}
# is_end = ""
step_name = ""

# 被过滤掉的步骤 => 如果有在过滤中的步骤名则直接结束流程
step_filter = [

]


def controller(step, msg, ex_type, exceptions):
    if ex_type:
        if msg.startWith("业务异常"):
            msg = msg.split("-")[1]
    else:
        # 系统异常
        # 先检测是否带有程序异常开头
        if msg.startWith("程序异常"):
            msg = msg.split("-")[1]

    if step in step_filter:
        return True, msg, {}, exceptions

    ex_key = msg[:20]
    # 生成结果处理
    result = exceptions.get(ex_key, dict())
    result["detail"] = msg
    result["count"] = result.get("count", 0) + 1

    if result.get("count") > 3:
        print("当前异常处理已经到达最大阈值,放弃重试进入流程失败!")
        return True, msg, {}, exceptions
    else:
        return False, msg, result, exceptions


(is_end, ex_msg, res, exception_dict) = controller(step_name, ex_msg, is_business_ex, exception_dict)
# END
