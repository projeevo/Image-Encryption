import numpy as np
import zigzag

def decrypt_channel(encrypted, indices, mask, original_shape, app_logger=None):
    if app_logger:
        app_logger.info(f"decrypt_channel - original_shape: {original_shape} (type: {type(original_shape)})")
        if hasattr(original_shape, '__len__'):
            app_logger.info(f"decrypt_channel - original_shape length: {len(original_shape)}")
        else:
            app_logger.info(f"decrypt_channel - original_shape is not a sequence")
    # Step 1: Apply inverse 2D logistic map decryption
    flat_enc = encrypted.flatten()
    diffused = np.bitwise_xor(flat_enc, mask)
    rev_indices = np.zeros_like(indices)
    rev_indices[indices] = np.arange(len(indices))
    decrypted_flat = diffused[rev_indices]
    # Step 2: Apply inverse zig-zag scanning to restore spatial arrangement
    try:
        h, w = original_shape
        if app_logger:
            app_logger.info(f"decrypt_channel - Successfully unpacked: h={h}, w={w}")
    except ValueError as e:
        if app_logger:
            app_logger.error(f"decrypt_channel - Failed to unpack original_shape: {e}")
            app_logger.error(f"decrypt_channel - original_shape value: {original_shape}")
        raise
    original = zigzag.inverse_zigzag_scan(decrypted_flat, h, w)
    return original

def decrypt_image_rgb(encrypted_img, indices, masks, shape, original_shapes, app_logger=None):
    r_enc, g_enc, b_enc = encrypted_img.transpose(2, 0, 1)
    r_dec = decrypt_channel(r_enc, indices[0], masks[0], original_shapes[0], app_logger)
    g_dec = decrypt_channel(g_enc, indices[1], masks[1], original_shapes[1], app_logger)
    b_dec = decrypt_channel(b_enc, indices[2], masks[2], original_shapes[2], app_logger)
    decrypted_img = np.stack([r_dec, g_dec, b_dec], axis=2)
    return decrypted_img 