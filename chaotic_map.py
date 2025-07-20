import numpy as np

def logistic_sine_map(size, x0=0.7, y0=0.8, r=3.99):
    x = np.zeros(size)
    y = np.zeros(size)
    x[0] = x0
    y[0] = y0
    for i in range(1, size):
        x[i] = np.sin(r * y[i-1]) * x[i-1] * (1 - x[i-1])
        y[i] = np.sin(r * x[i-1]) * y[i-1] * (1 - y[i-1])
    # Normalize to 0-255
    key = np.mod(np.floor(x * 1e14), 256).astype(np.uint8)
    return key 