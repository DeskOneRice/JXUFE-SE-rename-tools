import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import public_tools


class WindowFunc1:
    def __init__(self):
        self.parent_window = None

        # 主窗口
        self.window_func1 = tk.Tk()
        self.window_func1.title("软件与物联网工程学院团委学生会大自委工作助手")
        self.window_func1.resizable(width=False, height=False)  # 固定窗口宽度和高度
        public_tools.set_window_geometry_center(self.window_func1, 550, 185)

        self.label1 = tk.Label(self.window_func1, text="选择你的部门：", width=15, anchor=tk.E)
        self.label1.place(x=60, y=30)
        self.label2 = tk.Label(self.window_func1, text="选择指定的功能：", width=15, anchor=tk.E)
        self.label2.place(x=60, y=60)
        # self.label3 = tk.Label(self.window_func1, text="当前选中的文件夹：", width=15, anchor=tk.E)
        # self.label3.place(x=60, y=90)

        # 下拉列表的内容
        self.combobox_dict = {"---未选择部门---": "---未选择功能---",
                              "团委素质拓展部": "---功能待开发---",
                              "团委青年志愿者协会": "---功能待开发---",
                              "学生会体育部": "---功能待开发---",
                              "学生会对外联络部": "---功能待开发---",
                              "大自委思政研究部": ["[一键规范命名]专业班级 + 班会主题 + "班会材料""],
                              "大自委新媒体&宣传部": "---功能待开发---",
                              "---其余部门待添加---": "---功能待开发---"
                              }
        self.dict_keys = list(self.combobox_dict.keys())

        # 两个下拉列表框
        self.combobox1 = ttk.Combobox(self.window_func1,
                                      width=40,
                                      values=self.dict_keys,
                                      state="readonly")
        self.combobox1.place(x=170, y=30)
        self.combobox1.current(0)
        self.combobox1.bind("<<ComboboxSelected>>", self.combobox1_selected)
        self.combobox2 = ttk.Combobox(self.window_func1,
                                      width=40,
                                      values=["---未选择功能---"],
                                      state="readonly")
        self.combobox2.place(x=170, y=60)
        self.combobox2.current(0)

        # 标签：显示已经选择的文件夹
        # self.var_label_dir_path = tk.StringVar()
        # self.var_label_dir_path.set("---未选择文件夹---")
        self.dir_selected = "---未选择文件夹---"
        # self.label_dir_path = tk.Label(self.window_func1,
        #                                text=self.var_label_dir_path.get(),
        #                                anchor=tk.W) # 该label使用textvariable参数会出bug，原因未知
        # self.label_dir_path.place(x=170, y=90)

        # 两个功能按钮
        # self.btn1 = tk.Button(self.window_func1,
        #                       width=15,
        #                       text="选择目标文件夹",
        #                       command=self.select_directory)
        # self.btn1.place(x=170, y=120)
        self.btn2 = tk.Button(self.window_func1,
                              width=15,
                              text="执行指定功能",
                              command=self.run_func)
        self.btn2.place(x=170, y=90)

        # 修改窗口关闭协议
        self.window_func1.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        if self.parent_window is not None:
            self.parent_window.deiconify()
        self.destroy()
        # sys.exit()

    def select_directory(self):  # 选择目标文件夹
        dir_path = filedialog.askdirectory(
            title="选择一个文件夹",
            initialdir="C:/"  # 默认打开路径
        )
        if dir_path != "":
            if len(dir_path) > 40:  # 文件夹路径过长处理
                pos = dir_path.rfind("/")
                text = "..." + dir_path[pos:]
                self.var_label_dir_path.set(text)
            else:
                self.var_label_dir_path.set(dir_path)
            self.dir_selected = dir_path
            self.label_dir_path.config(text=self.var_label_dir_path.get())

    def combobox1_selected(self, event):  # 根据选择的部门显示可用功能
        self.combobox2.config(values=self.combobox_dict[self.combobox1.get()])
        self.combobox2.current(0)

    def run_func(self):  # 根据选择的部门和功能执行指定功能
        if self.combobox1.get() == "大自委思政研究部":
            if self.combobox2.current() == 0:
                try:
                    pass
                    # szyjb.rename_files(self.dir_selected)
                except FileNotFoundError:
                    messagebox.showerror(title="错误", message="未找到指定文件夹！")
        else:
            messagebox.showerror(title="错误", message="功能执行失败，请确保已选择可用功能！")

    def show(self):
        self.window_func1.mainloop()

    def show_from_window(self, parent_window):
        self.parent_window = parent_window
        self.parent_window.withdraw()
        self.window_func1.mainloop()

    def destroy(self):
        self.window_func1.destroy()


if __name__ == "__main__":
    WindowFunc1().show()
