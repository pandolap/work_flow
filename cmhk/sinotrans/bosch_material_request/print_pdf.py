#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import tempfile
import win32api
import win32print

# filename = tempfile.mktemp(".pdf")

file_path = r"C:\Users\Administrator\Downloads\附件2：看板内容.pdf"

win32api.ShellExecute(
    0,
    "printto",
    file_path,
    '{}'.format(win32print.GetDefaultPrinter()),
    ".",
    0
)
