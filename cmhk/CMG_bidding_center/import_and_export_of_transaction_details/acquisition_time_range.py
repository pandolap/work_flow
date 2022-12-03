#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Description 取得时间范围
from datetime import datetime

# ARGS!>
date = "2022-10-20"


def date_fmt(str_date):
    return datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")


def get_time_range(in_date):
    start = "{} 00:00:00".format(in_date)
    end = "{} 23:59:59".format(in_date)
    # 格式化
    start = date_fmt(start)
    end = date_fmt(end)
    return start, end


(start_time, end_time) = get_time_range(date)
print(start_time)
print(end_time)
