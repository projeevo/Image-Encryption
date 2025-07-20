from flask import Flask, render_template, request, jsonify, send_file, session
import os
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from werkzeug.utils import secure_filename
import zipfile
import io
import zigzag

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'supersecretkey'  # Needed for session

# 2D Logistic Map Function
def logistic_2d_map(x, y, r1, r2, alpha, beta, size):
    x_seq, y_seq = [], []
    for _ in range(size):
        x = r1 * x * (1 - x) + beta * y * y
        y = r2 * y * (1 - y) + alpha * x * x
        x = x % 1
        y = y % 1
        x_seq.append(x)
        y_seq.append(y)
    return np.array(x_seq), np.array(y_seq)

# Encrypt one channel with zig-zag scanning
def encrypt_channel(channel_data, key_params):
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
    app.logger.info(f"encrypt_channel - original_shape: {original_shape} (type: {type(original_shape)})")
    
    return encrypted, indices, mask, original_shape

# Encrypt RGB Image with zig-zag scanning
def encrypt_image_rgb(image, key_params):
    r, g, b = np.array(image).transpose(2, 0, 1)
    r_enc, r_idx, r_mask, r_original_shape = encrypt_channel(r, key_params)
    g_enc, g_idx, g_mask, g_original_shape = encrypt_channel(g, key_params)
    b_enc, b_idx, b_mask, b_original_shape = encrypt_channel(b, key_params)
    encrypted_img = np.stack([r_enc, g_enc, b_enc], axis=2)
    return encrypted_img, (r_idx, g_idx, b_idx), (r_mask, g_mask, b_mask), r.shape, (r_original_shape, g_original_shape, b_original_shape)

# Decrypt one channel with zig-zag scanning
def decrypt_channel(encrypted, indices, mask, original_shape):
    # Debug: Log the original_shape parameter
    app.logger.info(f"decrypt_channel - original_shape: {original_shape} (type: {type(original_shape)})")
    if hasattr(original_shape, '__len__'):
        app.logger.info(f"decrypt_channel - original_shape length: {len(original_shape)}")
    else:
        app.logger.info(f"decrypt_channel - original_shape is not a sequence")
    
    # Step 1: Apply inverse 2D logistic map decryption
    flat_enc = encrypted.flatten()
    diffused = np.bitwise_xor(flat_enc, mask)
    rev_indices = np.zeros_like(indices)
    rev_indices[indices] = np.arange(len(indices))
    decrypted_flat = diffused[rev_indices]
    
    # Step 2: Apply inverse zig-zag scanning to restore spatial arrangement
    # original_shape is a tuple (height, width), so we need to unpack it
    try:
        h, w = original_shape
        app.logger.info(f"decrypt_channel - Successfully unpacked: h={h}, w={w}")
    except ValueError as e:
        app.logger.error(f"decrypt_channel - Failed to unpack original_shape: {e}")
        app.logger.error(f"decrypt_channel - original_shape value: {original_shape}")
        raise
    
    original = zigzag.inverse_zigzag_scan(decrypted_flat, h, w)
    
    return original

# Decrypt full RGB image with zig-zag scanning
def decrypt_image_rgb(encrypted_img, indices, masks, shape, original_shapes):
    r_enc, g_enc, b_enc = encrypted_img.transpose(2, 0, 1)
    r_dec = decrypt_channel(r_enc, indices[0], masks[0], original_shapes[0])
    g_dec = decrypt_channel(g_enc, indices[1], masks[1], original_shapes[1])
    b_dec = decrypt_channel(b_enc, indices[2], masks[2], original_shapes[2])
    decrypted_img = np.stack([r_dec, g_dec, b_dec], axis=2)
    return decrypted_img

# Helper to convert PIL image to base64
def pil_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f'data:image/png;base64,{img_str}'

# Helper to convert base64 to PIL image
def base64_to_pil(b64_string):
    try:
        if 'data:image' in b64_string and ',' in b64_string:
            header, b64_string = b64_string.split(',', 1)
        
        img_bytes = base64.b64decode(b64_string)
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        return img
    except Exception as e:
        app.logger.error(f"Failed to decode base64 string: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def handle_encrypt():
    try:
        data = request.get_json()
        img_b64 = data.get('image')
        patient_name = data.get('patient_name', 'encrypted')
        if not img_b64:
            return jsonify({'status': 'error', 'message': 'No image provided'}), 400

        # Convert base64 to PIL image
        image = base64_to_pil(img_b64)
        if image is None:
            return jsonify({'status': 'error', 'message': 'Invalid image data'}), 400

        # Key parameters for 2D logistic map
        key_params = (0.2, 0.3, 3.99, 3.98, 0.5, 0.3)

        # Encrypt the image with zig-zag scanning
        encrypted_img, indices, masks, shape, zigzag_shapes = encrypt_image_rgb(image, key_params)
        
        # Debug: Log original shapes during encryption
        app.logger.info(f"Encryption - original_shapes: {zigzag_shapes}")
        app.logger.info(f"Encryption - original_shapes types: {[type(s) for s in zigzag_shapes]}")
        app.logger.info(f"Encryption - original_shapes lengths: {[len(s) if hasattr(s, '__len__') else 'N/A' for s in zigzag_shapes]}")
        
        # Convert to PIL and then to base64
        encrypted_pil = Image.fromarray(encrypted_img.astype(np.uint8))
        encrypted_b64 = pil_to_base64(encrypted_pil)

        # Create zip file in memory
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
            # Save encrypted image
            img_bytes = BytesIO()
            encrypted_pil.save(img_bytes, format='PNG')
            zipf.writestr('encrypted_image.png', img_bytes.getvalue())
            
            # Save keys as numpy array
            keys_bytes = BytesIO()
            np.savez(keys_bytes, 
                     r_idx=indices[0], g_idx=indices[1], b_idx=indices[2],
                     r_mask=masks[0], g_mask=masks[1], b_mask=masks[2],
                     shape=shape,
                     r_original_shape=zigzag_shapes[0], g_original_shape=zigzag_shapes[1], b_original_shape=zigzag_shapes[2])
            zipf.writestr('encryption_keys.npz', keys_bytes.getvalue())

        # Convert zip to base64
        zip_buffer.seek(0)
        zip_b64 = base64.b64encode(zip_buffer.getvalue()).decode()

        return jsonify({
            'status': 'success', 
            'encrypted_image': encrypted_b64,
            'zip_file': zip_b64,
            'zip_filename': f'{patient_name}_encrypted_package.zip',
            'message': 'Image encrypted successfully! Download the zip file for decryption.'
        })

    except Exception as e:
        app.logger.error(f"Encryption error: {e}")
        return jsonify({'status': 'error', 'message': f'Encryption failed: {str(e)}'}), 500

@app.route('/decrypt', methods=['POST'])
def handle_decrypt():
    try:
        data = request.get_json()
        zip_b64 = data.get('zip_file')
        if not zip_b64:
            return jsonify({'status': 'error', 'message': 'No zip file provided'}), 400

        # Decode zip file
        zip_data = base64.b64decode(zip_b64)
        zip_buffer = BytesIO(zip_data)

        # Extract contents from the zip
        with zipfile.ZipFile(zip_buffer, 'r') as zipf:
            # Load encrypted image
            with zipf.open('encrypted_image.png') as img_file:
                encrypted_img = Image.open(img_file).convert("RGB")
                encrypted_img = np.array(encrypted_img)
            
            # Load keys
            with zipf.open('encryption_keys.npz') as key_file:
                keys = np.load(key_file)
                r_idx = keys['r_idx']
                g_idx = keys['g_idx']
                b_idx = keys['b_idx']
                r_mask = keys['r_mask']
                g_mask = keys['g_mask']
                b_mask = keys['b_mask']
                shape = tuple(keys['shape'])
                # Debug: Check what numpy.load returns for original shapes
                app.logger.info(f"Raw r_original_shape from npz: {keys['r_original_shape']} (type: {type(keys['r_original_shape'])}, shape: {keys['r_original_shape'].shape if hasattr(keys['r_original_shape'], 'shape') else 'N/A'})")
                app.logger.info(f"Raw g_original_shape from npz: {keys['g_original_shape']} (type: {type(keys['g_original_shape'])}, shape: {keys['g_original_shape'].shape if hasattr(keys['g_original_shape'], 'shape') else 'N/A'})")
                app.logger.info(f"Raw b_original_shape from npz: {keys['b_original_shape']} (type: {type(keys['b_original_shape'])}, shape: {keys['b_original_shape'].shape if hasattr(keys['b_original_shape'], 'shape') else 'N/A'})")

                r_original_shape = tuple(keys['r_original_shape'])
                g_original_shape = tuple(keys['g_original_shape'])
                b_original_shape = tuple(keys['b_original_shape'])

                app.logger.info(f"Converted r_original_shape: {r_original_shape} (type: {type(r_original_shape)}, len: {len(r_original_shape)})")
                app.logger.info(f"Converted g_original_shape: {g_original_shape} (type: {type(g_original_shape)}, len: {len(g_original_shape)})")
                app.logger.info(f"Converted b_original_shape: {b_original_shape} (type: {type(b_original_shape)}, len: {len(b_original_shape)})")

        # Debug: Print original shapes
        app.logger.info(f"Original shapes - R: {r_original_shape}, G: {g_original_shape}, B: {b_original_shape}")
        app.logger.info(f"Image shape: {shape}")
        
        # Convert encrypted image to base64 for display
        encrypted_pil = Image.fromarray(encrypted_img.astype(np.uint8))
        encrypted_b64 = pil_to_base64(encrypted_pil)

        # Decrypt the image with zig-zag scanning
        decrypted_img = decrypt_image_rgb(encrypted_img,
                                        (r_idx, g_idx, b_idx),
                                        (r_mask, g_mask, b_mask),
                                        shape,
                                        (r_original_shape, g_original_shape, b_original_shape))

        # Convert to PIL and then to base64
        decrypted_pil = Image.fromarray(decrypted_img.astype(np.uint8))
        decrypted_b64 = pil_to_base64(decrypted_pil)

        return jsonify({
            'status': 'success', 
            'encrypted_image': encrypted_b64,  # Add encrypted image to response
            'decrypted_image': decrypted_b64,
            'message': 'Image decrypted successfully!'
        })

    except Exception as e:
        app.logger.error(f"Decryption error: {e}")
        import traceback
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'status': 'error', 'message': f'Decryption failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True) 