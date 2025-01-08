from PyQt6.QtWidgets import QMainWindow, QFileDialog, QLineEdit, QDialog, QPushButton, QSpinBox, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QTabWidget, QTextEdit, QGridLayout, QMessageBox
from PyQt6.QtCore import QTimer, QRect, QPoint, Qt
from data_transfer import send_file
from PyQt6.QtGui import QPixmap, QAction, QIcon, QPainter, QPen, QCursor,QImage
import threading
import cv2
import numpy as np
import pyautogui
import time
from queue import Queue
import pyautogui  # 用于截屏
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QPoint, QRect, QSize
from PyQt6.QtGui import QPainter, QPen, QColor
from qr_recognizer import recognize_qr_code, parse_qr_data
from selection import SelectionArea
import zlib
from file_handler import decompress_data
from recognition_thread import RecognitionThread

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("二维码数据接收系统")
        self.setGeometry(100, 100, 800, 600)
        self.pre_size = 90 # 二维码预览框的大小 

        # 创建主布局
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # 日志区域
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)

        # 文件存储路径
        self.file_path_label = QLabel("文件存储路径:")
        self.file_path_input = QLineEdit()
        self.browse_button = QPushButton("浏览")
        self.browse_button.clicked.connect(self.browse_file)

        # 分段数设置
        self.segment_count_label = QLabel("文件总分段数:")
        self.segment_count_input = QSpinBox()
        self.segment_count_input.setMinimum(1)
        self.segment_count_input.setMaximum(999999)
        self.segment_count_input.setValue(200)
        self.segment_count_input.valueChanged.connect(self.on_segment_size_changed)

        # 二维码位置设置
        self.monitor_qr1_btn = QPushButton("点选二维码框框1")
        self.monitor_qr1_btn.clicked.connect(self.select_qr1_area)
        self.monitor_qr2_btn = QPushButton("点选二维码框框2")
        self.monitor_qr2_btn.clicked.connect(self.select_qr2_area)
        self.monitor_qr3_btn = QPushButton("点选二维码框框3")
        self.monitor_qr3_btn.clicked.connect(self.select_qr3_area)
        self.monitor_qr4_btn = QPushButton("点选二维码框框4")
        self.monitor_qr4_btn.clicked.connect(self.select_qr4_area) 

        self.monitor_qr1_label = QLabel()
        self.monitor_qr2_label = QLabel()
        self.monitor_qr3_label = QLabel()
        self.monitor_qr4_label = QLabel()

        self.monitor_qr1_label.setText("请选择")
        self.monitor_qr2_label.setText("请选择")
        self.monitor_qr3_label.setText("请选择")
        self.monitor_qr4_label.setText("请选择")

        # 二维码预览框
        self.monitor_qr1_preview_label = QLabel()
        self.monitor_qr2_preview_label = QLabel()
        self.monitor_qr3_preview_label = QLabel()
        self.monitor_qr4_preview_label = QLabel()

        # 二维码监视的框框坐标
        self.qr1_rect = None
        self.qr2_rect = None
        self.qr3_rect = None
        self.qr4_rect = None
        # 二维码扫描总数和进度
        self.qr1_total = 0
        self.qr2_total = 0
        self.qr3_total = 0
        self.qr4_total = 0
        self.qr1_process = 0
        self.qr2_process = 0
        self.qr3_process = 0
        self.qr4_process = 0

        self.monitor_qr1_process_label = QLabel()
        self.monitor_qr2_process_label = QLabel()
        self.monitor_qr3_process_label = QLabel()
        self.monitor_qr4_process_label = QLabel()

        vbox1 = QVBoxLayout()
        vbox2 = QVBoxLayout()
        vbox3 = QVBoxLayout()
        vbox4 = QVBoxLayout()
        vbox1.addWidget(self.monitor_qr1_btn)
        vbox1.addWidget(self.monitor_qr1_label)
        vbox1.addWidget(self.monitor_qr1_process_label)
        vbox1.addWidget(self.monitor_qr1_preview_label)
        vbox2.addWidget(self.monitor_qr2_btn)
        vbox2.addWidget(self.monitor_qr2_label)
        vbox2.addWidget(self.monitor_qr2_process_label)
        vbox2.addWidget(self.monitor_qr2_preview_label)
        vbox3.addWidget(self.monitor_qr3_btn)
        vbox3.addWidget(self.monitor_qr3_label)
        vbox3.addWidget(self.monitor_qr3_process_label)
        vbox3.addWidget(self.monitor_qr3_preview_label)
        vbox4.addWidget(self.monitor_qr4_btn)
        vbox4.addWidget(self.monitor_qr4_label)
        vbox4.addWidget(self.monitor_qr4_process_label)
        vbox4.addWidget(self.monitor_qr4_preview_label)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox1)
        hbox.addLayout(vbox2)
        hbox.addLayout(vbox3)
        hbox.addLayout(vbox4)

        # 开始和暂停按钮
        self.start_button = QPushButton("开始")
        self.start_button.clicked.connect(self.start_recognition)
        self.pause_button = QPushButton("暂停")
        self.pause_button.clicked.connect(self.pause_recognition)
        self.stop_button = QPushButton("停止")
        self.stop_button.clicked.connect(self.stop_recognition)

        hbox_btn = QHBoxLayout()
        hbox_btn.addWidget(self.stop_button)
        hbox_btn.addWidget(self.pause_button)
        hbox_btn.addWidget(self.start_button)

        # 添加帧率设置
        self.frame_rate_label = QLabel("帧率:")
        self.frame_rate_input = QSpinBox()
        self.frame_rate_input.setMinimum(1)
        self.frame_rate_input.setMaximum(100)
        self.frame_rate_input.setValue(30)  # 默认30帧

        # 线程控制变量
        self.recognition_threads = {}  # 使用字典存储线程
        self.is_running = False
        self.is_paused = False
        self.collected_data = {}
        self.data_lock = threading.Lock()

        # 需要禁用的控件列表
        self.control_widgets = [
            self.file_path_input,
            self.browse_button,
            self.segment_count_input,
            self.frame_rate_input,
            self.monitor_qr1_btn,
            self.monitor_qr2_btn,
            self.monitor_qr3_btn,
            self.monitor_qr4_btn
        ]

        # 布局设置
        self.layout = QGridLayout(self.central_widget)
        self.layout.addWidget(self.file_path_label, 0, 0)
        self.layout.addWidget(self.file_path_input, 0, 1)
        self.layout.addWidget(self.browse_button, 0, 2)
        self.layout.addWidget(self.segment_count_label, 1, 0)
        self.layout.addWidget(self.segment_count_input, 1, 1)
        self.layout.addWidget(self.frame_rate_label, 2, 0)
        self.layout.addWidget(self.frame_rate_input, 2, 1)
        self.layout.addLayout(hbox, 3, 0, 1, 3)
        self.layout.addLayout(hbox_btn, 4, 0, 1, 3)
        self.layout.addWidget(self.log_area, 5, 0, 1, 3)

        self.monitoring = False  # 监测状态
        self.update_qr_process()

        # 设置预览标签的大小和样式
        preview_size = QSize(self.pre_size, self.pre_size)
        preview_style = """
            QLabel {
                border: 1px solid #cccccc;
                background-color: #f0f0f0;
            }
        """
        
        for label in [self.monitor_qr1_preview_label, 
                     self.monitor_qr2_preview_label,
                     self.monitor_qr3_preview_label,
                     self.monitor_qr4_preview_label]:
            label.setMinimumSize(preview_size)
            label.setMaximumSize(preview_size)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(preview_style)

        self.screenshot_queue = Queue()
        self.collected_data = {}  # 存储收集到的数据
        self.total_segments = 0   # 总分段数
        self.screenshot_timer = QTimer()
        self.screenshot_timer.timeout.connect(self.capture_screen)
        
    # 更新二维码识别进度 
    def update_qr_process(self):  
        self.recalculate_total(self.segment_count_input.value())
        if (self.qr1_rect): 
            self.monitor_qr1_process_label.setText(f"{self.qr1_process}/{self.qr1_total}")
        else: 
            self.monitor_qr1_process_label.setText("-/-")
        if (self.qr2_rect):         
            self.monitor_qr2_process_label.setText(f"{self.qr2_process}/{self.qr2_total}")
        else: 
            self.monitor_qr2_process_label.setText("-/-")
        if (self.qr3_rect): 
            self.monitor_qr3_process_label.setText(f"{self.qr3_process}/{self.qr3_total}")
        else: 
            self.monitor_qr3_process_label.setText("-/-")
        if (self.qr4_rect):
            self.monitor_qr4_process_label.setText(f"{self.qr4_process}/{self.qr4_total}")
        else: 
            self.monitor_qr4_process_label.setText("-/-")

    def on_segment_size_changed(self, value): 
        self.update_qr_process()

    # 调整分段数处理函数 即文件总分段数 
    def recalculate_total(self, value): 
        total = 0 
        if (self.qr1_rect): 
            total += 1
        if (self.qr2_rect): 
            total += 1      
        if (self.qr3_rect): 
            total += 1
        if (self.qr4_rect): 
            total += 1 
        if (total == 0):
            return 
        size = value // total 
        lastSize = value - (size * (total-1)) 
        # set last one 
        lastIdx = 4 
        if (self.qr4_rect): 
            lastIdx = 4 
            self.qr4_total = lastSize 
        elif (self.qr3_rect): 
            lastIdx = 3 
            self.qr3_total = lastSize 
        elif (self.qr2_rect): 
            lastIdx = 2 
            self.qr2_total = lastSize 
        elif (self.qr1_rect): 
            lastIdx = 1 
            self.qr1_total = lastSize            
        # set other's  
        for i in range(lastIdx): 
            if (i == 1 and self.qr1_rect): 
                self.qr1_total = size 
            elif (i == 2 and self.qr2_rect): 
                self.qr2_total = size 
            elif (i == 3 and self.qr3_rect): 
                self.qr3_total = size 
            elif (i == 4 and self.qr4_rect): 
                self.qr4_total = size               
    # 
        
    def select_qr1_area(self): 
        self.log_area.append("请框选二维码区域1...")
        current_screen = self.screen()
        self.selection_area = SelectionArea(self, "1")
        self.selection_area.setGeometry(current_screen.geometry())
        self.selection_area.show()
        self.selection_area.raise_()
        self.selection_area.activateWindow()

    def select_qr2_area(self): 
        self.log_area.append("请框选二维码区域2...")
        current_screen = self.screen()
        self.selection_area = SelectionArea(self, "2")
        self.selection_area.setGeometry(current_screen.geometry())
        self.selection_area.show()
        self.selection_area.raise_()
        self.selection_area.activateWindow()

    def select_qr3_area(self): 
        self.log_area.append("请框选二维码区域3...")
        current_screen = self.screen()
        self.selection_area = SelectionArea(self, "3")
        self.selection_area.setGeometry(current_screen.geometry())
        self.selection_area.show()
        self.selection_area.raise_()
        self.selection_area.activateWindow()
    def select_qr4_area(self): 
        self.log_area.append("请框选二维码区域4...")
        current_screen = self.screen()
        self.selection_area = SelectionArea(self, "4")
        self.selection_area.setGeometry(current_screen.geometry())
        self.selection_area.show()
        self.selection_area.raise_()
        self.selection_area.activateWindow()


    def browse_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "选择文件存储路径", "", "All Files (*)")
        if file_path:
            self.file_path_input.setText(file_path)

    def show_alert(self, title, message, icon=QMessageBox.Icon.Information):
        """
        显示一个消息框
        :param title: 消息框标题
        :param message: 消息内容
        :param icon: 消息框图标类型，默认为信息图标
        """
        msg = QMessageBox()
        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()

    def check_can_start(self): 
        if not self.file_path_input.text():
            self.show_alert("错误", "请选择文件存储路径", QMessageBox.Icon.Warning)
            return False
        
        if self.segment_count_input.value() <= 0:
            self.show_alert("错误", "文件分段数必须大于0", QMessageBox.Icon.Warning)
            return False
            
        if not (self.qr1_rect or self.qr2_rect or self.qr3_rect or self.qr4_rect):
            self.show_alert("错误", "请至少选择一个二维码监控区域", QMessageBox.Icon.Warning)
            return False
            
        return True

    def toggle_controls(self, enabled):
        """启用或禁用控件"""
        for widget in self.control_widgets:
            widget.setEnabled(enabled)

    def start_recognition(self):
        if not self.check_can_start():
            return
            
        # 清理旧数据
        self.collected_data.clear()
        self.total_segments = self.segment_count_input.value()
        
        # 创建并启动识别线程
        self.recognition_thread = RecognitionThread(self.screenshot_queue)
        self.recognition_thread.data_recognized.connect(self.on_data_recognized)
        self.recognition_thread.error_occurred.connect(self.on_error_occurred)
        self.recognition_thread.start()
        
        # 启动截图定时器
        interval = int(1000 / self.frame_rate_input.value())
        self.screenshot_timer.setInterval(interval)
        self.screenshot_timer.start()
        
        # 禁用控件
        self.toggle_controls(False)
        self.log_message("开始识别...")

    def capture_screen(self):
        """捕获屏幕区域"""
        try:
            # 计算需要截取的总区域
            x, y, width, height = self.calculate_capture_area()
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            screenshot_np = np.array(screenshot)
            
            # 发送到识别线程
            self.screenshot_queue.put(screenshot_np)
            
            # 更新预览
            self.update_preview(screenshot_np)
            
        except Exception as e:
            self.log_message(f"截图错误: {str(e)}")

    def calculate_capture_area(self):
        """计算需要截取的总区域"""
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        # 遍历所有选择的区域
        for rect in [self.qr1_rect, self.qr2_rect, self.qr3_rect, self.qr4_rect]:
            if rect:
                min_x = min(min_x, rect.x())
                min_y = min(min_y, rect.y())
                max_x = max(max_x, rect.x() + rect.width())
                max_y = max(max_y, rect.y() + rect.height())
                
        width = max_x - min_x
        height = max_y - min_y
        return min_x, min_y, width, height

    def on_data_recognized(self, index, data_content):
        """处理识别到的数据"""
        if index not in self.collected_data:
            self.collected_data[index] = data_content
            self.log_message(f"识别到数据片段 {index}")
            
            # 更新进度
            progress = len(self.collected_data)
            self.update_progress(progress)
            
            # 检查是否完成
            if progress >= self.total_segments:
                self.complete_recognition()

    def complete_recognition(self):
        """完成识别处理"""
        self.screenshot_timer.stop()
        self.recognition_thread.stop()
        self.recognition_thread.wait()
        
        # 处理收集到的数据
        self.process_collected_data()
        
        # 恢复控件状态
        self.toggle_controls(True)
        self.log_message("识别完成")

    def stop_recognition(self):
        """停止识别"""
        self.screenshot_timer.stop()
        if hasattr(self, 'recognition_thread'):
            self.recognition_thread.stop()
            self.recognition_thread.wait()
        self.toggle_controls(True)
        self.log_message("停止识别")

    def pause_recognition(self):
        """暂停/继续识别"""
        if self.screenshot_timer.isActive():
            self.screenshot_timer.stop()
            self.pause_button.setText("继续")
        else:
            self.screenshot_timer.start()
            self.pause_button.setText("暂停")

    def monitor_qr_area(self):
        self.log_area.append("请框选二维码区域...")
        current_screen = self.screen()
        self.selection_area = SelectionArea(self)
        #self.selection_area.showFullScreen()  # 全屏显示选择区域
        # 设置选择区域窗口的位置为当前屏幕
        self.selection_area.setGeometry(current_screen.geometry())
        self.selection_area.show()
        self.selection_area.raise_()
        self.selection_area.activateWindow()

    def set_selection(self, rect, area_idx):
        x, y, width, height = rect.x(), rect.y(), rect.width(), rect.height()
        self.log_area.append(f"选择的区域:{area_idx} = ({x}, {y}, {width}, {height})") 
        if (area_idx == "1"): 
            self.monitor_qr1_label.setText(f"({x},{y}) ({width},{height})")
            self.qr1_rect = rect
            self.update_qr_process()
        elif (area_idx == "2"): 
            self.monitor_qr2_label.setText(f"({x},{y}) ({width},{height})")
            self.qr2_rect = rect
            self.update_qr_process()
        elif (area_idx == "3"): 
            self.monitor_qr3_label.setText(f"({x},{y}) ({width},{height})")
            self.qr3_rect = rect
            self.update_qr_process()
        elif (area_idx == "4"): 
            self.monitor_qr4_label.setText(f"({x},{y}) ({width},{height})")
            self.qr4_rect = rect
            self.update_qr_process()
        #self.monitoring = True
        #threading.Thread(target=self.capture_and_recognize, args=(x, y, width, height)).start()

    def capture_and_recognize(self, x, y, width, height):
        while self.monitoring:
            # 截取屏幕
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            screenshot_np = np.array(screenshot)
            screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)

            # 识别二维码
            detector = cv2.QRCodeDetector()
            data, bbox, _ = detector(screenshot_gray)

            if data:
                self.log_area.append(f"识别到二维码数据: {data}")

            # 暂停一段时间以避免过于频繁的截屏
            cv2.waitKey(1000)  # 每秒截取一次

