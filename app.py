from flask import Flask, render_template, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Placeholder: handle image upload
    return jsonify({'status': 'success', 'message': 'Image uploaded'})

@app.route('/encrypt', methods=['POST'])
def encrypt():
    # Placeholder: handle encryption
    return jsonify({'status': 'success', 'message': 'Image encrypted'})

@app.route('/decrypt', methods=['POST'])
def decrypt():
    # Placeholder: handle decryption
    return jsonify({'status': 'success', 'message': 'Image decrypted'})

@app.route('/metrics', methods=['POST'])
def metrics():
    # Placeholder: return metrics
    return jsonify({'entropy': 0, 'psnr': 0})

if __name__ == '__main__':
    app.run(debug=True) 