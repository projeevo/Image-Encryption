import numpy as np
import zigzag
from chaotic_map import logistic_2d_map

# Encrypt one channel with zig-zag scanning
def encrypt_channel(channel_data, key_params, app_logger=None):
    x0, y0, r1, r2, alpha, beta = key_params
    # Step 1: Apply zig-zag scanning to scramble spatial arrangement
    zigzag_sequence = zigzag.zigzag_scan(channel_data)
    # Step 2: Apply 2D logistic map encryption
    size = zigzag_sequence.size
    x_seq, y_seq = logistic_2d_map(x0, y0, r1, r2, alpha, beta, size)
    indices = np.argsort(x_seq)
    permuted = zigzag_sequence[indices]
    mask = np.array((y_seq * 256), dtype=np.uint8)
    encrypted_flat = np.bitwise_xor(permuted, mask)
    # Step 3: Reshape back to original dimensions
    encrypted = encrypted_flat.reshape(channel_data.shape)
    # Store the original channel dimensions for zigzag reconstruction
    original_shape = channel_data.shape  # This is (height, width)
    if app_logger:
        app_logger.info(f"encrypt_channel - original_shape: {original_shape} (type: {type(original_shape)})")
    return encrypted, indices, mask, original_shape

# Encrypt RGB Image with zig-zag scanning
def encrypt_image_rgb(image, key_params, app_logger=None):
    r, g, b = np.array(image).transpose(2, 0, 1)
    r_enc, r_idx, r_mask, r_original_shape = encrypt_channel(r, key_params, app_logger)
    g_enc, g_idx, g_mask, g_original_shape = encrypt_channel(g, key_params, app_logger)
    b_enc, b_idx, b_mask, b_original_shape = encrypt_channel(b, key_params, app_logger)
    encrypted_img = np.stack([r_enc, g_enc, b_enc], axis=2)
    return encrypted_img, (r_idx, g_idx, b_idx), (r_mask, g_mask, b_mask), r.shape, (r_original_shape, g_original_shape, b_original_shape) 