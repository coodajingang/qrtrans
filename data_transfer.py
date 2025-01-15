# data_transfer.py
from file_handler import compress_file, split_data
from qr_generator import generate_qr_code
import zlib
import base64
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QThread, pyqtSignal
from PIL.ImageQt import ImageQt
import threading
from queue import Queue
import math
import time

class QRCodeGeneratorThread(QThread):
    def __init__(self, chunks, start_idx, end_idx, width, height, result_queue):
        super().__init__()
        self.chunks = chunks
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.width = width
        self.height = height
        self.result_queue = result_queue

    def run(self):
        for index in range(self.start_idx, self.end_idx):
            c = self.chunks[index]
            # 计算数据长度和 CRC32 校验码
            data_length = len(c)
            crc32_checksum = zlib.crc32(c)
            
            # 构建新的数据格式
            formatted_chunk = (
                index.to_bytes(4, byteorder='big') +  # 序号 (4字节)
                data_length.to_bytes(2, byteorder='big') +  # 数据长度 (2字节)
                c +  # 数据内容
                crc32_checksum.to_bytes(4, byteorder='big')  # CRC32 校验码 (4字节)
            )
            
            # 生成二维码并放入结果队列
            qr_code = QPixmap.fromImage(ImageQt(generate_qr_code(
                base64.b64encode(formatted_chunk).decode('utf-8'),
                self.width, 
                self.height
            )))
            self.result_queue.put((index, qr_code))

class FileProcessThread(QThread):
    progress_updated = pyqtSignal(str)  # 用于发送进度消息
    qr_codes_ready = pyqtSignal(list)   # 用于发送生成好的二维码列表
    
    def __init__(self, file_path, frame_rate, qr_count, data_chunk_size, width, height, thread_count):
        super().__init__()
        self.file_path = file_path
        self.frame_rate = frame_rate
        self.qr_count = qr_count
        self.data_chunk_size = data_chunk_size
        self.width = width
        self.height = height
        self.thread_count = thread_count
        self.running = True  # 添加控制标志

    def stop(self):
        """停止线程"""
        self.running = False
        self.wait()  # 等待线程结束

    def run(self):
        try:
            # 开始计时
            total_start_time = time.time()
            
            if not self.running:
                return

            # 压缩文件并分块
            preprocess_start_time = time.time()
            compressed_data = compress_file(self.file_path)
            chunks = split_data(compressed_data, self.data_chunk_size)
            preprocess_time = time.time() - preprocess_start_time
            
            self.progress_updated.emit(f"文件压缩后大小 {len(compressed_data)} 分段大小={self.data_chunk_size} 分段数={len(chunks)}")

            # 开始生成二维码计时
            qr_gen_start_time = time.time()

            # 创建结果队列和线程列表
            result_queue = Queue()
            threads = []
            qr_codes = [None] * len(chunks)  # 预分配结果列表

            # 计算每个线程处理的块数
            chunks_per_thread = math.ceil(len(chunks) / self.thread_count)
            
            # 创建并启动线程
            for i in range(self.thread_count):
                if not self.running:
                    return
                start_idx = i * chunks_per_thread
                end_idx = min((i + 1) * chunks_per_thread, len(chunks))
                
                thread = QRCodeGeneratorThread(
                    chunks=chunks,
                    start_idx=start_idx,
                    end_idx=end_idx,
                    width=self.width,
                    height=self.height,
                    result_queue=result_queue
                )
                threads.append(thread)
                thread.start()
                self.progress_updated.emit(f"启动线程 {i+1}: 处理范围 {start_idx}-{end_idx}")

            # 收集所有线程的结果
            completed_count = 0
            total_chunks = len(chunks)
            self.progress_updated.emit(f"开始生成二维码 请等待 , 耗时约{(total_chunks*20)/1000.0}s")
            while completed_count < total_chunks and self.running:
                index, qr_code = result_queue.get()
                qr_codes[index] = qr_code
                completed_count += 1
                
                # 每处理10%的数据更新一次进度
                if completed_count % max(1, total_chunks // 10) == 0:
                    progress = (completed_count / total_chunks) * 100
                    self.progress_updated.emit(f"二维码生成进度: {progress:.1f}%")

            # 如果线程被停止，提前退出
            if not self.running:
                return

            # 等待所有线程完成
            for thread in threads:
                thread.wait()

            # 计算耗时统计
            qr_gen_time = time.time() - qr_gen_start_time
            total_time = time.time() - total_start_time
            
            # 发送耗时统计信息
            self.progress_updated.emit("\n耗时统计:")
            self.progress_updated.emit(f"文件压缩和分段耗时: {preprocess_time:.2f}秒")
            self.progress_updated.emit(f"二维码生成耗时: {qr_gen_time:.2f}秒")
            self.progress_updated.emit(f"总耗时: {total_time:.2f}秒")
            self.progress_updated.emit(f"平均每个二维码生成耗时: {(qr_gen_time/len(chunks)*1000):.2f}毫秒")
            self.progress_updated.emit(f"生成了 {len(qr_codes)} 个二维码。")

            # 发送生成好的二维码列表
            self.qr_codes_ready.emit(qr_codes)

        except Exception as e:
            self.progress_updated.emit(f"错误: {str(e)}")
        finally:
            # 确保所有子线程都被清理
            for thread in threads:
                thread.quit()
                thread.wait()

def send_file(file_path, frame_rate, qr_count, data_chunk_size, gui_instance, width, height, thread_count):
    # 创建并启动文件处理线程
    process_thread = FileProcessThread(file_path, frame_rate, qr_count, data_chunk_size, width, height, thread_count)
    process_thread.progress_updated.connect(gui_instance.log_message)
    process_thread.qr_codes_ready.connect(gui_instance.on_qr_codes_ready)
    gui_instance.process_thread = process_thread  # 保存线程引用
    process_thread.start()
    return []

def read_chunk(formatted_chunk):
    # 读取序号 (4字节)
    index = int.from_bytes(formatted_chunk[:4], byteorder='big')
    # 读取数据长度 (2字节)
    data_length = int.from_bytes(formatted_chunk[4:6], byteorder='big')
    # 读取数据内容
    data_content = formatted_chunk[6:6 + data_length].decode()
    # 读取 CRC32 校验码 (4字节)
    crc32_checksum = int.from_bytes(formatted_chunk[6 + data_length:10 + data_length], byteorder='big')
    return index, data_length, data_content, crc32_checksum