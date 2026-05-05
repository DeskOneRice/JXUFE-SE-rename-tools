# encoding: utf-8
# @author: 花辞树
# @file: window_func_rename.py
# @time: 2025/10/15 20:09
# @desc: 班会文件批量重命名工具 —— GUI 界面入口
import os
import sys
import tkinter as tk
from tkinter import filedialog, font, messagebox

# 导入自定义模块
import public_tools      # 通用工具函数（如窗口居中）
import func_rename       # 核心重命名逻辑（预览 + 执行）

def resource_path(relative_path):
    """ 获取资源文件的绝对路径，兼容 PyInstaller 打包 """
    try:
        # PyInstaller 打包后，资源会被解压到 _MEIPASS 临时目录
        base_path = sys._MEIPASS
    except AttributeError:
        # 未打包时，使用当前脚本所在目录
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class WindowFuncRename:
    """
    班会文件批量重命名窗口类
    功能：选择文件夹 → 输入班会主题 → 预览重命名效果 → 执行重命名
    设计原则：安全第一（必须先预览才能执行），操作清晰，防误触
    """
    def __init__(self):
        """
        初始化窗口组件
        :param parent_window: 父窗口对象（用于从主程序打开时传递上下文，当前未使用）
        """
        self.parent_window = None

        # 创建主窗口
        self.window_func_rename = tk.Tk()
        # 设置全局字体：Arial 14号，提升可读性
        self.window_func_rename.option_add("*Font", font.Font(family='Arial', size=14))

        # 设置窗口标题：
        # - 如果是从父窗口打开（比如主程序的下拉菜单），标题用菜单项文本
        # - 否则（直接运行本文件），标题用类名（方便调试）
        if self.parent_window is not None:
            self.window_func_rename.title(self.parent_window.combobox2.get())
        else:
            self.window_func_rename.title(self.__class__.__name__)

        icon_path = resource_path("resources/jxufe_logo.ico")
        self.window_func_rename.iconbitmap(icon_path)  # 必须是 .ico 格式

        # 设置窗口大小为 1000x500，并居中显示（调用公共工具函数）
        public_tools.set_window_geometry_center(self.window_func_rename, 1000, 500)

        # 提示标签：“当前文件夹：”
        self.label_dir_tip = tk.Label(
            self.window_func_rename,
            text="当前文件夹：",
            width=18,  # 固定宽度，对齐右侧内容
            anchor=tk.E  # 文字右对齐（靠右显示）
        )
        self.label_dir_tip.place(x=30, y=30)  # 绝对定位

        # 显示已选文件夹路径的标签（初始为“未选择”）
        self.var_label_dir_path = tk.StringVar()
        self.var_label_dir_path.set("---未选择文件夹---")
        self.label_dir_path = tk.Label(
            self.window_func_rename,
            text=self.var_label_dir_path.get(),
            anchor=tk.W
        )  # 该label使用textvariable参数会出bug，原因未知
        self.label_dir_path.place(x=210, y=30)

        # 存储用户选择的文件夹绝对路径（初始状态）
        self.dir_selected = "---未选择文件夹---"

        # “选择”按钮：弹出文件夹选择对话框
        self.btn_dir_selected = tk.Button(
            self.window_func_rename,
            width=5,
            text="选择",
            command=self.select_dir  # 点击触发 select_dir 方法
        )
        self.btn_dir_selected.place(x=210, y=60)

        # “打开”按钮：用系统默认方式打开已选文件夹（如资源管理器）
        self.btn_dir_open = tk.Button(
            self.window_func_rename,
            width=5,
            text="打开",
            command=self.open_dir
        )
        self.btn_dir_open.place(x=280, y=60)

        # 提示标签：“班会主题：”
        self.label_topic_tip = tk.Label(
            self.window_func_rename,
            text="班会主题：",
            width=18,
            anchor=tk.E
        )
        self.label_topic_tip.place(x=30, y=100)

        # 输入框：用户输入本次班会的主题（如“网络安全教育”）
        self.entry_topic = tk.Entry(self.window_func_rename, width=30)
        self.entry_topic.place(x=210, y=100)

        # “查看预期结果”按钮：生成并显示重命名后的文件名列表（不实际修改文件）
        self.btn_res_view = tk.Button(
            self.window_func_rename,
            width=13,
            text="查看预期结果",
            command=self.res_view
        )
        self.btn_res_view.place(x=210, y=130)

        # 提示标签：“预期结果：”
        self.label_res_tip = tk.Label(
            self.window_func_rename,
            text="预期结果：",
            width=18,
            anchor=tk.E
        )
        self.label_res_tip.place(x=30, y=170)

        # “批量命名”按钮：执行实际的重命名操作（需先预览）
        self.btn_rename = tk.Button(
            self.window_func_rename,
            width=10,
            text="批量命名",
            command=self.res_rename
        )
        self.btn_rename.place(x=360, y=130)

        # 创建一个框架（Frame），用于容纳文本框和滚动条
        self.frame_res_view = tk.Frame(self.window_func_rename)
        self.frame_res_view.place(x=210, y=170)

        # 多行文本框：显示预览的重命名结果（只读，不可编辑）
        self.text_res = tk.Text(self.frame_res_view, width=70, height=13)
        self.text_res.pack(side="left", fill="both", expand=True)

        # 垂直滚动条
        self.scrollbar_text = tk.Scrollbar(self.frame_res_view)
        self.scrollbar_text.pack(side="right", fill="both")

        # 绑定滚动条与文本框的联动
        self.text_res.config(yscrollcommand=self.scrollbar_text.set)
        self.scrollbar_text.config(command=self.text_res.yview)

    def open_dir(self):
        """打开已选择的文件夹（使用系统默认文件管理器）"""
        if self.dir_selected == "---未选择文件夹---":
            messagebox.showerror(title="错误", message="请选择一个有效文件夹！")
        else:
            os.startfile(self.dir_selected)  # Windows 特有；macOS/Linux 需用 subprocess

    def res_view(self):
        """生成并显示重命名预览结果（不修改实际文件）"""
        # 校验：必须已选择文件夹
        if self.dir_selected == "---未选择文件夹---":
            messagebox.showerror(title="错误", message="请选择一个有效文件夹！")
        # 校验：必须输入班会主题
        elif self.entry_topic.get() == "":
            messagebox.showerror(title="错误", message="请输入本次的班会主题！")
        else:
            # 调用业务逻辑模块，生成预览文本
            text = func_rename.rename_files(
                self.dir_selected,
                self.entry_topic.get(),
                mode="preview"
            )
            # 清空旧内容，插入新预览
            self.text_res.delete(1.0, tk.END)
            self.text_res.insert('1.0', text)

    def res_rename(self):
        """执行实际的批量重命名操作"""
        # 三重校验：文件夹、主题、是否已预览
        if self.dir_selected == "---未选择文件夹---":
            messagebox.showerror(title="错误", message="请选择一个有效文件夹！")
        elif self.entry_topic.get() == "":
            messagebox.showerror(title="错误", message="请输入本次的班会主题！")
        elif self.text_res.get('1.0', 'end-1c') == "":
            # 'end-1c' 表示获取全部内容但不包含末尾自动换行符
            messagebox.showerror(title="错误", message="为确保操作正确，请先查看预期结果！")
        else:
            # 调用业务逻辑模块，执行重命名
            result = func_rename.rename_files(
                self.dir_selected,
                self.entry_topic.get(),
                mode="work"
            )
            if result["success"]:
                messagebox.showinfo("成功", result["message"])
            else:
                messagebox.showerror("错误", result["message"])

    def select_dir(self):
        """弹出文件夹选择对话框，并更新界面显示"""
        dir_path = filedialog.askdirectory(
            title="选择一个文件夹",
            initialdir="C:/"  # 默认打开 C 盘根目录
        )

        # 为避免路径过长导致界面错乱，进行截断显示（如 .../班会材料）
        if dir_path != "":
            self.dir_selected = dir_path
            text = dir_path
            if len(dir_path) > 40:  # 文件夹路径过长处理
                pos = dir_path.rfind("/")
                file_name = "..." + dir_path[pos:]  # 例如: .../文件名
                if len(file_name) > 40:
                    file_name = file_name[:37] + "..."  # .../部分文件名...
                text = file_name

            # 更新显示文本
            self.var_label_dir_path.set(text)
            self.label_dir_path.config(text=self.var_label_dir_path.get())
        else:
            # 用户取消了选择
            self.dir_selected = "---未选择文件夹---"

    def run(self):
        """
        启动 tkinter 的主事件循环（mainloop），让窗口显示出来并响应用户操作
        :return:
        """
        self.window_func_rename.mainloop()


if __name__ == "__main__":
    app= WindowFuncRename()
    app.run()
