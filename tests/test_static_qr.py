import sys
import os
from PyQt6.QtWidgets import QApplication,QHBoxLayout,QSpinBox, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QSize
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from selection import SelectionArea
from qr_recognizer import parse_qr_data 
import pyzbar.pyzbar as pyzbar
from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np
import pyautogui  # 用于截屏
import time
from PyQt6.QtCore import QTimer

class TestStaticQRWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("静态二维码识别测试")
        self.setGeometry(100, 100, 400, 200)

        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 预览图像显示
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(200, 200)
        self.preview_label.setStyleSheet("border: 1px solid black;")
        layout.addWidget(self.preview_label)

        # 选择区域按钮
        self.select_button = QPushButton("选择屏幕区域")
        self.select_button.clicked.connect(self.start_selection)
        layout.addWidget(self.select_button)

        hbox = QHBoxLayout() 
        self.x_label = QLabel("x:")
        self.x_input = QSpinBox()
        self.x_input.setMinimum(1)
        self.x_input.setMaximum(999999)
        self.x_input.setValue(656)
        self.y_label = QLabel("y:")
        self.y_input = QSpinBox()
        self.y_input.setMinimum(1)
        self.y_input.setMaximum(999999)
        self.y_input.setValue(95)
        self.size_label = QLabel("size:")
        self.size_input = QSpinBox()
        self.size_input.setMinimum(1)
        self.size_input.setMaximum(999999)
        self.size_input.setValue(850) 
        hbox.addWidget(self.x_label)
        hbox.addWidget(self.x_input)
        hbox.addWidget(self.y_label)
        hbox.addWidget(self.y_input) 
        hbox.addWidget(self.size_label) 
        hbox.addWidget(self.size_input) 
        self.capture_button = QPushButton("截取屏幕")
        self.capture_button.clicked.connect(self.start_capture)
        hbox.addWidget(self.capture_button)

        layout.addLayout(hbox) 
        

    def start_capture(self): 
        x = self.x_input.value()
        y = self.y_input.value() 
        size = self.size_input.value()  
        try:
            # 捕获选定区域的截图
            screenshot = pyautogui.screenshot(region=(x, y, size, size))
            
            # 转换为OpenCV格式
            screenshot_np = np.array(screenshot)
            
            if screenshot_np.size == 0:
                print("Screenshot is empty")
                return
            
            # 转换颜色空间
            screenshot_rgb = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2RGB)
            
            # 创建QImage
            height, width = screenshot_rgb.shape[:2]
            bytes_per_line = 3 * width
            q_img = QImage(screenshot_rgb.data, width, height, bytes_per_line, 
                          QImage.Format.Format_RGB888)
                      
            # 创建并缩放QPixmap
            pixmap = QPixmap.fromImage(q_img)
            scaled_pixmap = pixmap.scaled(
                QSize(200, 200),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # 设置预览图像
            self.preview_label.setPixmap(scaled_pixmap)
            # 二维码识别部分
            if len(screenshot_np.shape) > 2:
                gray_image = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)
            else:
                gray_image = screenshot_np
            
            decoded_objects = pyzbar.decode(gray_image)
            
            if decoded_objects:
                for obj in decoded_objects:
                    print("类型:", obj.type)
                    #print("数据:", obj.data.decode("utf-8")) 
                    index, data_content, is_valid = parse_qr_data(obj.data) 
                    print(index, is_valid)
                    print(f"{index} content:[{data_content}] is_valid: {is_valid}")
            else:
                print("未检测到二维码")
        except Exception as e:
            print(f"截图错误: {str(e)}")

    def start_selection(self):
        current_screen = self.screen()
        self.selection_area = SelectionArea(self, "2")
        self.selection_area.setGeometry(current_screen.geometry())
        self.selection_area.show()
        self.selection_area.raise_()
        self.selection_area.activateWindow()

    def set_selection(self, rect, area_idx=None):
        x = rect.x() 
        y = rect.y()
        width = rect.width()
        height = rect.height()
        
        # 确保截图区域有效
        if width <= 0 or height <= 0:
            print("Invalid selection area")
            return
        
        # 使用QTimer延迟截图，给系统一些时间清除选择窗口
        QTimer.singleShot(200, lambda: self.capture_screenshot(x, y, width, height))

    def capture_screenshot(self, x, y, width, height):
        try:
            print(f"开始截图: x={x}, y={y}, width={width}, height={height}")
            # 捕获选定区域的截图
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            
            # 转换为OpenCV格式
            screenshot_np = np.array(screenshot)
            
            if screenshot_np.size == 0:
                print("Screenshot is empty")
                return
            
            # 转换颜色空间 (BGR to RGB)
            screenshot_rgb = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)  # 修改这里
            
            # 创建QImage
            height, width = screenshot_rgb.shape[:2]
            bytes_per_line = 3 * width
            q_img = QImage(screenshot_rgb.data, width, height, bytes_per_line, 
                          QImage.Format.Format_RGB888)
                      
            # 创建并缩放QPixmap
            pixmap = QPixmap.fromImage(q_img)
            scaled_pixmap = pixmap.scaled(
                QSize(200, 200),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # 设置预览图像
            self.preview_label.setPixmap(scaled_pixmap)
            
            # 二维码识别部分
            if len(screenshot_np.shape) > 2:
                gray_image = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)  # 修改这里
            else:
                gray_image = screenshot_np
            
            decoded_objects = pyzbar.decode(gray_image)
            
            if decoded_objects:
                for obj in decoded_objects:
                    print("类型:", obj.type)
                    index, data_content, is_valid = parse_qr_data(obj.data) 
                    print(index, is_valid)
                    print(f"{index} content:[{data_content}] is_valid: {is_valid}")
            else:
                print("未检测到二维码")
            
        except Exception as e:
            print(f"截图错误: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestStaticQRWindow()
    window.show()
    sys.exit(app.exec()) 