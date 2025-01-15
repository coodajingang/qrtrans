import json
import base64
from dataclasses import dataclass
from typing import List

@dataclass
class TransferParams:
    filename: str
    frame_rate: int
    qr_count: int
    total_chunks: int
    chunk_ranges: List[tuple]  # [(start1, end1), (start2, end2), ...]
    chunks_size: int

def format_transfer_params(filename: str, frame_rate: int, qr_count: int, 
                         total_chunks: int, chunk_ranges: List[tuple], chunks_size: int) -> str:
    """将传输参数格式化为JSON字符串并进行base64编码"""
    params = TransferParams(
        filename=filename,
        frame_rate=frame_rate,
        qr_count=qr_count,
        total_chunks=total_chunks,
        chunk_ranges=chunk_ranges,
        chunks_size=chunks_size
    )
    
    # 转换为dict并序列化为JSON
    param_dict = {
        "filename": params.filename,
        "frame_rate": params.frame_rate,
        "qr_count": params.qr_count,
        "total_chunks": params.total_chunks,
        "chunk_ranges": params.chunk_ranges,
        "chunks_size": params.chunks_size
    }
    
    json_str = json.dumps(param_dict, ensure_ascii=False)
    return base64.b64encode(json_str.encode('utf-8')).decode('utf-8')

def parse_transfer_params(encoded_str: str) -> TransferParams:
    """解析base64编码的参数字符串"""
    try:
        json_str = base64.b64decode(encoded_str).decode('utf-8')
        param_dict = json.loads(json_str)
        
        return TransferParams(
            filename=param_dict["filename"],
            frame_rate=param_dict["frame_rate"],
            qr_count=param_dict["qr_count"],
            total_chunks=param_dict["total_chunks"],
            chunk_ranges=param_dict["chunk_ranges"],
            chunks_size=param_dict["chunks_size"],
        )
    except Exception as e:
        raise ValueError(f"Invalid parameter QR code data: {str(e)}") 