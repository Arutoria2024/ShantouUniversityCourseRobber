import subprocess
import time

from playwright.sync_api import Page, Browser
from playwright.sync_api import sync_playwright

# 注释
print("此程序由子文开发，仅用以学习交流使用，请勿滥用此软件")
print("使用脚本时请退出正在登录的选课系统，否则会冲突导致程序无法正确运行")
print("1、此脚本可能因校园网站卡顿而报错，只需重新打开即可")
print("2、账号密码输错时重开即可")
print("3、如有什么问题欢迎联系我，邮箱：23zwang1@stu.edu.cn")
username = input("请输入你的用户名: ")
password = input("请输入你的密码: ")
# 安装 Playwright 浏览器
try:
    subprocess.check_call(['playwright', 'install'])
except subprocess.CalledProcessError:
    print("Playwright 安装失败，请手动安装。")

# 获取用户输入
start = input("是否开始抢课？(y/n): ")

if start.lower() == 'y':
    with sync_playwright() as p:
        # 创建浏览器实例
        browser: Browser = p.chromium.launch(headless=False)
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

        # 切换到 父iframe 点击次级选课
        page.frame_locator("#FrameNEW_XSD_PYGL_XKGL_NXSXKZX").locator(
            "body > div > div.content > div > table > tbody > tr > td:nth-child(4) > span").click()

        # 等待页面加载完成
        page.wait_for_load_state("networkidle")
        #启动弹窗监听器
        def on_dialog(dialog):
            print('Dialog message:', dialog.message)
            dialog.accept()
            print("弹窗已处理")


        page.on('dialog', on_dialog)

        # 获取用户输入
        start = input("选专业课还是公选课？(1：专业课/2：公选课)#只用输入1或2: ")
        if start.lower() == '1':
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
                x1 = ciframe.locator("body > div:nth-child(13) > input.button")
                x1.wait_for()
                x1.click()
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
                    print("发现", a2)
                    print("开始抢课(/≧▽≦)/")

                    # 利用网站进行筛选
                    ciframe.locator(
                        "body > div:nth-child(13) > label:nth-child(8) > i").click()
                    ciframe.locator(
                        "body > div:nth-child(13) > label:nth-child(9) > i").click()
                    ciframe.locator(
                        "body > div:nth-child(13) > label:nth-child(10) > i").click()
                    # 先查一次归零
                    ciframe.locator("body > div:nth-child(13) > input.button").click()
                    # 使用 WebDriverWait 等待元素出现
                    ciframe.wait_for_selector('#dataView_info')
                    while True:
                        # 点击查询按钮
                        ciframe.locator("body > div:nth-child(13) > input.button").click()
                        # 使用 WebDriverWait 等待元素出现
                        ciframe.wait_for_selector('#dataView_info')
                        # 获取元素文本并判断
                        y = ciframe.locator('#dataView_info')
                        y.wait_for()
                        a1 = y.text_content()
                        z = ciframe.locator("a[href*='xsxkOper']")
                        numz = z.count()

                        if "显示 0 至 0 共 0 项" != a1:  # 注意：这里判断条件改为“不等于”
                            # 开选
                            print(a1)
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
        if start.lower() == '2':
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
                    # 先查一次归零
                    ciframe.locator('body > div.search-form-content > div > input:nth-child(11)').click()
                    while True:
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