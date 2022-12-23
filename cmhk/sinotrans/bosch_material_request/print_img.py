#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# 打印图片

import win32print
import win32ui
from PIL import Image, ImageWin

img_path = r"C:\Users\Administrator\Downloads\附件2：看板内容_0.png"

printer_name = win32print.GetDefaultPrinter()
print(printer_name)
hDC = win32ui.CreateDC()
hDC.CreatePrinterDC(printer_name)


bmp = Image.open(img_path)

scale = 4.5

hDC.StartDoc(img_path)
hDC.StartPage()

dib = ImageWin.Dib(bmp)

scaled_width, scaled_height = [int(scale * i) for i in bmp.size]

x1 = 20
y1 = -30
x2 = x1 + scaled_width
y2 = y1 + scaled_height
dib.draw(hDC.GetHandleOutput(), (x1, y1, x2, y2))

hDC.EndPage()
hDC.EndDoc()
hDC.DeleteDC()
