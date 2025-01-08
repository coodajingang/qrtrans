# gui.py
from PyQt6.QtWidgets import QMainWindow, QFileDialog,QDialog,QPushButton, QSpinBox, QLabel, QVBoxLayout,QHBoxLayout, QWidget, QTabWidget, QTextEdit, QGridLayout
from PyQt6.QtCore import QTimer
from data_transfer import send_file
from PyQt6.QtGui import QPixmap, QAction, QIcon

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
        self.log_area.append(message)  # 将消息添加到日志区域

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if file_path:
            self.log_message(f"正在上传文件: {file_path}")  # 记录日志
            frame_rate = 1000 / self.frame_rate_spinbox.value()  # 转换为毫秒
            qr_count = self.qr_count_spinbox.value()
            qr_width = self.qrcode_size_label_spinbox.value()
            data_chunk_size = self.data_chunk_size_spinbox.value()  # 获取数据分段大小
            self.qr_code_groups = send_file(file_path, frame_rate, qr_count, data_chunk_size, self, qr_width, qr_width)  # 调用发送文件函数
            self.log_message(f"文件分段数：{len(self.qr_code_groups)}")
            self.qr1_start.setRange(0, len(self.qr_code_groups))
            self.qr2_start.setRange(0, len(self.qr_code_groups))
            self.qr3_start.setRange(0, len(self.qr_code_groups))
            self.qr4_start.setRange(0, len(self.qr_code_groups))
            self.qr1_end.setRange(0, len(self.qr_code_groups))
            self.qr2_end.setRange(0, len(self.qr_code_groups))
            self.qr3_end.setRange(0, len(self.qr_code_groups))
            self.qr4_end.setRange(0, len(self.qr_code_groups))
            if (len(self.qr_code_groups) < 100) :
                self.qr_count_spinbox.setValue(1)
                qr_count = 1
            # 新增代码：更新二维码展示框和数据范围
            for i in range(qr_count):
                start_index = i * (len(self.qr_code_groups) // qr_count)
                end_index = (i + 1) * (len(self.qr_code_groups) // qr_count) if i < qr_count - 1 else len(self.qr_code_groups) - 1
                #self.qr_code_ranges[i].setText(f"范围: {start_index} - {end_index}")  # 更新范围标签
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
                    
                    # self.qr4_ranges.setText(f"范围: {start_index} - {end_index}") 
                    # self.qr4_idx = start_index
                    # self.qr4_label.setPixmap(self.qr_code_groups[start_index])
                    # self.qr_layout.addWidget(self.qr4_label, i // 2, i % 2)  # 2x2布局
                    # self.qr4_start.setValue(start_index)
                    # self.qr4_end.setValue(end_index)
                    # self.qr_layout.addWidget(self.qr4_start, (i // 2) + 5, i % 2) 
                    # self.qr_layout.addWidget(self.qr4_end, (i // 2) + 5, i % 2)   
                    # self.qr_layout.addWidget(self.qr_code_ranges[i], (i // 2) + 5, i % 2)        
            # self.current_qr_index = [0] * qr_count  # 初始化每个分组的当前索引
            # self.timer.start(frame_rate)  # 启动定时器
            # self.update_ranges()  # 更新范围显示
            self.timer = QTimer(self)
            self.timer.setInterval(int(frame_rate))
            self.timer.timeout.connect(self.show_next_qr_code2)
            self.timer.start()
            # 启用控制按钮
            self.start_action.setEnabled(False)
            self.pause_action.setEnabled(True)
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
        qr_count = self.qr_count_spinbox.value() 
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

    def start_display(self):
        """开始显示二维码"""
        if hasattr(self, 'timer'):
            self.timer.start()
            self.start_action.setEnabled(False)
            self.pause_action.setEnabled(True)
            self.log_message("开始显示二维码")

    def pause_display(self):
        """暂停显示二维码"""
        if hasattr(self, 'timer'):
            self.timer.stop()
            self.start_action.setEnabled(True)
            self.pause_action.setEnabled(False)
            self.log_message("暂停显示二维码")