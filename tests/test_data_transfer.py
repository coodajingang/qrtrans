import unittest
import base64
import os
import sys
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_transfer import send_file, read_chunk
from qr_generator import generate_qr_code
from PyQt6.QtGui import QPixmap
from PIL.ImageQt import ImageQt
from io import BytesIO
import zlib
from pyzbar.pyzbar import decode 

class MockGui:
    def log_message(self, message):
        print(message)

class TestDataTransfer(unittest.TestCase):
    def setUp(self):
        self.gui_instance = MockGui()
        self.width = 200
        self.height = 200
        self.frame_rate = 30
        self.qr_count = 1
        self.data_chunk_size = 1024

    def test_data_transfer(self):
        # Step 1: Generate random binary data
        #random_data = os.urandom(200)  # Generate 2048 bytes of random data
        #random_data = b'this ai asd iasdfka q2341 4 2 345 234jaksdkf'
        random_data = os.urandom(200)
        data = self.gen_data(random_data)

        img = generate_qr_code(data, 400, 400)

        img.save("test.png")

        res = decode(img)
        print("recognizer: ", res)

        rec_data = res[0].data
        print("rec base64 data:", rec_data.decode('ascii'))
        formatted_chunk = base64.b64decode(rec_data)

        index = int.from_bytes(formatted_chunk[:4], byteorder='big')
        data_length = int.from_bytes(formatted_chunk[4:6], byteorder='big')
        
        #crc32_checksum = int.from_bytes(formatted_chunk[6: 10], byteorder='big')
        data_content = formatted_chunk[6:6 + data_length]  # 保持为bytes，不要decode
        crc32_checksum = int.from_bytes(formatted_chunk[6 + data_length:10 + data_length], byteorder='big')
        
        # 验证 CRC32 校验码
        calculated_crc32 = zlib.crc32(data_content)
        is_valid = (calculated_crc32 == crc32_checksum)

        print(f"rec all data length: {len(formatted_chunk)}")
        print(f"rec index: {index}")
        print(f"rec data_length: {data_length}")
        print(f"rec data content length: {len(data_content)}")
        print(f"rec data crc32: {crc32_checksum} , calculated_crc32={calculated_crc32}, isvalid={is_valid}")
        self.print_base64("rec content", data_content)
        self.print_base64("rec all", formatted_chunk)
        

        #AAAAAwAsdGhpcyBhaSBhc2QgaWFzZGZrYSBxMjM0MSA0IDIgMzQ1IDIzNGpha3Nka2Z4iXCy 
        #AAAAAwAsdGhpcyBhaSBhc2QgaWFzZGZrYSBxMjM0MSA0IDIgMzQ1IDIzNGpha3Nka2Z46Iux772y
        


    def gen_data(self, c): 
        index = 3
        data_length = len(c)
        crc32_checksum = zlib.crc32(c)  # 直接使用c计算 CRC32 校验码
        # 构建新的数据格式
        formatted_chunk = (
            index.to_bytes(4, byteorder='big') +  # 序号 (4字节)
            data_length.to_bytes(2, byteorder='big') +  # 数据长度 (2字节)
            c +  # 数据内容
            crc32_checksum.to_bytes(4, byteorder='big')  # CRC32 校验码 (4字节)
        )
        print(f"origin data length: {data_length}")
        print(f"origin data formatted length: {len(formatted_chunk)}")
        self.print_base64("origin data", c)
        self.print_base64("origin crc32", crc32_checksum)
        self.print_base64("origin formatted_chunk", formatted_chunk)
        return base64.b64encode(formatted_chunk).decode('utf-8') 
    def print_base64(self, desc, c): 
        if (isinstance(c, bytes)): 
            s = base64.b64encode(c).decode('utf-8') 
            print(f"Base64of {desc}: {s}") 
        else: 
            print(f"type is {type(c)}:{c}")
if __name__ == '__main__':
    unittest.main() 