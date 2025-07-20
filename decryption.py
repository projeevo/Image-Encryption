import numpy as np

def decrypt(data, key):
    return np.bitwise_xor(data, key) 