import numpy as np

def extract_roi(img, x, y, w, h):
    return img[y:y+h, x:x+w] 