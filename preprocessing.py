import cv2
import numpy as np

def read_image(path):
    img = cv2.imread(path)
    return img

def resize_image(img, size=(256, 256)):
    return cv2.resize(img, size)

def to_grayscale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 