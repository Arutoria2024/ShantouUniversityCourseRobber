import os
import shutil
import sys
import interface
import opencv
from playwright.sync_api import Page, sync_playwright
from PyQt5.QtCore import Qt, QSettings  # 合并 PyQt5.QtCore 导入
from PyQt5.QtWidgets import QApplication, QMainWindow
from qfluentwidgets import (
    InfoBarIcon,
    TeachingTip,
    TeachingTipTailPosition,
)

from interface import *
from login import *  # 建议检查是否可以避免使用 `from ... import *`



# 获取当前脚本所在目录
executable_dir = os.path.dirname(os.path.abspath('main.py'))  # 记得将目录改为sys.executable
# 构建 Chrome.exe 路径
chrome_exe_path = os.path.join(executable_dir, "chrome-win", "chrome.exe")
class loginWindow(QMainWindow):
    def __init__(self):  # 修正初始化方法名称
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        # 隐藏窗口
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # 加阴影
        self.ui.label.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=25, xOffset=0, yOffset=0))
        self.ui.username_input.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=5, xOffset=0, yOffset=0))
        self.ui.password_input.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=5, xOffset=0, yOffset=0))
        self.ui.loginButton.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=25, xOffset=3, yOffset=3))
        # 加跳转
        self.ui.username_input.returnPressed.connect(self.ui.password_input.setFocus)
        self.ui.password_input.returnPressed.connect(self.ui.loginButton.click)
        self.ui.loginButton.clicked.connect(self.login_in)
        self.ui.memory_checkBox.stateChanged.connect(self.save_account)
        self.show()

    def save_account(self, state):
        """
                根据勾选状态保存或清除账号密码。

                Args:
                    state (int): 勾选状态，2 表示勾选，0 表示未勾选。
                """
        if state == Qt.Checked:
            username = self.ui.username_input.text()
            password = self.ui.password_input.text()
            self.save_credentials(username, password)
        else:
            self.clear_credentials()

    def save_credentials(self, username, password):
        """
        将账号密码保存到安全的位置，例如使用 QSettings。

        Args:
            username (str): 用户名。
            password (str): 密码。
        """
        settings = QSettings("STU", "CourseAssistant")
        settings.setValue("username", username)
        settings.setValue("password", password)

    def clear_credentials(self):
        """
        清除保存的账号密码。
        """
        settings = QSettings("STU", "CourseAssistant")
        settings.remove("username")
        settings.remove("password")

    def load_credentials(self):
        """
        加载保存的账号密码。

        Returns:
            tuple: 包含用户名和密码的元组，如果未保存则返回 None。
        """
        settings = QSettings("STU", "CourseAssistant")
        username = settings.value("username")
        password = settings.value("password")
        if username and password:
            return username, password
        else:
            return None

    def showEvent(self, event):
        """
        在窗口显示时自动填充账号密码。
        """
        super().showEvent(event)
        credentials = self.load_credentials()
        if credentials:
            self.ui.username_input.setText(credentials[0])
            self.ui.password_input.setText(credentials[1])
            self.ui.memory_checkBox.setChecked(True)

    # 拖动
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.isMaximized() == False:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, mouse_event):
        if QtCore.Qt.LeftButton and self.m_flag:
            self.move(mouse_event.globalPos() - self.m_Position)  # 更改窗口位置
            mouse_event.accept()

    def mouseReleaseEvent(self, mouse_event):
        self.m_flag = False
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

    def showTeachingTip(self):
        TeachingTip.create(
            target=self.ui.loginButton,
            icon=InfoBarIcon.WARNING,
            title='警告',
            content="账号或密码不能为空",
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )
    def showAccountTip(self):
        TeachingTip.create(
            target=self.ui.loginButton,
            icon=InfoBarIcon.WARNING,
            title='警告',
            content="账号或密码错误\n请输入校园网账号",
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )
    def showSysTip(self):
        TeachingTip.create(
            target=self.ui.loginButton,
            icon=InfoBarIcon.WARNING,
            title='警告',
            content="选课系统未开放",
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )
    def login_in(self):
        username = self.ui.username_input.text()
        password = self.ui.password_input.text()
        if not username and not password:
            self.showTeachingTip()
        else:
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
                # 检查账号是否输入正确
                nmp = page.locator("#login_error").count()
                if nmp == 1:
                    self.ui.username_input.clear()
                    self.ui.password_input.clear()
                    self.showAccountTip()
                else:
                    # 切换到母iframe中点选课中心
                    page.frame_locator("#Frame0").locator(
                        'body > div.person > div.person-top > ul > li:nth-child(5)').click()
                    element_count = page.frame_locator("#Frame0").locator("body > div > div.content > div").count()
                    if element_count == 0:
                        self.showSysTip()
                    else:
                        self.win = MainWindow(username, password)
                        self.close()

class MainWindow(QtWidgets.QMainWindow,interface.Ui_MainWindow):
    def __init__(self, username, password):  # 修正初始化方法名称
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # 获取目录
        self.parent_image_file = None
        #允许窗体接受拖拽
        self.setAcceptDrops(True)
        #隐藏窗口
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.ui.comboBox.currentIndexChanged.connect(self.on_combobox_changed)
        self.a0 = ''
        self.course_type = '专业课'
        self.username = username
        self.password = password
        self.ciframe = None
        self.ui.lineEdit.searchSignal.connect(self.update_a0)
        self.ui.startButton.clicked.connect(self.changeLamba)
        self.ui.StartRec.clicked.connect(self.OCR_Process)

        self.show()

    def init_browser_and_navigate(self):
        """初始化浏览器并导航到目标页面"""


        with sync_playwright() as p:
            self.browser = p.chromium.launch(executable_path=chrome_exe_path)
            self.page = self.browser.new_page()
            self.page.goto("https://sso.stu.edu.cn/login?service=http%3A%2F%2Fjw.stu.edu.cn%2F")
            self.page.fill("#username", self.username)
            self.page.fill("#password", self.password)
            self.page.click('#login')
            self.page.wait_for_load_state("networkidle")
            self.page.frame_locator("#Frame0").locator(
                'body > div.person > div.person-top > ul > li:nth-child(5)').click()
            self.page.frame_locator("#FrameNEW_XSD_PYGL_XKGL_NXSXKZX").locator(
                "body > div > div.content > div > table > tbody > tr > td:nth-child(4) > span").click()
            self.page.wait_for_load_state("networkidle")

            # 定位 iframe 元素
            aiframe = self.page.frame_locator("#FrameNEW_XSD_PYGL_XKGL_NXSXKZX")
            biframe = aiframe.frame_locator("#selectBottom")
            self.ciframe = biframe.frame_locator("#selectTable")

    def workingTip(self):
        TeachingTip.create(
            target=self.ui.lineEdit,
            icon=InfoBarIcon.INFORMATION,
            title='通告',
            content="由于平时学校并不开启选课系统，所以像根据教师名称搜素、搜寻结果显示等，暂未开发",
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )

    def showImageXTip(self):
        TeachingTip.create(
            target=self.ui.lineEdit_3,
            icon=InfoBarIcon.INFORMATION,
            title='警告',
            content="图片路径错误，请重新写入/拖入图片路径",
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )

    def showImageTip(self):
        TeachingTip.create(
            target=self.ui.lineEdit_3,
            icon=InfoBarIcon.SUCCESS,
            title='消息',
            content="图片导入成功",
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )

    def wrongTip(self):
        TeachingTip.create(
            target=self.ui.lineEdit,
            icon=InfoBarIcon.WARNING,
            title='警告',
            content="没有查寻到该课程",
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )

    def showSuccessTip(self):
        TeachingTip.create(
            target=self.ui.startButton,
            icon=InfoBarIcon.SUCCESS,
            title='恭喜',
            content="抢课成功",
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )

    def showSearchTip(self):
        TeachingTip.create(
            target=self.ui.lineEdit,
            icon=InfoBarIcon.SUCCESS,
            title='查询成功',
            content="已查询到对应课程",
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )

    def showSearchXTip(self):
        TeachingTip.create(
            target=self.ui.lineEdit,
            icon=InfoBarIcon.WARNING,
            title='查询失败',
            content="请输入正确课程名称",
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self
        )
    # 获得搜索文本
    def update_a0(self, text):
        self.a0 = text
        self.SearchProcess()

    def SearchProcess(self):
        self.init_browser_and_navigate()
        if self.course_type == '专业课':
            self.ciframe.locator("body > div:nth-child(13) > label:nth-child(9) > i").click()
            self.ciframe.locator("body > div:nth-child(13) > label:nth-child(10) > i").click()
        elif self.course_type == '公选课':
            self.ciframe.locator("body > div.search-form-content > div > label:nth-child(9) > i").click()
            self.ciframe.locator("body > div.search-form-content > div > label:nth-child(10) > i").click()
        self.search_course()

    # 获得选课类型
    def on_combobox_changed(self, index):
        self.course_type = self.ui.comboBox.itemText(index)

    def select_course(self):
        """选择课程"""
        if self.course_type == '专业课':
            self.ciframe.locator("body > div:nth-child(13) > label:nth-child(8) > i").click()
            self.ciframe.locator("body > div:nth-child(13) > label:nth-child(9) > i").click()
            self.ciframe.locator("body > div:nth-child(13) > label:nth-child(10) > i").click()
            selector = "a[href*='xsxkOper']"
        elif self.course_type == '公选课':
            self.ciframe.locator("body > div.search-form-content > div > label:nth-child(8) > i").click()
            self.ciframe.locator("body > div.search-form-content > div > label:nth-child(9) > i").click()
            self.ciframe.locator("body > div.search-form-content > div > label:nth-child(10) > i").click()
            selector = "a[href*='xsxkFun']"

        inum = 0
        while True:
            inum += 1
            if self.course_type == '专业课':
                self.ciframe.locator("body > div:nth-child(13) > input.button").click()
            elif self.course_type == '公选课':
                self.ciframe.locator('body > div.search-form-content > div > input:nth-child(11)').click()

            self.ciframe.wait_for_selector('#dataView > tbody > tr > td')
            result_text = self.ciframe.locator('#dataView_info').text_content()
            numz = self.ciframe.locator(selector).count()

            if "显示 0 至 0 共 0 项" != result_text:
                self.ciframe.wait_for_selector(selector)
                for i in range(numz):
                    self.ciframe.locator(selector).nth(i).click()
                self.showSuccessTip()
                self.browser.close()
                break
    # 主程序
    def MainProcess(self):

        self.init_browser_and_navigate()

        def on_dialog(dialog):
            print('Dialog message:', dialog.message)
            dialog.accept()
            print("弹窗已处理")

        self.page.on('dialog', on_dialog)

        if self.course_type == '专业课':
            self.ciframe.locator("body > div:nth-child(13) > label:nth-child(9) > i").click()
            self.ciframe.locator("body > div:nth-child(13) > label:nth-child(10) > i").click()
        elif self.course_type == '公选课':
            self.ciframe.locator("body > div.search-form-content > div > label:nth-child(9) > i").click()
            self.ciframe.locator("body > div.search-form-content > div > label:nth-child(10) > i").click()

        while True:
            if self.search_course():
                self.select_course()
                break

    def OCR_Process(self):
        if self.parent_image_file is None:
            self.showImageXTip()
        else:
            self.showImageTip()
            # 构建 母版图片 路径
            parent_image_dir = os.path.join(executable_dir, "parent_image")

            shutil.copy2(self.parent_image_file, parent_image_dir)

            opencv.rename_chinese_files(parent_image_dir)

            results = opencv.detect_and_recognize(parent_image_dir)
            # 处理识别结果
            for item in results:
                print(item["course"])
                print(item["teacher"])
            # 清空表格内容
            self.ui.tableWidget.setRowCount(0)

            # 添加识别结果到表格
            for row, item in enumerate(results):
                self.ui.tableWidget.insertRow(row)

                course_item = QtWidgets.QTableWidgetItem(item["course"])
                course_item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.ui.tableWidget.setItem(row, 0, course_item)

                teacher_item = QtWidgets.QTableWidgetItem(item["teacher"])
                teacher_item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.ui.tableWidget.setItem(row, 1, teacher_item)
    # 拖动
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.isMaximized() == False:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, mouse_event):
        if QtCore.Qt.LeftButton and self.m_flag:
            self.move(mouse_event.globalPos() - self.m_Position)  # 更改窗口位置
            mouse_event.accept()

    def mouseReleaseEvent(self, mouse_event):
        self.m_flag = False
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

    def changeLamba(self):
        if self.ui.startButton.text() == "开始抢课":
            self.ui.startButton.setText("停止抢课")
            self.MainProcess()
        else:
            self.ui.startButton.setText("开始抢课")
    def dragEnterEvent(self, a0: QtGui.QDragEnterEvent) -> None:
        #判断有没有接受到内容
        if a0.mimeData().hasUrls():
            #如果接收到内容了，就把它存在事件中
            a0.accept()
        else:
            #没接收到内容就忽略
            a0.ignore()

    def dropEvent(self, a0: QtGui.QDropEvent) -> None:
        if a0:
            for i in a0.mimeData().urls():
                print(i.path())
                file_path = i.path()[1:]
                self.ui.lineEdit_3.setText(file_path)
                self.parent_image_file = file_path

if __name__ == '__main__':  # 修正主程序入口条件判断
    app = QApplication(sys.argv)
    win = loginWindow()
    sys.exit(app.exec_())
