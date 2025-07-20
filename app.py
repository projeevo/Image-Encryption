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
from encryption import encrypt_image_rgb
from decryption import decrypt_image_rgb
from preprocessing import pil_to_base64, base64_to_pil

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'supersecretkey'  # Needed for session

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
        image = base64_to_pil(img_b64, app_logger=app.logger)
        if image is None:
            return jsonify({'status': 'error', 'message': 'Invalid image data'}), 400
        # Key parameters for 2D logistic map
        key_params = (0.2, 0.3, 3.99, 3.98, 0.5, 0.3)
        # Encrypt the image with zig-zag scanning
        encrypted_img, indices, masks, shape, zigzag_shapes = encrypt_image_rgb(image, key_params, app_logger=app.logger)
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
                encrypted_pil = Image.open(img_file).convert('RGB')
                encrypted_img = np.array(encrypted_pil)
            # Load keys
            with zipf.open('encryption_keys.npz') as key_file:
                keys = np.load(key_file)
                indices = (keys['r_idx'], keys['g_idx'], keys['b_idx'])
                masks = (keys['r_mask'], keys['g_mask'], keys['b_mask'])
                shape = tuple(keys['shape'])
                original_shapes = (tuple(keys['r_original_shape']), tuple(keys['g_original_shape']), tuple(keys['b_original_shape']))
        # Decrypt the image
        decrypted_img = decrypt_image_rgb(encrypted_img, indices, masks, shape, original_shapes, app_logger=app.logger)
        decrypted_pil = Image.fromarray(decrypted_img.astype(np.uint8))
        decrypted_b64 = pil_to_base64(decrypted_pil)
        return jsonify({
            'status': 'success',
            'decrypted_image': decrypted_b64,
            'encrypted_image': pil_to_base64(Image.fromarray(encrypted_img.astype(np.uint8))),
            'message': 'Image decrypted successfully!'
        })
    except Exception as e:
        app.logger.error(f"Decryption error: {e}")
        return jsonify({'status': 'error', 'message': f'Decryption failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True) 