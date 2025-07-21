# ImageCrypt - Advanced 2D Logistic Map Image Encryption

A modern web-based image encryption system using advanced 2D Logistic Map cryptography with a beautiful, user-friendly interface.

## 🚀 Features

- **Advanced Encryption**: Uses 2D Logistic Map algorithm for military-grade security
- **Modern Interface**: Beautiful, responsive web interface with drag-and-drop functionality
- **Dual Mode**: Separate encryption and decryption workflows
- **Secure Packaging**: Encrypted images and keys are packaged in secure ZIP files
- **Cross-Platform**: Works on any modern web browser
- **Real-time Processing**: Fast encryption and decryption with visual feedback

## 🔐 How It Works

### 2D Logistic Map Algorithm

The system uses a sophisticated 2D Logistic Map, which is a chaotic system that provides excellent security properties:

1. **Chaotic Sequence Generation**: 
   - x<sub>n+1</sub> = r₁ × x<sub>n</sub> × (1 - x<sub>n</sub>) + β × y<sub>n</sub>²
   - y<sub>n+1</sub> = r₂ × y<sub>n</sub> × (1 - y<sub>n</sub>) + α × x<sub>n</sub>²

2. **Pixel Permutation**: The chaotic x-sequence creates a permutation of pixel positions

3. **Pixel Diffusion**: The chaotic y-sequence generates a mask for XOR diffusion

4. **RGB Channel Processing**: Each color channel is processed independently

### Security Features

- **High Entropy**: Chaotic maps ensure maximum randomness
- **Key Sensitivity**: Tiny parameter changes produce completely different results
- **Visual Security**: Encrypted images appear as random noise
- **Perfect Recovery**: Original images are restored exactly without loss

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd Image-Encryption
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 🎯 How to Use

### Encryption Process

1. **Navigate to Encryption Tab**
   - Click the "Encrypt" tab in the navigation

2. **Upload Your Image**
   - Drag and drop an image file or click to browse
   - Supported formats: JPG, PNG, GIF, BMP

3. **Encrypt the Image**
   - Click "Encrypt Image" button
   - Wait for processing to complete

4. **Download the Package**
   - Click "Download ZIP File" to save the encrypted package
   - This contains your encrypted image and decryption keys

### Decryption Process

1. **Navigate to Decryption Tab**
   - Click the "Decrypt" tab in the navigation

2. **Upload the ZIP File**
   - Drag and drop the `encrypted_package.zip` file or click to browse

3. **Decrypt the Image**
   - Click "Decrypt Image" button
   - Wait for processing to complete

4. **Download the Result**
   - Click "Download Image" to save your restored original image

## 🏗️ Project Structure

```
Image-Encryption/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── static/
│   ├── css/
│   │   └── style.css     # Modern styling
│   └── js/
│       └── main.js       # Interactive functionality
└── templates/
    └── index.html        # Main interface
```

## 🔧 Technical Details

### Backend (Python/Flask)
- **Framework**: Flask web framework
- **Image Processing**: PIL (Pillow) for image manipulation
- **Cryptography**: Custom 2D Logistic Map implementation
- **Data Handling**: NumPy for efficient array operations

### Frontend (HTML/CSS/JavaScript)
- **Design**: Modern, responsive interface
- **Interactions**: Drag-and-drop file uploads
- **Animations**: Smooth transitions and loading states
- **Compatibility**: Works on all modern browsers

### Security Features
- **Algorithm**: 2D Logistic Map with XOR diffusion
- **Key Parameters**: x₀, y₀, r₁, r₂, α, β
- **File Format**: PNG with embedded keys
- **Processing**: Real-time encryption/decryption

## 🎨 Interface Features

### Home Tab
- Welcome screen with feature overview
- Quick access to encryption and decryption
- Visual demonstration of the process

### Encryption Tab
- Drag-and-drop image upload
- Real-time image preview
- Side-by-side comparison (original vs encrypted)
- Secure ZIP file download

### Decryption Tab
- Drag-and-drop ZIP file upload
- Real-time image preview
- Side-by-side comparison (encrypted vs decrypted)
- Restored image download

### How It Works Tab
- Detailed algorithm explanation
- Security features overview
- Technical specifications
- Mathematical formulas

## 🚨 Security Notes

- **Keep ZIP files secure**: The encrypted package contains all necessary keys
- **Share carefully**: Only share encrypted packages with intended recipients
- **Backup originals**: Always keep backups of your original images
- **No server storage**: Images are processed in memory and not stored on the server

## 🐛 Troubleshooting

### Common Issues

1. **"No image provided" error**
   - Ensure you're uploading a valid image file (JPG, PNG, GIF, BMP)

2. **"Invalid ZIP file" error**
   - Make sure you're uploading the correct `encrypted_package.zip` file
   - Don't modify the ZIP file contents

3. **Slow processing**
   - Large images may take longer to process
   - Ensure you have sufficient RAM available

4. **Browser compatibility**
   - Use modern browsers (Chrome, Firefox, Safari, Edge)
   - Enable JavaScript in your browser

### Performance Tips

- **Image size**: Smaller images process faster
- **Browser**: Use the latest version of your browser
- **System resources**: Close other applications for better performance



## 🙏 Acknowledgments

- Built with modern web technologies
- Inspired by advanced cryptographic research
- Designed for user privacy and security

---

**Note**: This is a demonstration project. For production use, consider additional security measures and professional cryptographic review. 
