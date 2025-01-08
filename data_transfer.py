# data_transfer.py
from file_handler import compress_file, split_data
from qr_generator import generate_qr_code
import zlib
from PyQt6.QtGui import QPixmap
from PIL.ImageQt import ImageQt

def send_file(file_path, frame_rate, qr_count, data_chunk_size, gui_instance, width, height):
    compressed_data = compress_file(file_path)
    chunks = split_data(compressed_data, data_chunk_size)
    gui_instance.log_message(f"文件压缩后大小 {len(compressed_data)} 分段大小={data_chunk_size} 分段数={len(chunks)}")  # 记录日志
    qr_codes = []
    for index, c in enumerate(chunks): 
        #gui_instance.log_message(f"处理分段 {index}  数据长度={len(c)}")
        # 计算数据长度和 CRC32 校验码
        data_length = len(c)
        crc32_checksum = zlib.crc32(c)  # 直接使用c计算 CRC32 校验码
        # 构建新的数据格式
        formatted_chunk = (
            index.to_bytes(4, byteorder='big') +  # 序号 (4字节)
            data_length.to_bytes(2, byteorder='big') +  # 数据长度 (2字节)
            c +  # 数据内容
            crc32_checksum.to_bytes(4, byteorder='big')  # CRC32 校验码 (4字节)
        )
        qr_codes.append(QPixmap.fromImage(ImageQt(generate_qr_code(formatted_chunk,width, height))))

    gui_instance.log_message(f"生成了 {len(qr_codes)} 个二维码。")  # 记录日志
    return qr_codes

def read_chunk(formatted_chunk):
    # 读取序号 (4字节)
    index = int.from_bytes(formatted_chunk[:4], byteorder='big')
    # 读取数据长度 (2字节)
    data_length = int.from_bytes(formatted_chunk[4:6], byteorder='big')
    # 读取数据内容
    data_content = formatted_chunk[6:6 + data_length].decode()  # 解码为字符串
    # 读取 CRC32 校验码 (4字节)
    crc32_checksum = int.from_bytes(formatted_chunk[6 + data_length:10 + data_length], byteorder='big')
    return index, data_length, data_content, crc32_checksum

    # # 计算每个二维码的数据范围
    # chunk_size = len(chunks) // qr_count
    # qr_code_groups = []  # 存储二维码分组
    # for index in range(qr_count):
    #     start_index = index * chunk_size
    #     end_index = start_index + chunk_size if index < qr_count - 1 else len(chunks)
    #     qr_chunks = chunks[start_index:end_index]

    #     # 生成二维码
    #     qr_codes = []
    #     for chunk in qr_chunks:
    #         qr_code = generate_qr_code(chunk)
    #         qr_codes.append(qr_code)  # 保存二维码图像

    #     # 将二维码分组和起始结束索引一起存储
    #     qr_code_groups.append((qr_codes, start_index, end_index))  # 存储二维码和索引

    # return qr_code_groups  # 返回二维码分组