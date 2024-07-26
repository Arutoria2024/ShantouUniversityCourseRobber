# ocr_functions.py

import cv2
import numpy as np
from paddleocr import PaddleOCR
from itertools import zip_longest

# 实例化 OCR 模型 (可以考虑将其放在函数外部，避免重复加载)
ocr = PaddleOCR()

def detect_and_recognize(parent_image_path):
    """
    检测模板图像并识别框内的文字。

    Args:
        parent_image_path (str): 父图像的路径。

    Returns:
        list: 包含识别结果的列表，每个元素是一个字典，包含 "course" 和 "teacher" 键值对。
    """

    parent_image = cv2.imread(parent_image_path)
    template_image = cv2.imread("template.png")

    gray = cv2.cvtColor(parent_image, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)

    found = None
    default_scale = 1.0

    # 定义精度阈值函数
    def get_threshold(scale):
        # 根据缩放比例计算阈值
        threshold = 1.07770112 * scale**2 + -1.64812899 * scale + 1.32596539
        return threshold

    # 尝试不同的缩放比例
    for scale in np.linspace(0.5, 1.5, 20)[::-1]:
        # 缩放模板图像
        resized_template = cv2.resize(template_gray, None, fx=scale, fy=scale)
        w, h = resized_template.shape[::-1]

        # 模板匹配
        match = cv2.matchTemplate(gray, resized_template, cv2.TM_CCOEFF_NORMED)
        # 获取动态阈值
        threshold = get_threshold(scale)
        loc = np.where(match >= threshold)

        # 如果找到匹配，更新结果
        if len(loc[0]) > 0:
            found = (loc, w, h)
            default_scale = scale

    results = []  # 存储识别结果的列表

    # 如果找到匹配
    if found is not None:
        locations, w, h = found
        for p in zip(*locations[::-1]):
            x1, y1 = p
            x0 = int(x1 + 2 * default_scale)
            y0 = int(y1 - 40 * default_scale)
            x2 = int(x1 + h * default_scale + 120 * default_scale)
            y2 = int(y1 + w * default_scale)
            cv2.rectangle(parent_image, (x0, y0), (x2, y2), (0, 255, 0), 1)
            # 提取框内文字
            cropped_image = parent_image[y0:y2, x0:x2]
            result = ocr.ocr(cropped_image, cls=False)
            # 处理识别结果
            course_text = ""
            teacher_text = ""
            for line in result:
                for word in line:
                    text_line = word[-1]
                    # 从文字元组中提取文字内容
                    text = text_line[0]
                    if "教师" in text:
                        teacher_text += text.split("教师：")[1]  # 如果包含"教师"，则提取后的
                    else:
                        course_text += text
            results.append({"course": course_text, "teacher": teacher_text})

    cv2.waitKey()

    return results
