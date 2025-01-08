# file_handler.py
import zlib

def compress_file(file_path):
    # 压缩文件
    with open(file_path, 'rb') as f:
        data = f.read()
        print(f"read size ={len(data)}")
    compressed_data = zlib.compress(data)
    return compressed_data

def decompress_data(compressed_data, output_file_path):
    """
    解压数据并写入文件
    Args:
        compressed_data: 压缩后的数据
        output_file_path: 输出文件路径
    Returns:
        int: 解压后数据的长度
    Raises:
        zlib.error: 解压缩错误
        IOError: 文件写入错误
    """
    # 解压数据
    decompressed_data = zlib.decompress(compressed_data)
    
    # 写入文件
    with open(output_file_path, 'wb') as f:
        f.write(decompressed_data)
        print(f"Decompressed data written to {output_file_path}, size={len(decompressed_data)}")
    
    return len(decompressed_data)

def split_data(data, chunk_size=800):
    # 分片数据
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]