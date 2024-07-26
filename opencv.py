import cv2
import numpy as np
from paddleocr import PaddleOCR
from itertools import zip_longest

# 实例化 OCR 模型
ocr = PaddleOCR()


parent_image = cv2.imread("test.png")
template_image = cv2.imread("public_template.png")

gray = cv2.cvtColor(parent_image, cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)

template = gray2
match = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
locations = np.where(match >= 0.8)

w, h = template.shape[0:2]
for p in zip(*locations[::-1]):
    x1, y1 = p
    x0 = x1 +2
    y0 = y1 -40
    x2, y2 = x1 + h + 85, y1 + w
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
    print("识别结果为:\n",course_text,"\n", teacher_text)

cv2.imshow("image", parent_image)
cv2.waitKey()
