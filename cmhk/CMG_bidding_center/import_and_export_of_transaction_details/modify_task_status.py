#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Description 修改数据资产表任务状态
from datetime import datetime

# ARGS!>
# 数据资产表实体
task_list = {}
# 运行是否成功
is_success = True
# 异常信息文本
ex_msg = ""


# START:>

def modify_status(in_task_list, in_is_success, in_ex_msg=None):
    try:
        table_data = in_task_list['tableData']
        row_data = table_data[-1]

        task_stats = row_data.get("任务状态")
    except Exception as e:
        print("{ex}".format(ex=str(e)))
        return -1
    if task_stats == "已导入":
        raise Exception("程序异常-数据资产表修改：执行中的任务状态错误！")
    if task_stats == "":
        if in_is_success:
            row_data["任务状态"] = "已导入"
        else:
            if in_ex_msg is None:
                row_data["异常信息"] = "有异常但不知道是啥异常！"
            else:
                row_data["异常信息"] = in_ex_msg
    # 结束时间
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row_data["任务结束时间"] = end_time
    table_data[-1] = row_data
    task_list["tableData"] = table_data
    return 1


# END$>
modify_status(task_list, is_success, ex_msg)
# TEST?>
