#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Description 判断是否到启动时间

from datetime import datetime, timedelta

# ARGS!>

start_time = "18:00:00"


# START:>

def get_today_startup_time(time_str):
    current_date = datetime.now().strftime("%Y-%m-%d")
    today_startup_time_str = "{} {}".format(current_date, time_str)
    today_startup_time = datetime.strptime(today_startup_time_str, "%Y-%m-%d %H:%S:%M")
    return today_startup_time


def judge_whether_to_start(time_str):
    flag = False
    current_time = datetime.now()
    today_startup_time = get_today_startup_time(time_str)
    _startup_time = today_startup_time + timedelta(minutes=5)
    if today_startup_time <= current_time <= _startup_time:
        flag = True
    return flag


is_startup = judge_whether_to_start(start_time)
print(is_startup)
# END$>
