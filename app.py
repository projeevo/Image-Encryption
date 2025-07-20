from flask import Flask, render_template, request, jsonify, send_file, session
import os
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from werkzeug.utils import secure_filename
import preprocessing
import roi_selector
import zigzag
import chaotic_map
import encryption as enc
import decryption as dec
import metrics as met
#learn
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'supersecretkey'  # Needed for session
 
# Helper to convert OpenCV image to base64
def cv2_to_base64(img):
    _, buffer = cv2.imencode('.png', img)
    return 'data:image/png;base64,' + base64.b64encode(buffer).decode('utf-8')

# Helper to convert base64 to OpenCV image
def base64_to_cv2(b64_string):
    """
    Decodes a base64 string (either raw or a data URL) into an OpenCV image.
    """
    try:
        # If it's a data URL, strip the header
        if 'data:image' in b64_string and ',' in b64_string:
            header, b64_string = b64_string.split(',', 1)

        img_bytes = base64.b64decode(b64_string)
        img_array = np.frombuffer(img_bytes, np.uint8)
        # Decode as a color image, which can then be converted to grayscale
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("cv2.imdecode returned None")
        return img
    except (ValueError, TypeError, base64.binascii.Error) as e:
        app.logger.error(f"Failed to decode base64 string: {e}")
        return None

# Helper to get an image from session
def get_image_from_session(session_key):
    if session_key not in session or not session[session_key]:
        return None
    img_bytes = base64.b64decode(session[session_key])
    return cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    data = request.get_json()
    img_b64 = data.get('image')
    if not img_b64:
        return jsonify({'status': 'error', 'message': 'No image provided'}), 400

    img = base64_to_cv2(img_b64)
    if img is None:
        return jsonify({'status': 'error', 'message': 'Invalid or corrupt image data'}), 400

    img = preprocessing.resize_image(img)
    img = preprocessing.to_grayscale(img)
    # Save to session (as bytes)
    _, buffer = cv2.imencode('.png', img)
    session['image'] = base64.b64encode(buffer).decode('utf-8')
    session['encrypted'] = None
    session['decrypted'] = None
    return jsonify({'status': 'success', 'message': 'Image uploaded'})

@app.route('/encrypt', methods=['POST'])
def handle_encrypt():
    data = request.get_json()
    roi = data.get('roi')
    img = get_image_from_session('image')
    if not roi or img is None:
        return jsonify({'status': 'error', 'message': 'No ROI or image'}), 400
    try:
        x = int(roi['x'])
        y = int(roi['y'])
        w = int(roi['w'])
        h = int(roi['h'])
    except (ValueError, TypeError, KeyError):
        return jsonify({'status': 'error', 'message': 'Invalid ROI coordinates'}), 400
    roi_img = roi_selector.extract_roi(img, x, y, w, h)
    flat = zigzag.zigzag_scan(roi_img)
    key = chaotic_map.logistic_sine_map(flat.size)
    encrypted_flat = enc.encrypt(flat, key)
    encrypted_roi = zigzag.inverse_zigzag_scan(encrypted_flat, h, w)
    encrypted_img = img.copy()
    encrypted_img[y:y+h, x:x+w] = encrypted_roi
    # Save encrypted for later decryption/metrics
    _, buffer = cv2.imencode('.png', encrypted_img)
    session['encrypted'] = base64.b64encode(buffer).decode('utf-8')
    session['roi'] = roi
    session['key'] = key.tolist()
    return jsonify({'status': 'success', 'encrypted_image': cv2_to_base64(encrypted_img)})

@app.route('/decrypt', methods=['POST'])
def handle_decrypt():
    encrypted_img = get_image_from_session('encrypted')
    roi = session.get('roi')
    key_list = session.get('key')
    if encrypted_img is None or not roi or not key_list:
        return jsonify({'status': 'error', 'message': 'No encrypted image or key'}), 400
    key = np.array(key_list, dtype=np.uint8)
    try:
        x = int(roi['x'])
        y = int(roi['y'])
        w = int(roi['w'])
        h = int(roi['h'])
    except (ValueError, TypeError, KeyError):
        return jsonify({'status': 'error', 'message': 'Invalid ROI coordinates from session'}), 400
    encrypted_roi = roi_selector.extract_roi(encrypted_img, x, y, w, h)
    flat = zigzag.zigzag_scan(encrypted_roi)
    decrypted_flat = dec.decrypt(flat, key)
    decrypted_roi = zigzag.inverse_zigzag_scan(decrypted_flat, h, w)
    decrypted_img = encrypted_img.copy()
    decrypted_img[y:y+h, x:x+w] = decrypted_roi
    # Save decrypted for metrics
    _, buffer = cv2.imencode('.png', decrypted_img)
    session['decrypted'] = base64.b64encode(buffer).decode('utf-8')
    return jsonify({'status': 'success', 'decrypted_image': cv2_to_base64(decrypted_img)})

@app.route('/metrics', methods=['POST'])
def handle_metrics():
    orig = get_image_from_session('image')
    enc_img = get_image_from_session('encrypted')
    dec_img = get_image_from_session('decrypted')
    if orig is None or enc_img is None or dec_img is None:
        return jsonify({'entropy': 0, 'psnr': 0})
    entropy_val = float(met.entropy(enc_img))
    psnr_val = float(met.psnr(orig, dec_img))
    return jsonify({'entropy': round(entropy_val, 4), 'psnr': round(psnr_val, 4)})

if __name__ == '__main__':
    app.run(debug=True) 