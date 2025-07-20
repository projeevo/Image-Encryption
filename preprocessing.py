import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image

def read_image(path):
    img = cv2.imread(path)
    return img

def resize_image(img, size=(256, 256)):
    return cv2.resize(img, size)

def to_grayscale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def pil_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f'data:image/png;base64,{img_str}'

def base64_to_pil(b64_string, app_logger=None):
    try:
        if 'data:image' in b64_string and ',' in b64_string:
            header, b64_string = b64_string.split(',', 1)
        img_bytes = base64.b64decode(b64_string)
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        return img
    except Exception as e:
        if app_logger:
            app_logger.error(f"Failed to decode base64 string: {e}")
        return None 