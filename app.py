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
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
app.secret_key = 'supersecretkey'  # Needed for session

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Helper to convert OpenCV image to base64
def cv2_to_base64(img):
    _, buffer = cv2.imencode('.png', img)
    return 'data:image/png;base64,' + base64.b64encode(buffer).decode('utf-8')

# Helper to convert base64 to OpenCV image
def base64_to_cv2(data):
    header, encoded = data.split(',', 1)
    img_bytes = base64.b64decode(encoded)
    img = Image.open(BytesIO(img_bytes)).convert('RGB')
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

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
    img = preprocessing.resize_image(img)
    img = preprocessing.to_grayscale(img)
    # Save to session (as bytes)
    _, buffer = cv2.imencode('.png', img)
    session['image'] = base64.b64encode(buffer).decode('utf-8')
    session['encrypted'] = None
    session['decrypted'] = None
    return jsonify({'status': 'success', 'message': 'Image uploaded'})

@app.route('/encrypt', methods=['POST'])
def encrypt():
    data = request.get_json()
    roi = data.get('roi')
    if not roi or 'image' not in session:
        return jsonify({'status': 'error', 'message': 'No ROI or image'}), 400
    img_bytes = base64.b64decode(session['image'])
    img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)
    x, y, w, h = roi['x'], roi['y'], roi['w'], roi['h']
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
def decrypt():
    if 'encrypted' not in session or 'roi' not in session or 'key' not in session or 'image' not in session:
        return jsonify({'status': 'error', 'message': 'No encrypted image or key'}), 400
    img_bytes = base64.b64decode(session['encrypted'])
    encrypted_img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)
    roi = session['roi']
    key = np.array(session['key'], dtype=np.uint8)
    x, y, w, h = roi['x'], roi['y'], roi['w'], roi['h']
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
def metrics():
    if 'image' not in session or 'encrypted' not in session or 'decrypted' not in session:
        return jsonify({'entropy': 0, 'psnr': 0})
    orig_bytes = base64.b64decode(session['image'])
    enc_bytes = base64.b64decode(session['encrypted'])
    dec_bytes = base64.b64decode(session['decrypted'])
    orig = cv2.imdecode(np.frombuffer(orig_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)
    enc_img = cv2.imdecode(np.frombuffer(enc_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)
    dec_img = cv2.imdecode(np.frombuffer(dec_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)
    entropy_val = float(met.entropy(enc_img))
    psnr_val = float(met.psnr(orig, dec_img))
    return jsonify({'entropy': round(entropy_val, 4), 'psnr': round(psnr_val, 4)})

if __name__ == '__main__':
    app.run(debug=True) 