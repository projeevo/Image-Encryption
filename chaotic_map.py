import numpy as np

def logistic_sine_map(size, x0=0.7, y0=0.8, r=3.99):
    """
    Generate a key sequence using the logistic-sine chaotic map.
    """
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

def logistic_2d_map(x, y, r1, r2, alpha, beta, size):
    """
    Generate two chaotic sequences using a 2D logistic map.
    """
    x_seq, y_seq = [], []
    for _ in range(size):
        x = r1 * x * (1 - x) + beta * y * y
        y = r2 * y * (1 - y) + alpha * x * x
        x = x % 1
        y = y % 1
        x_seq.append(x)
        y_seq.append(y)
    return np.array(x_seq), np.array(y_seq) 