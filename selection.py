from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLineEdit, QDialog, QPushButton, QSpinBox, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QTabWidget, QTextEdit, QGridLayout, QMessageBox
from PyQt5.QtCore import QTimer, QRect, QPoint, Qt
from data_transfer import send_file
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QPen, QCursor, QImage
import cv2
import numpy as np
import pyautogui
import time
from PyQt5.QtWidgets import QWidget, QApplication, QAction
from PyQt5.QtCore import Qt, QPoint, QRect, QSize
from PyQt5.QtGui import QPainter, QPen, QColor


class SelectionArea(QWidget):
    def __init__(self, parent=None, area_idx=None):
        super().__init__(parent)
        self.area_idx = area_idx
        # 设置窗口标志
        #self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # 无边框
            Qt.WindowStaysOnTopHint |  # 窗口置顶
            Qt.Tool |                  # 工具窗口
            Qt.BypassWindowManagerHint # 绕过窗口管理器
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 初始化变量
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_drawing = False
        
        # 获取当前屏幕
        current_screen = QApplication.screenAt(QCursor.pos())
        if current_screen is None:
            current_screen = QApplication.primaryScreen()
            
        # 设置窗口大小为当前屏幕大小
        self.screen_rect = current_screen.geometry()
        self.setGeometry(self.screen_rect)
        self.selection_rect = QRect()

        # 设置鼠标追踪
        self.setMouseTracking(True)
        # 设置全屏
        # screen = QApplication.primaryScreen().geometry()
        # self.setGeometry(screen)
        
        # # 初始化整个屏幕的矩形
        # self.screen_rect = self.geometry()
        # self.selection_rect = QRect()

        # 获取所有屏幕
        # screens = QApplication.screens()
        # # 计算所有屏幕组成的总区域
        # total_rect = QRect()
        # for screen in screens:
        #     total_rect = total_rect.united(screen.geometry())
            
        # # 设置窗口大小为总屏幕区域
        # self.setGeometry(total_rect)
        
        # # 初始化整个屏幕的矩形
        # self.screen_rect = total_rect
        # self.selection_rect = QRect()

        # # 设置鼠标追踪
        # self.setMouseTracking(True)
        
        # # 将窗口显示在最前面
        # self.show()
        # self.raise_()
        # self.activateWindow()

    def paintEvent(self, event):
        painter = QPainter(self)
        # 设置半透明的黑色背景
        mask_color = QColor(0, 0, 0, 100)  # 背景遮罩颜色，最后一个参数是透明度(0-255)
        painter.fillRect(self.screen_rect, mask_color)
        
        if self.is_drawing and not self.selection_rect.isEmpty():
            # 创建一个半透明的选区遮罩颜色
            selection_mask = QColor(255, 255, 255, 50)  # 选区遮罩颜色，透明度设为50
            painter.fillRect(self.selection_rect, selection_mask)
            
            # 绘制选区边框
            painter.setPen(QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.SolidLine))
            painter.drawRect(self.selection_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.is_drawing = True
            self.selection_rect = QRect()
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.end_point = event.pos()
            self.selection_rect = QRect(self.start_point, self.end_point).normalized()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.end_point = event.pos()
            self.selection_rect = QRect(self.start_point, self.end_point).normalized()
            self.is_drawing = False
            self.update()
            # 获取选区坐标
            print(f"Selection coordinates: {self.selection_rect.x()}, {self.selection_rect.y()}, "
                  f"{self.selection_rect.width()}, {self.selection_rect.height()}")
            self.parent().set_selection(self.selection_rect, self.area_idx)  # 将选择的区域传递给父窗口
            self.close()
            print("select area window close!")

    def keyPressEvent(self, event):
        # 按ESC键退出
        if event.key() == Qt.Key_Escape:
            self.close()


class SelectionArea2(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.rect = QRect()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.SolidLine))
        painter.drawRect(self.rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.end_point = self.start_point
            self.rect = QRect(self.start_point, self.end_point)
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.end_point = event.pos()
            self.rect = QRect(self.start_point, self.end_point).normalized()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.end_point = event.pos()
            self.rect = QRect(self.start_point, self.end_point).normalized()
            self.update()
            self.parent().set_selection(self.rect)  # 将选择的区域传递给父窗口
            self.close()  # 关闭选择区域窗口
