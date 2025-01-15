from PyQt6.QtCore import QThread, pyqtSignal
import numpy as np
import cv2
from qr_recognizer import recognize_qr_code, parse_qr_data

class RecognitionThread(QThread):
    # 定义信号
    data_recognized = pyqtSignal(int, bytes)  # (segment_index, data_content)
    error_occurred = pyqtSignal(str)  # error message
    qrcode_count_signal = pyqtSignal(int) # qrcode_count
    
    def __init__(self, data_queue):
        super().__init__()
        self.data_queue = data_queue  # 用于接收截图数据的队列
        self.is_running = True
        
    def run(self):
        while self.is_running:
            try:
                # 从队列中获取截图数据
                screenshot_np = self.data_queue.get()
                if screenshot_np is None:  # 终止信号
                    break
                    
                # 识别二维码
                qr_data_list = recognize_qr_code(screenshot_np)
                if qr_data_list:
                    self.qrcode_count_signal.emit(len(qr_data_list))
                    for data in qr_data_list:
                        try:
                            index, data_content, is_valid = parse_qr_data(data)
                            if is_valid:
                                self.data_recognized.emit(index, data_content)
                            else: 
                                self.error_occurred.emit("invaliad")
                        except ValueError as e:
                            print(e)
                            self.error_occurred.emit(str(e))
                            
            except Exception as e:
                self.error_occurred.emit(f"Recognition error: {str(e)}")
                
    def stop(self):
        self.is_running = False
        self.data_queue.put(None)  # 发送终止信号 