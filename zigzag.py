import numpy as np

def zigzag_scan(matrix):
    """
    Perform zig-zag scan of a 2D matrix and return a 1D array.
    Args:
        matrix (np.ndarray): 2D input array.
    Returns:
        np.ndarray: 1D array in zig-zag order.
    """
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
    """
    Reconstruct a 2D matrix from a 1D zig-zag scanned array.
    Args:
        arr (np.ndarray): 1D zig-zag array.
        h (int): Height of the output matrix.
        w (int): Width of the output matrix.
    Returns:
        np.ndarray: 2D reconstructed array.
    """
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