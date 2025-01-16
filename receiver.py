# main.py
import sys
from PyQt5.QtWidgets import QApplication
from rece_gui import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # 示例：调用 log_message 方法
    #window.log_message("Receiver 应用程序启动成功！")  # 记录日志

    sys.exit(app.exec())