# qr_generator.py
import qrcode
from PIL import Image

def generate_qr_code(data, width, height):
    # 生成二维码
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img = img.resize((width,height), Image.Resampling.LANCZOS)
    return img