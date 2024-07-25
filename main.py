import os
import sys
import tkinter as tk
from idlelib import browser
from tkinter import ttk
from tkinter import messagebox
from playwright.sync_api import Page
from playwright.sync_api import sync_playwright

class App(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        # Make the app responsive
        self.choosing_frame = None
        self.login_frame = None
        self.parent = parent
        for index in [0, 1, 2]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        # 创建变量存储用户名和密码
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        # 创建登录界面
        self.create_login_widgets()

    def create_login_widgets(self):
        # 创建登录表单
        self.login_frame = ttk.LabelFrame(self, text="用户登录", padding=(20, 10))
        self.login_frame.grid(row=0, column=0, padx=(20, 10), pady=(20, 10), sticky="nsew")

        # 用户名
        ttk.Label(self.login_frame, text="用户名:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        ttk.Entry(self.login_frame, textvariable=self.username).grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # 密码
        ttk.Label(self.login_frame, text="密码:").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        ttk.Entry(
            self.login_frame, textvariable=self.password, show="*").grid(row=1, column=1, padx=5, pady=10,sticky="ew")

        # 登录按钮
        ttk.Button(self.login_frame, text="登录", command=self.login).grid(
            row=2, column=0, columnspan=2, padx=5,pady=10, sticky="ew")

    def login(self):
        # 获取用户名和密码
        username = self.username.get()
        password = self.password.get()

        # 简单验证用户名和密码是否为空
        if not username or not password:
            messagebox.showerror("错误", "请输入用户名和密码！")
            return

        # 尝试登录
        try:
            self.start_grabbing(username, password)
        except Exception as e:
            messagebox.showerror("错误", f"登录失败：{str(e)}")

    def start_grabbing(self, username, password):
        def main():
            # 获取当前脚本所在目录
            executable_dir = os.path.dirname(sys.executable)
            # 构建 Chrome.exe 路径
            chrome_exe_path = os.path.join(executable_dir, "chrome-win", "chrome.exe")
            print(chrome_exe_path)
            # 使用 Playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path=chrome_exe_path)  # 指定驱动文件路径
                page = browser.new_page()
                # 打开新页面
                page: Page = browser.new_page()
                # 打开指定网址
                page.goto("https://sso.stu.edu.cn/login?service=http%3A%2F%2Fjw.stu.edu.cn%2F")
                # 输入用户名
                page.fill("#username", username)
                # 输入密码
                page.fill("#password", password)
                # 点击登录按钮
                page.click('#login')

                # 等待页面加载完成
                page.wait_for_load_state("networkidle")
                # 切换到母iframe中点选课中心
                page.frame_locator("#Frame0").locator('body > div.person > div.person-top > ul > li:nth-child(5)').click()
                # 判断系统有无开放
                judge = page.frame_locator("#FrameNEW_XSD_PYGL_XKGL_NXSXKZX").locator(
                    "body > div > div.content > div > table > tbody > tr > td:nth-child(4) > span").count()
                print(judge)
                if judge == 0:
                    messagebox.showinfo("提示", "系统暂未开放！")
                else:
                    # 登录成功后隐藏登录界面
                    self.login_frame.grid_forget()

                    # 创建抢课界面
                    self.create_choosing_widgets(page)

        def choose_majoy_course(self, page):
            # 切换到 表格iframe 中 并点击专业选课按钮
            # 定位父 iframe
            aiframe = page.frame_locator("#FrameNEW_XSD_PYGL_XKGL_NXSXKZX")

            # 定位子 iframe (selectBottom)
            biframe = aiframe.frame_locator("#selectBottom")

            # 在子 iframe 内定位元素并点击
            biframe.locator("body > div.bottom1 > div > ul > li:nth-child(2)").click()

            # 定位表格 iframe
            ciframe = biframe.frame_locator("#selectTable")

            # 在表格 iframe 内定位并点击专业选课按钮
            ciframe.locator("body > div:nth-child(13) > label:nth-child(9) > i").click()
            ciframe.locator("body > div:nth-child(13) > label:nth-child(10) > i").click()
            # 循环，直到查询到课程数据
            while True:
                # 输入课程名称
                classname = input("请输入课程名称: ")
                # 定位并输入课程名称
                x = ciframe.locator("#kcxx")
                x.fill(classname)
                # 提交查询
                ciframe.locator("body > div:nth-child(13) > input.button").click()
                # 等待查询结果
                ciframe.wait_for_selector(" #dataView_info")

                # 判断查询结果,获取元素文本
                y = ciframe.locator('#dataView_info')
                y.wait_for()
                a1 = y.text_content()
                if "显示 0 至 0 共 0 项" != a1:  # 注意：这里判断条件改为“不等于”
                    # 执行其他操作
                    print("查询到数据:")
                    # 反馈查询结果
                    print("发现", a1, "个结果")
                    print("开始抢课(/≧▽≦)/")

                    # 利用网站进行筛选
                    ciframe.locator(
                        "body > div:nth-child(13) > label:nth-child(8) > i").click()
                    ciframe.locator(
                        "body > div:nth-child(13) > label:nth-child(9) > i").click()
                    ciframe.locator(
                        "body > div:nth-child(13) > label:nth-child(10) > i").click()
                    inum = 0
                    while True:
                        inum = inum + 1
                        # 点击查询按钮
                        n = ciframe.locator("body > div:nth-child(13) > input.button")
                        n.wait_for()
                        n.click()
                        # 使用 WebDriverWait 等待元素出现
                        ciframe.wait_for_selector('#dataView > tbody > tr > td')
                        # 获取元素文本并判断
                        y = ciframe.locator('#dataView_info')
                        y.wait_for()
                        a1 = y.text_content()
                        z = ciframe.locator("a[href*='xsxkOper']")
                        numz = z.count()
                        print("已查询", inum,"次")

                        if "显示 0 至 0 共 0 项" != a1:  # 注意：这里判断条件改为“不等于”
                            # 开选
                            ciframe.wait_for_selector("a[href*='xsxkOper']")
                            # 遍历每个链接并点击(抽空整这功能)
                            for i in range(numz):
                                ciframe.locator("a[href*='xsxkOper']").nth(i).click()  # 遍历所有链接并点击
                            print("恭喜恭喜[]~(￣▽￣)~*，这门课抢课成功<(￣︶￣)>")
                            print("先别急的关，记得手动点安全退出")
                            # 等待用户输入，程序不会自动关闭
                            input("按 Enter 键退出程序...")
                            # 关闭浏览器
                            browser.close()
                            break

                else:

                    # 提示用户重新输入
                    print("查询结果为空，请重新输入课程名称")
                    # 清空课程名称输入框
                    x.fill("")

        def choose_public_course(self, page):
            # 切换到 表格iframe 中 并点击公选课按钮
            # 定位父 iframe
            aiframe = page.frame_locator("#FrameNEW_XSD_PYGL_XKGL_NXSXKZX")

            # 定位子 iframe (selectBottom)
            biframe = aiframe.frame_locator("#selectBottom")

            # 在子 iframe 内定位元素并点击
            biframe.locator("body > div.bottom1 > div > ul > li:nth-child(3)").click()

            # 定位表格 iframe
            ciframe = biframe.frame_locator("#selectTable")

            # 去筛选
            ciframe.locator("body > div.search-form-content > div > label:nth-child(9) > i").click()
            ciframe.locator("body > div.search-form-content > div > label:nth-child(10) > i").click()
            # 循环，直到查询到课程数据
            while True:
                # 输入课程名称
                classname = input("请输入课程名称: ")
                # 定位并输入课程名称
                x = ciframe.locator("#kcxx")
                x.fill(classname)
                # 提交查询
                ciframe.locator('body > div.search-form-content > div > input:nth-child(11)').click()
                # 等待查询结果
                ciframe.wait_for_selector(" #dataView_info")

                # 判断查询结果,获取元素文本
                y = ciframe.locator('#dataView_info')
                y.wait_for()
                a1 = y.text_content()
                a2 = a1.strip("当前显示 ")
                if "显示 0 至 0 共 0 项" != a1:  # 注意：这里判断条件改为“不等于”
                    # 执行其他操作
                    print("查询到数据:")
                    # 反馈查询结果
                    print("发现", a2, "个结果")
                    print("开始抢课(/≧▽≦)/")

                    # 利用网站进行筛选
                    ciframe.locator(
                        "body > div.search-form-content > div > label:nth-child(8) > i").click()
                    ciframe.locator(
                        "body > div.search-form-content > div > label:nth-child(9) > i").click()
                    ciframe.locator(
                        "body > div.search-form-content > div > label:nth-child(10) > i").click()
                    inum = 0
                    while True:
                        inum = inum + 1
                        print("已查询", inum, "次")
                        # 点击查询按钮
                        ciframe.locator('body > div.search-form-content > div > input:nth-child(11)').click()
                        # 使用 WebDriverWait 等待元素出现
                        ciframe.wait_for_selector('#dataView_info')
                        # 获取元素文本并判断
                        y = ciframe.locator('#dataView_info')
                        y.wait_for()
                        a1 = y.text_content()
                        z = ciframe.locator("a[href*='xsxkFun']")
                        numz = z.count()

                        if "显示 0 至 0 共 0 项" != a1:  # 注意：这里判断条件改为“不等于”
                            # 开选
                            ciframe.wait_for_selector("a[href*='xsxkFun']")
                            # 遍历每个链接并点击(抽空整这功能)
                            for i in range(numz):
                                ciframe.locator("a[href*='xsxkFun']").nth(i).click()  # 遍历所有链接并点击
                            print("恭喜恭喜[]~(￣▽￣)~*，这门课抢课成功<(￣︶￣)>")
                            print("先别急的关，记得手动点安全退出")
                            # 等待用户输入，程序不会自动关闭
                            input("按 Enter 键退出程序...")
                            # 关闭浏览器
                            browser.close()
                            break
                else:

                    # 提示用户重新输入
                    print("查询结果为空，请重新输入课程名称")
                    # 清空课程名称输入框
                    x.fill("")

        # 在新线程中启动抢课逻辑
        import threading
        threading.Thread(target=main).start()

    def create_grabbing_widgets(self, page):
        # ... 创建抢课界面的 widgets ...
        # 例如：课程选择、操作按钮等
        pass  # 这里需要根据实际需求补充

    def create_choosing_widgets(self, page):
        # 创建选择表单
        self.choosing_frame = ttk.LabelFrame(self, text="选课类型选择", padding=(20, 10))
        self.choosing_frame.grid(row=0, column=0, padx=(20, 10), pady=(20, 10), sticky="nsew")

        # 专业课按钮
        ttk.Button(self.choosing_frame, text="专业课", command=lambda: self.choose_majoy_course(page)).grid(
            row=0, column=0, padx=5, pady=10, sticky="ew")
        # 公选课按钮
        ttk.Button(self.choosing_frame, text="公选课", command=lambda: self.choose_public_course(page)).grid(
            row=0, column=1, padx=5, pady=10, sticky="ew")

    def choose_majoy_course(self, page):
        pass

    def choose_public_course(self, page):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    root.title("抢课软件")

    # 设置 Azure 主题
    root.tk.call("source", "azure.tcl")
    root.tk.call("set_theme", "light")

    app = App(root)
    app.pack(fill="both", expand=True)

    # 设置窗口最小尺寸并居中
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
    y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
    root.geometry("+{}+{}".format(x_cordinate, y_cordinate - 20))

    root.mainloop()
