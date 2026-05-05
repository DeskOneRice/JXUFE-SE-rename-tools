# encoding: utf-8
# @author: 花辞树
# @file:public_tools.py
# @time: 2024/3/6 19:48
# @desc: ...

# 计算窗口位置，使窗口显示在屏幕中央
def set_window_geometry_center(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    # print(screen_width, screen_height)
    pos_x = (screen_width - width) // 2
    pos_y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

