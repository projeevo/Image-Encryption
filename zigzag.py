import numpy as np

def zigzag_scan(matrix):
    h, w = matrix.shape
    result = []
    for s in range(h + w - 1):
        if s % 2 == 0:
            for y in range(s, -1, -1):
                x = s - y
                if x < w and y < h:
                    result.append(matrix[y, x])
        else:
            for x in range(s, -1, -1):
                y = s - x
                if x < w and y < h:
                    result.append(matrix[y, x])
    return np.array(result)

def inverse_zigzag_scan(arr, h, w):
    matrix = np.zeros((h, w), dtype=arr.dtype)
    idx = 0
    for s in range(h + w - 1):
        if s % 2 == 0:
            for y in range(s, -1, -1):
                x = s - y
                if x < w and y < h:
                    matrix[y, x] = arr[idx]
                    idx += 1
        else:
            for x in range(s, -1, -1):
                y = s - x
                if x < w and y < h:
                    matrix[y, x] = arr[idx]
                    idx += 1
    return matrix 