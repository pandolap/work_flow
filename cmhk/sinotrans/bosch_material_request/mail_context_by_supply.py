#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# 根据供应商组织邮件内容
import os

supply = {}

# 映射的供应商邮箱
supplier_email = {
    "鼎立": "aoyucs@163.com",
    "美盈森": "Fupj@szmys.com",
    "裕同": "53237761@qq.com",
    "王子新材": "cssales2@szwzxc.com",
}


def check_attach(files):
    if files is None or files == []:
        raise Exception("程序异常-这个供货商的供货单为空")
    for file in files:
        if not os.path.exists(file):
            raise FileExistsError("程序异常—找不到供货单：<{}>".format(file))


def assign_mailbox(supply_en):
    # 获取当前供应商名称
    supply_name = supply_en.get("key")
    email_box = supplier_email.get(supply_name, None)
    if email_box is None:
        return None
    mail = dict()
    # 获取数据
    file_list = supply_en.get("value")

    mail_title = "供应商{}供货单".format(supply_name)
    mail_context = """
    Dear ALL,
    系统发送供货单邮件，请勿回复。有任何问题请联系：？
    """
    # 检查一下附件：
    check_attach(file_list)
    mail.setdefault("title", mail_title)
    mail.setdefault("body", mail_context)
    mail.setdefault("attach", file_list)
    mail.setdefault("mail", email_box)

    return mail


email_entity = assign_mailbox(supply)
