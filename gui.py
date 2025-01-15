# gui.py
from PyQt6.QtWidgets import QMainWindow, QFileDialog,QDialog,QPushButton, QSpinBox, QLabel, QVBoxLayout,QHBoxLayout, QWidget, QTabWidget, QTextEdit, QGridLayout
from PyQt6.QtCore import QTimer
from data_transfer import send_file, FileProcessThread
from PyQt6.QtGui import QPixmap, QAction, QIcon
from param_qr import format_transfer_params
import os
from qr_generator import generate_qr_code
from PyQt6.QtCore import Qt
from PIL.ImageQt import ImageQt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("二维码数据传输系统")
        self.setGeometry(100, 100, 800, 600)

        # 创建菜单栏
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("文件")
        open_action = QAction("打开文件", self)
        open_action.triggered.connect(self.upload_file)
        file_menu.addAction(open_action)

        # Add a new action for parameter settings in the menu bar
        param_settings_menu = menu_bar.addMenu("参数设置")
        param_settings_action = QAction("参数设置", self)
        param_settings_action.triggered.connect(self.open_param_settings)
        param_settings_menu.addAction(param_settings_action)

        log_view_menu = menu_bar.addMenu("查看日志")
        log_view_action = QAction("查看日志", self)
        log_view_action.triggered.connect(self.show_log_view)
        log_view_menu.addAction(log_view_action)

        # Add a new action for parameter QR code in the menu bar
        param_qr_menu = menu_bar.addMenu("参数二维码")
        show_param_qr_action = QAction("显示参数二维码", self)
        show_param_qr_action.triggered.connect(self.show_param_qr)
        show_param_qr_action.setEnabled(False)  # 初始时禁用
        param_qr_menu.addAction(show_param_qr_action)
        self.show_param_qr_action = show_param_qr_action

        # 添加控制菜单
        control_menu = menu_bar.addMenu("控制")
        
        # 添加开始按钮
        self.start_action = QAction("开始", self)
        self.start_action.triggered.connect(self.start_display)
        self.start_action.setEnabled(False)  # 初始时禁用
        control_menu.addAction(self.start_action)
        
        # 添加暂停按钮
        self.pause_action = QAction("暂停", self)
        self.pause_action.triggered.connect(self.pause_display)
        self.pause_action.setEnabled(False)  # 初始时禁用
        control_menu.addAction(self.pause_action)

        # 创建主布局
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # 日志区域
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)  # 设置为只读
        # self.param_layout.addWidget(self.log_area)

        self.qr_layout = QGridLayout(self.central_widget)


        # 初始化二维码图像框
        # self.qr_code_labels = []
        # # self.qr_code_ranges = []
        # self.qr_range_spinboxes = []  # 用于动态调整分组范围
        # self.current_qr_index = []  # 存储每个分组的当前索引
        self.qr_code_groups = []  # 存储二维码分组 

        self.qr1_start = QSpinBox()
        self.qr1_end = QSpinBox()
        self.qr1_label = QLabel(self)
        self.qr1_label.setScaledContents(False)
        self.qr2_start = QSpinBox()
        self.qr2_end = QSpinBox()
        self.qr2_label = QLabel(self)
        self.qr2_label.setScaledContents(False)
        self.qr3_start = QSpinBox()
        self.qr3_end = QSpinBox()
        self.qr3_label = QLabel(self)
        self.qr3_label.setScaledContents(False)
        self.qr4_start = QSpinBox()
        self.qr4_end = QSpinBox()
        self.qr4_label = QLabel(self)
        self.qr4_label.setScaledContents(False)
        self.qr1_idx = -1
        self.qr2_idx = -1
        self.qr3_idx = -1
        self.qr4_idx = -1
        self.qr1_ranges = QLabel(self)
        self.qr2_ranges = QLabel(self)
        self.qr3_ranges = QLabel(self)
        self.qr4_ranges = QLabel(self)
        self.qr1_idx_label = QLabel(self)
        self.qr2_idx_label = QLabel(self)
        self.qr3_idx_label = QLabel(self)
        self.qr4_idx_label = QLabel(self)
        self.frame_rate = 30   # 帧率 
        self.chunk_size = 200  # 数据分段大小
        self.qrcode_size = 400 # 每个二维码的宽度
        self.qrcode_count = 4  # 显示的qr个数
        self.thread_count = 4  # 添加线程数属性
        
        # 添加日志显示区域到主界面
        self.main_log_area = QTextEdit()
        self.main_log_area.setReadOnly(True)
        self.qr_layout.addWidget(self.main_log_area, 2, 0, 1, 2)  # 在二维码网格下方显示

        self.process_thread = None  # 添加线程引用
        
    def appendQrLayout(self, qrLabel, start_index, end_index, startSpin, endSpin, indexLabel): 
        vbox = QVBoxLayout()
        vbox.addWidget(qrLabel)
        rangeText = QLabel()
        rangeText.setText(f"{start_index}-{end_index}") 
        hbox2 = QHBoxLayout()
        hbox2.addWidget(rangeText)
        hbox2.addWidget(indexLabel)
        hbox2.addWidget(startSpin)
        hbox2.addWidget(endSpin)
        vbox.addLayout(hbox2)
        container = QWidget()
        container.setLayout(vbox)
        return container


    def log_message(self, message):
        """在日志区域输出消息"""
        self.log_area.append(message)
        self.main_log_area.append(message)

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if file_path:
            # 如果有正在运行的线程，先停止它
            if self.process_thread is not None:
                self.process_thread.stop()
                self.process_thread = None

            # 确保主界面日志区域可见
            self.main_log_area.show()
            self.log_message(f"正在上传文件: {file_path}")
            frame_rate = 1000 / self.frame_rate
            qr_count = self.qrcode_count
            qr_width = self.qrcode_size
            data_chunk_size = self.chunk_size

            self.log_message(f"使用参数 qr_count={qr_count}, qr_size={qr_width}, chunk_size={data_chunk_size}")
            
            # 创建新的处理线程
            self.process_thread = FileProcessThread(
                file_path, frame_rate, qr_count, data_chunk_size, 
                qr_width, qr_width, self.thread_count
            )
            self.process_thread.progress_updated.connect(self.log_message)
            self.process_thread.qr_codes_ready.connect(self.on_qr_codes_ready)
            self.process_thread.start()
            
            self.current_file_path = file_path

    def on_qr_idx_change(self, idx, start_end, value): 
        self.log_message(f"qr index change: {idx} {start_end} {value}")
        if (idx == 1 and start_end == 'start'):
            self.qr1_start.setValue(value)
        elif (idx == 1 and start_end == 'end'):
            self.qr1_end.setValue(value)
        elif (idx == 2 and start_end == 'start'):
            self.qr2_start.setValue(value)
        elif (idx == 2 and start_end == 'end'):
            self.qr2_end.setValue(value)
        elif (idx == 3 and start_end == 'start'):
            self.qr3_start.setValue(value)
        elif (idx == 3 and start_end == 'end'):
            self.qr3_end.setValue(value)
        elif (idx == 4 and start_end == 'start'):
            self.qr4_start.setValue(value)
        elif (idx == 4 and start_end == 'end'):
            self.qr4_end.setValue(value)


    def show_next_qr_code2(self): 
        qr_count = self.qrcode_count
        for i in range(qr_count): 
            if (i == 0): 
                start = self.qr1_start.value()
                end = self.qr1_end.value() 
                idx = self.qr1_idx + 1
                if (idx > end or idx < start) :
                    idx = start
                self.qr1_idx_label.setText(f"{idx}")
                self.qr1_label.setPixmap(self.qr_code_groups[idx])
                self.qr1_idx = idx 
            elif (i == 1): 
                start = self.qr2_start.value()
                end = self.qr2_end.value() 
                idx = self.qr2_idx + 1
                if (idx > end or idx < start) :
                    idx = start
                self.qr2_idx_label.setText(f"{idx}")
                self.qr2_label.setPixmap(self.qr_code_groups[idx])
                self.qr2_idx = idx 
            elif (i == 2): 
                start = self.qr3_start.value()
                end = self.qr3_end.value() 
                idx = self.qr3_idx + 1
                if (idx > end or idx < start) :
                    idx = start
                self.qr3_idx_label.setText(f"{idx}")
                self.qr3_label.setPixmap(self.qr_code_groups[idx])
                self.qr3_idx = idx 
            elif (i == 3): 
                start = self.qr4_start.value()
                end = self.qr4_end.value() 
                idx = self.qr4_idx + 1
                if (idx > end or idx < start) :
                    idx = start
                self.qr4_idx_label.setText(f"{idx}")
                self.qr4_label.setPixmap(self.qr_code_groups[idx])
                self.qr4_idx = idx 
                
                

    # def show_next_qr_code(self):
    #     qr_count = self.qr_count_spinbox.value()
    #     for i in range(qr_count):
    #         if self.qr_code_groups[i]:
    #             # 显示当前二维码
    #             qr_code_image = self.qr_code_groups[i][0][self.current_qr_index[i]]  # 获取二维码图像
    #             qr_code_image.save("current_qr_code.png")  # 保存当前二维码为临时文件
    #             pixmap = QPixmap("current_qr_code.png")
    #             self.qr_code_labels[i].setPixmap(pixmap)  # 显示二维码
    #             self.current_qr_index[i] = (self.current_qr_index[i] + 1) % len(self.qr_code_groups[i][0])  # 循环播放

    # def resizeEvent(self, event):
    #     # 响应式调整图像框大小
    #     for label in self.qr_code_labels:
    #         label.setFixedSize(self.qr_layout.sizeHint().width() // 2, self.qr_layout.sizeHint().height() // 2)
    #     super().resizeEvent(event)

    def show_log_view(self):
        """Open the log view dialog."""
        self.log_view_dialog = QDialog(self)
        self.log_view_dialog.setWindowTitle("日志查看")
        self.log_view_dialog.setGeometry(150, 150, 600, 400)
        log_layout = QVBoxLayout(self.log_view_dialog)

        # Create a text area to display logs
        self.log_display_area = QTextEdit(self.log_view_dialog)
        self.log_display_area.setReadOnly(True)  # Set to read-only
        log_layout.addWidget(self.log_display_area)

        # Populate the log display area with existing logs
        self.log_display_area.setPlainText(self.log_area.toPlainText())  # Copy logs from the main log area

        # Add a close button
        close_button = QPushButton("关闭", self)
        close_button.clicked.connect(self.log_view_dialog.close)  # Connect button to close the dialog
        log_layout.addWidget(close_button)
        self.log_view_dialog.setLayout(log_layout)
        self.log_view_dialog.exec()

    def open_param_settings(self):
        """Open the parameter settings dialog."""
        self.param_settings_dialog = QDialog(self)
        self.param_settings_dialog.setWindowTitle("参数设置")
        self.param_settings_dialog.setGeometry(150, 150, 400, 300)
        param_layout = QVBoxLayout(self.param_settings_dialog)

        # Move parameter configuration code here
        self.frame_rate_label = QLabel("帧率 (帧/秒):1-100", self)
        param_layout.addWidget(self.frame_rate_label)
        self.frame_rate_spinbox = QSpinBox(self)
        self.frame_rate_spinbox.setRange(1, 100)  # 设置帧率范围
        self.frame_rate_spinbox.setValue(self.frame_rate)  # 默认值
        self.frame_rate_spinbox.valueChanged.connect(self.on_frame_rate_change)
        param_layout.addWidget(self.frame_rate_spinbox)

        self.qr_count_label = QLabel("二维码数量:1-4", self)
        param_layout.addWidget(self.qr_count_label)
        self.qr_count_spinbox = QSpinBox(self)
        self.qr_count_spinbox.setRange(1, 4)  # 最多4个二维码
        self.qr_count_spinbox.setValue(self.qrcode_count)  # 默认值改为4
        self.qr_count_spinbox.valueChanged.connect(self.on_qrcode_count_change)
        param_layout.addWidget(self.qr_count_spinbox)

        self.data_chunk_size_label = QLabel("数据分段大小:1-2048", self)  # 改为数据分段大小
        param_layout.addWidget(self.data_chunk_size_label)
        self.data_chunk_size_spinbox = QSpinBox(self)
        self.data_chunk_size_spinbox.setRange(1, 2048)  # 数据分段大小范围
        self.data_chunk_size_spinbox.setValue(self.chunk_size)  # 默认值
        self.data_chunk_size_spinbox.valueChanged.connect(self.on_chunk_size_change)
        param_layout.addWidget(self.data_chunk_size_spinbox)

        # qr code width height 
        self.qrcode_size_label = QLabel("二维码大小:1-600", self)
        param_layout.addWidget(self.qrcode_size_label)
        self.qrcode_size_label_spinbox = QSpinBox(self)
        self.qrcode_size_label_spinbox.setRange(1, 600)  # 数据分段大小范围
        self.qrcode_size_label_spinbox.setValue(self.qrcode_size)  # 默认值
        self.qrcode_size_label_spinbox.valueChanged.connect(self.on_qrcode_size_change)
        param_layout.addWidget(self.qrcode_size_label_spinbox)

        # 在关闭按钮之前添加线程数设置
        self.thread_count_label = QLabel("生成二维码线程数:1-8", self)
        param_layout.addWidget(self.thread_count_label)
        self.thread_count_spinbox = QSpinBox(self)
        self.thread_count_spinbox.setRange(1, 8)
        self.thread_count_spinbox.setValue(self.thread_count)
        self.thread_count_spinbox.valueChanged.connect(self.on_thread_count_change)
        param_layout.addWidget(self.thread_count_spinbox)

        # Add a close button
        close_button = QPushButton("关闭", self)
        close_button.clicked.connect(self.param_settings_dialog.close)  # Connect button to close the dialog
        param_layout.addWidget(close_button)

        self.param_settings_dialog.setLayout(param_layout)
        self.param_settings_dialog.exec()  # Show the dialog as a modal
    def on_chunk_size_change(self, value): 
        self.chunk_size = value
    def on_qrcode_size_change(self, value): 
        self.qrcode_size = value
    def on_qrcode_count_change(self, value): 
        self.qrcode_count = value
    def on_frame_rate_change(self, value): 
        self.frame_rate = value
    def on_thread_count_change(self, value):
        self.thread_count = value

    def start_display(self):
        """开始显示二维码"""
        if hasattr(self, 'timer'):
            # 隐藏主界面日志区域
            self.main_log_area.hide()
            self.timer.start()
            self.start_action.setEnabled(False)
            self.pause_action.setEnabled(True)
            self.log_message("开始显示二维码")
            # 显示参数二维码对话框
            self.show_param_qr()

    def pause_display(self):
        """暂停显示二维码"""
        if hasattr(self, 'timer'):
            self.timer.stop()
            self.start_action.setEnabled(True)
            self.pause_action.setEnabled(False)
            self.log_message("暂停显示二维码")

    def show_param_qr(self):
        """显示包含传输参数的二维码"""
        if not hasattr(self, 'current_file_path') or not self.qr_code_groups:
            return
        
        # 收集当前的参数
        filename = os.path.basename(self.current_file_path)
        chunk_ranges = [
            (self.qr1_start.value(), self.qr1_end.value()),
            (self.qr2_start.value(), self.qr2_end.value()),
            (self.qr3_start.value(), self.qr3_end.value()),
            (self.qr4_start.value(), self.qr4_end.value())
        ][:self.qrcode_count]  # 只取实际使用的QR码数量
        
        # 格式化参数
        encoded_params = format_transfer_params(
            filename=filename,
            frame_rate=self.frame_rate,
            qr_count=self.qrcode_count,
            total_chunks=len(self.qr_code_groups),
            chunk_ranges=chunk_ranges,
            chunks_size=self.chunk_size
        )
        
        # 生成参数二维码
        param_qr = generate_qr_code(encoded_params, 400, 400)
        
        # 创建对话框显示参数二维码
        dialog = QDialog(self)
        dialog.setWindowTitle("传输参数二维码")
        layout = QVBoxLayout()
        
        # 转换PIL Image为QPixmap
        qr_label = QLabel()
        qr_pixmap = QPixmap.fromImage(ImageQt(param_qr))
        qr_label.setPixmap(qr_pixmap)
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 添加说明文本
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setText(f"""参数信息：
文件名：{filename}
帧率：{self.frame_rate} fps
二维码数量：{self.qrcode_count}
总分段数：{len(self.qr_code_groups)}
分段大小：{self.chunk_size}
分段范围：{chunk_ranges}""")
        
        layout.addWidget(qr_label)
        layout.addWidget(info_text)
        
        # 添加关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)
        
        dialog.setLayout(layout)
        dialog.exec()

    def on_qr_codes_ready(self, qr_codes):
        """当二维码生成完成时调用"""
        self.qr_code_groups = qr_codes
        self.log_message(f"二维码生成完成，共 {len(qr_codes)} 个")
        frame_rate = 1000 / self.frame_rate
        # 更新范围设置
        self.qr1_start.setRange(0, len(self.qr_code_groups))
        self.qr2_start.setRange(0, len(self.qr_code_groups))
        self.qr3_start.setRange(0, len(self.qr_code_groups))
        self.qr4_start.setRange(0, len(self.qr_code_groups))
        self.qr1_end.setRange(0, len(self.qr_code_groups))
        self.qr2_end.setRange(0, len(self.qr_code_groups))
        self.qr3_end.setRange(0, len(self.qr_code_groups))
        self.qr4_end.setRange(0, len(self.qr_code_groups))

        qr_count = self.qrcode_count
        if (len(self.qr_code_groups) < 100):
            #self.qr_count_spinbox.setValue(1)
            self.qrcode_count = 1
            qr_count = 1

        # 更新二维码显示
        for i in range(qr_count):
            start_index = i * (len(self.qr_code_groups) // qr_count)
            end_index = (i + 1) * (len(self.qr_code_groups) // qr_count) if i < qr_count - 1 else len(self.qr_code_groups) - 1
            self.log_message(f"分段{i}: {start_index} - {end_index}")
        
            if (i == 0) :
                self.qr1_idx = start_index
                self.qr1_label.setPixmap(self.qr_code_groups[start_index])
                self.qr1_start.setValue(start_index)
                self.qr1_end.setValue(end_index)
                self.qr1_start.valueChanged.connect(lambda value: self.on_qr_idx_change(1, "start", value))
                self.qr1_end.valueChanged.connect(lambda value: self.on_qr_idx_change(1, "end", value))
                self.qr1_idx_label.setText(f"{start_index}")
                self.qr_layout.addWidget(self.appendQrLayout(self.qr1_label, start_index, end_index, self.qr1_start, self.qr1_end, self.qr1_idx_label),0,0)
            if (i == 1) :
                self.qr2_idx = start_index
                self.qr2_label.setPixmap(self.qr_code_groups[start_index])
                self.qr2_start.setValue(start_index)
                self.qr2_end.setValue(end_index)
                self.qr2_start.valueChanged.connect(lambda value: self.on_qr_idx_change(2, "start", value))
                self.qr2_end.valueChanged.connect(lambda value: self.on_qr_idx_change(2, "end", value))
                self.qr2_idx_label.setText(f"{start_index}")
                self.qr_layout.addWidget(self.appendQrLayout(self.qr2_label, start_index, end_index, self.qr2_start, self.qr2_end, self.qr2_idx_label), 0,1)
            if (i == 2) :
                self.qr3_idx = start_index
                self.qr3_label.setPixmap(self.qr_code_groups[start_index])
                self.qr3_start.setValue(start_index)
                self.qr3_end.setValue(end_index)
                self.qr3_start.valueChanged.connect(lambda value: self.on_qr_idx_change(3, "start", value))
                self.qr3_end.valueChanged.connect(lambda value: self.on_qr_idx_change(3, "end", value))
                self.qr3_idx_label.setText(f"{start_index}")
                self.qr_layout.addWidget(self.appendQrLayout(self.qr3_label, start_index, end_index, self.qr3_start, self.qr3_end, self.qr3_idx_label),1, 0)
                            
            if (i == 3) :
                self.qr4_idx = start_index
                self.qr4_label.setPixmap(self.qr_code_groups[start_index])
                self.qr4_start.setValue(start_index)
                self.qr4_end.setValue(end_index)
                self.qr4_start.valueChanged.connect(lambda value: self.on_qr_idx_change(4, "start", value))
                self.qr4_end.valueChanged.connect(lambda value: self.on_qr_idx_change(4, "end", value))
                self.qr4_idx_label.setText(f"{start_index}")
                self.qr_layout.addWidget(self.appendQrLayout(self.qr4_label, start_index, end_index, self.qr4_start, self.qr4_end, self.qr4_idx_label),1, 1)
                
        self.timer = QTimer(self)
        self.timer.setInterval(int(frame_rate))
        self.timer.timeout.connect(self.show_next_qr_code2)
        self.timer.start()

        # 启用相关按钮
        self.start_action.setEnabled(False)
        self.pause_action.setEnabled(True)
        self.show_param_qr_action.setEnabled(True)

    def closeEvent(self, event):
        """窗口关闭时的处理"""
        # 停止所有正在运行的线程
        if self.process_thread is not None:
            self.process_thread.stop()
            self.process_thread = None
        
        if hasattr(self, 'timer'):
            self.timer.stop()
        
        event.accept()