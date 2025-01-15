# qr_recognizer.py
import cv2
import zlib
import base64
import numpy as np
from pyzbar.pyzbar import decode  # 需要安装: pip install pyzbar
from param_qr import parse_transfer_params

def recognize_qr_code(image):
    """识别图像中的所有二维码
    Args:
        image: numpy array 图像数据
    Returns:
        list: 包含所有识别出的二维码数据的列表
    """
    # 转换为灰度图
    if len(image.shape) > 2:
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray_image = image
        
    # 使用pyzbar识别多个二维码
    qr_codes = decode(gray_image)
    
    # 提取所有二维码的数据
    results = []
    for qr in qr_codes:
        if qr.type == 'QRCODE':  # 确保是二维码而不是其他类型的条码
            data = qr.data
            results.append(data)
            
    return results if results else None

def recognize_qr_code_for_reader_param(image): 
    # 转换为灰度图
    if len(image.shape) > 2:
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray_image = image
        
    # 使用pyzbar识别多个二维码
    qr_codes = decode(gray_image)
    
    # 提取所有二维码的数据
    results = []
    for qr in qr_codes:
        if qr.type == 'QRCODE':  # 确保是二维码而不是其他类型的条码
            return parse_transfer_params(qr.data) 
            
    return None


def parse_qr_data(data):
    """解析二维码数据
    Args:
        data: str 二维码数据
    Returns:
        tuple: (index, data_content, is_valid)
            - index: 数据序号
            - data_content: 数据内容
            - is_valid: CRC32校验是否通过
    """
    try:
        # 确保数据是bytes类型
        #formatted_chunk = data if isinstance(data, bytes) else data.encode('utf-8')
        formatted_chunk = base64.b64decode(data)
        # 解析数据格式
        index = int.from_bytes(formatted_chunk[:4], byteorder='big')
        data_length = int.from_bytes(formatted_chunk[4:6], byteorder='big')
        data_content = formatted_chunk[6:6 + data_length]  # 保持为bytes，不要decode
        crc32_checksum = int.from_bytes(formatted_chunk[6 + data_length:10 + data_length], byteorder='big')
        
        # 验证 CRC32 校验码
        calculated_crc32 = zlib.crc32(data_content)
        is_valid = (calculated_crc32 == crc32_checksum)
        
        return index, data_content, is_valid  # 返回原始bytes数据
        
    except Exception as e:
        raise ValueError(f"数据解析错误: {str(e)}")