import numpy as np

def encrypt(data, key):
    return np.bitwise_xor(data, key) 