import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QSpinBox
from PyQt5.QtCore import QRect
from recognition_thread import RecognitionThread
from PyQt5.QtGui import QPixmap

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("二维码识别测试")
        self.setGeometry(100, 100, 400, 500)

        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建坐标输入控件
        self.create_coordinate_inputs(layout)
        
        # 预览图像显示
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(200, 200)
        self.preview_label.setStyleSheet("border: 1px solid black;")
        layout.addWidget(self.preview_label)

        # 识别结果显示
        self.result_label = QLabel("识别结果：")
        layout.addWidget(self.result_label)

        # 开始/停止按钮
        self.start_button = QPushButton("开始识别")
        self.start_button.clicked.connect(self.toggle_recognition)
        layout.addWidget(self.start_button)

        self.recognition_thread = None
        self.is_running = False

    def create_coordinate_inputs(self, layout):
        # X坐标
        x_label = QLabel("X:")
        self.x_input = QSpinBox()
        self.x_input.setMaximum(3000)
        self.x_input.setValue(1121)
        layout.addWidget(x_label)
        layout.addWidget(self.x_input)

        # Y坐标
        y_label = QLabel("Y:")
        self.y_input = QSpinBox()
        self.y_input.setMaximum(3000)
        self.y_input.setValue(98)
        layout.addWidget(y_label)
        layout.addWidget(self.y_input)

        # 宽度
        width_label = QLabel("宽度:")
        self.width_input = QSpinBox()
        self.width_input.setMaximum(1000)
        self.width_input.setValue(386)
        layout.addWidget(width_label)
        layout.addWidget(self.width_input)

        # 高度
        height_label = QLabel("高度:")
        self.height_input = QSpinBox()
        self.height_input.setMaximum(1000)
        self.height_input.setValue(386)
        layout.addWidget(height_label)
        layout.addWidget(self.height_input)

    def toggle_recognition(self):
        if not self.is_running:
            self.start_recognition()
        else:
            self.stop_recognition()

    def start_recognition(self):
        rect = QRect(
            self.x_input.value(),
            self.y_input.value(),
            self.width_input.value(),
            self.height_input.value()
        )

        self.recognition_thread = RecognitionThread(
            rect=rect,
            qr_index=1,
            total_segments=100,  # 测试用，设置较大的值
            frame_rate=1,
            preview_size=200
        )

        # 连接信号
        self.recognition_thread.preview_updated.connect(self.update_preview)
        self.recognition_thread.data_recognized.connect(self.on_data_recognized)
        self.recognition_thread.error_occurred.connect(self.on_error)

        self.recognition_thread.start()
        self.is_running = True
        self.start_button.setText("停止识别")

    def stop_recognition(self):
        if self.recognition_thread:
            self.recognition_thread.stop()
            self.recognition_thread.wait()
            self.recognition_thread = None
        
        self.is_running = False
        self.start_button.setText("开始识别")

    def update_preview(self, qr_index, pixmap):
        self.preview_label.setPixmap(pixmap)

    def on_data_recognized(self, qr_index, segment_index, data):
        self.result_label.setText(f"识别结果：段索引={segment_index}, 数据长度={len(data)}字节")

    def on_error(self, error_message):
        self.result_label.setText(f"错误：{error_message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec()) 