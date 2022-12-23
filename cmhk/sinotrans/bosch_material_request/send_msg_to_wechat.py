#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# 将异常信息通过微信通知客户

from wxauto import WeChat


# 获取微信客户端
wx_app = WeChat()

# # 获取会话列表
# session_list = wx_app.GetSessionList()
#
# print(session_list)
# msgs = wx_app.GetAllMessage
#
# for msg in msgs:
#     print("{} : {}".format(*msg))


print("======================")

# 向某人发送消息

msg = "测试发送"

who = "自己"

wx_app.ChatWith(who)
wx_app.SendMsg(msg)
