#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Description 邮件信息收集
import os

# ARGS

g_err_image = ""
input_file_path = r"C:\RPA\招商_招投标中心_交易明细导入导出\output\20221205\银行账户交易明细导入2022-12-05.xlsx"
err_date = []
ex_msg = "程序异常-我也不知道啥问题"
step_name = ""
is_err_end = False
result = {}


# START

def success_process(out_file, error_date):
    enclosures = []
    if not os.path.exists(out_file):
        raise FileNotFoundError("程序异常-导入文件缺失：找不到导入文件地址")
    else:
        enclosures.append(out_file)
    title = "【招投标-交易明细导入导出RPA流程】运行成功结果反馈"
    context = """
    Dear 业务老师，
    \n\t招投标中心RPA流程-交易明细导入导出运行结束，导入结果数据请查看附件。
    """
    if error_date:
        context += "\n\t运行过程中有如下日期数据下载失败，请联系运维人员或重新运行流程："
        for date in error_date:
            context += "\n\t" + date
    return title, context, enclosures


def fail_process(image_path, ex, out_file):
    title = "【招投标-交易明细导入导出RPA流程】运行失败结果反馈"
    context = """
    Dear 业务老师，
    \n\t招投标中心RPA流程-交易明细导入导出运行结束，流程运行失败，具体原因请查看异常截图。
    \n\t请重新启动或者联系运维人员！
    \n\t异常提示信息：%s 步骤，%s
    """ % (step_name, ex)
    enclosures = []
    if os.path.exists(image_path):
        enclosures.append(image_path)
    if os.path.exists(out_file):
        enclosures.append(out_file)
    return title, context, enclosures


def get_email_info(image_path, error_date, ex, out_file):
    # 判断是否运行成功
    if not is_err_end:
        # 失败
        (title, context, enclosures) = fail_process(image_path, ex, out_file)
    else:
        # 成功
        (title, context, enclosures) = success_process(out_file, error_date)
    return title, context, enclosures


# END$>
(mail_title, mail_context, enclosure) = get_email_info(g_err_image, err_date, result, input_file_path)

print(mail_title)
print(mail_context)
print(enclosure)
