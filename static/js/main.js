// Modern Image Encryption Interface JavaScript
document.addEventListener('DOMContentLoaded', () => {
    // Global state
    let currentTab = 'home';
    let uploadedImage = null;
    let encryptedData = null;
    let decryptedImage = null;

    // DOM Elements
    const navLinks = document.querySelectorAll('.nav-link');
    const tabContents = document.querySelectorAll('.tab-content');
    const statusMessage = document.getElementById('status-message');
    const loadingOverlay = document.getElementById('loading-overlay');

    // Encryption elements
    const uploadArea = document.getElementById('upload-area');
    const imageInput = document.getElementById('image-input');
    const encryptBtn = document.getElementById('encrypt-btn');
    const originalImage = document.getElementById('original-image');
    const encryptedImage = document.getElementById('encrypted-image');
    const downloadSection = document.getElementById('download-section');
    const downloadBtn = document.getElementById('download-btn');

    // Decryption elements
    const decryptUploadArea = document.getElementById('decrypt-upload-area');
    const zipInput = document.getElementById('zip-input');
    const decryptBtn = document.getElementById('decrypt-btn');
    const decryptEncryptedImage = document.getElementById('decrypt-encrypted-image');
    const decryptedImageElement = document.getElementById('decrypted-image');
    const decryptDownloadSection = document.getElementById('decrypt-download-section');
    const decryptDownloadBtn = document.getElementById('decrypt-download-btn');

    // Patient name input
    const patientNameInput = document.getElementById('patient-name');

    // Debug: Check if elements are found
    console.log('Decryption elements found:', {
        decryptUploadArea: !!decryptUploadArea,
        zipInput: !!zipInput,
        decryptBtn: !!decryptBtn,
        decryptEncryptedImage: !!decryptEncryptedImage,
        decryptedImageElement: !!decryptedImageElement,
        decryptDownloadSection: !!decryptDownloadSection,
        decryptDownloadBtn: !!decryptDownloadBtn
    });

    // Utility Functions
    function showStatus(message, type = 'info') {
        statusMessage.className = `status-message ${type}`;
        statusMessage.querySelector('.status-text').textContent = message;
        statusMessage.style.display = 'block';
        
        setTimeout(() => {
            statusMessage.style.display = 'none';
        }, 5000);
    }

    function showLoading(show = true) {
        loadingOverlay.style.display = show ? 'flex' : 'none';
    }

    function switchTab(tabName) {
        if (tabName.startsWith('#')) tabName = tabName.slice(1);
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.dataset.tab === tabName) {
                link.classList.add('active');
            }
        });
        const tabContents = document.querySelectorAll('.tab-content');
        tabContents.forEach(content => {
            content.classList.remove('active');
            if (content.id === tabName) {
                content.classList.add('active');
            }
        });
    }
    window.switchTab = switchTab;

    function downloadFile(data, filename, type = 'application/octet-stream') {
        const blob = new Blob([data], { type });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // Tab Navigation
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const tabName = link.dataset.tab;
            switchTab(tabName);
        });
    });

    // Encryption Tab Functionality
    function setupEncryptionTab() {
        // Drag and drop for image upload
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleImageUpload(files[0]);
            }
        });

        // Click to upload
        uploadArea.addEventListener('click', () => {
            imageInput.click();
        });

        imageInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleImageUpload(e.target.files[0]);
            }
        });

        // Encrypt button
        encryptBtn.addEventListener('click', handleEncryption);

        // Download button
        downloadBtn.addEventListener('click', () => {
            if (encryptedData) {
                const zipData = atob(encryptedData.zip_file);
                const zipArray = new Uint8Array(zipData.length);
                for (let i = 0; i < zipData.length; i++) {
                    zipArray[i] = zipData.charCodeAt(i);
                }
                const patientName = patientNameInput.value.trim() || 'encrypted';
                const filename = `${patientName}_encrypted_package.zip`;
                downloadFile(zipArray, filename);
            }
        });
    }

    function handleImageUpload(file) {
        if (!file.type.startsWith('image/')) {
            showStatus('Please select a valid image file.', 'error');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            uploadedImage = e.target.result;
            originalImage.src = uploadedImage;
            encryptBtn.disabled = false;
            showStatus('Image uploaded successfully! Click "Encrypt Image" to proceed.', 'success');
        };
        reader.readAsDataURL(file);
    }

    async function handleEncryption() {
        if (!uploadedImage) {
            showStatus('Please upload an image first.', 'error');
            return;
        }
        const patientName = patientNameInput.value.trim() || 'encrypted';
        showLoading(true);
        try {
            const response = await fetch('/encrypt', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: uploadedImage,
                    patient_name: patientName
                })
            });
            const result = await response.json();
            if (result.status === 'success') {
                encryptedData = result;
                encryptedImage.src = result.encrypted_image;
                downloadSection.style.display = 'block';
                showStatus(result.message, 'success');
            } else {
                showStatus(result.message, 'error');
            }
        } catch (error) {
            showStatus('Encryption failed. Please try again.', 'error');
            console.error('Encryption error:', error);
        } finally {
            showLoading(false);
        }
    }

    // Decryption Tab Functionality
    function setupDecryptionTab() {
        console.log('Setting up decryption tab...');
        
        // Drag and drop for ZIP upload (without animation)
        decryptUploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            // No visual feedback for decryption upload
        });

        decryptUploadArea.addEventListener('dragleave', (e) => {
            // No visual feedback for decryption upload
        });

        decryptUploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            console.log('File dropped:', e.dataTransfer.files);
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleZipUpload(files[0]);
            }
        });

        // Click to upload
        decryptUploadArea.addEventListener('click', () => {
            console.log('Upload area clicked');
            zipInput.click();
        });

        zipInput.addEventListener('change', (e) => {
            console.log('File input changed:', e.target.files);
            if (e.target.files.length > 0) {
                handleZipUpload(e.target.files[0]);
            }
        });

        // Decrypt button
        decryptBtn.addEventListener('click', handleDecryption);

        // Download decrypted image
        decryptDownloadBtn.addEventListener('click', () => {
            if (decryptedImage) {
                const link = document.createElement('a');
                link.href = decryptedImage;
                link.download = 'decrypted_image.png';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
        });
        
        console.log('Decryption tab setup complete');
    }

    function handleZipUpload(file) {
        if (!file.name.endsWith('.zip')) {
            showStatus('Please select a valid ZIP file.', 'error');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                // Convert ArrayBuffer to base64 more reliably
                const arrayBuffer = e.target.result;
                const uint8Array = new Uint8Array(arrayBuffer);
                let binaryString = '';
                for (let i = 0; i < uint8Array.length; i++) {
                    binaryString += String.fromCharCode(uint8Array[i]);
                }
                const base64 = btoa(binaryString);
                
                encryptedData = { zip_file: base64 };
                decryptBtn.disabled = false;
                showStatus('ZIP file uploaded successfully! Click "Decrypt Image" to proceed.', 'success');
                
                // Debug log
                console.log('ZIP file uploaded:', file.name, 'Size:', file.size, 'Base64 length:', base64.length);
            } catch (error) {
                console.error('Error processing ZIP file:', error);
                showStatus('Error processing ZIP file. Please try again.', 'error');
            }
        };
        
        reader.onerror = () => {
            showStatus('Error reading ZIP file. Please try again.', 'error');
        };
        
        reader.readAsArrayBuffer(file);
    }

    async function handleDecryption() {
        if (!encryptedData) {
            showStatus('Please upload a ZIP file first.', 'error');
            return;
        }

        showLoading(true);
        try {
            console.log('Sending decryption request...');
            const response = await fetch('/decrypt', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    zip_file: encryptedData.zip_file
                })
            });

            console.log('Response status:', response.status);
            const result = await response.json();
            console.log('Decryption result:', result);

            if (result.status === 'success') {
                decryptedImage = result.decrypted_image;
                // Show both encrypted and decrypted images
                decryptEncryptedImage.src = result.encrypted_image;
                decryptEncryptedImage.style.display = 'block';
                decryptedImageElement.src = result.decrypted_image;
                decryptedImageElement.style.display = 'block';
                decryptDownloadSection.style.display = 'block';
                showStatus(result.message, 'success');
            } else {
                showStatus(result.message, 'error');
            }
        } catch (error) {
            showStatus('Decryption failed. Please try again.', 'error');
            console.error('Decryption error:', error);
        } finally {
            showLoading(false);
        }
    }

    // Initialize tabs
    function initTabs() {
        setupEncryptionTab();
        setupDecryptionTab();
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case '1':
                    e.preventDefault();
                    switchTab('home');
                    break;
                case '2':
                    e.preventDefault();
                    switchTab('encrypt');
                    break;
                case '3':
                    e.preventDefault();
                    switchTab('decrypt');
                    break;
                case '4':
                    e.preventDefault();
                    switchTab('how-it-works');
                    break;
            }
        }
    });

    // Initialize the application
    initTabs();

    // Removed cursor-following animations for better user experience

    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading animations for images
    function addImageLoadingAnimation() {
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            img.addEventListener('load', () => {
                img.style.opacity = '0';
                img.style.transform = 'scale(0.8)';
                setTimeout(() => {
                    img.style.transition = 'all 0.3s ease';
                    img.style.opacity = '1';
                    img.style.transform = 'scale(1)';
                }, 100);
            });
        });
    }

    addImageLoadingAnimation();

    // Add particle effect for hero section
    function createParticles() {
        const heroSection = document.querySelector('.hero-section');
        if (!heroSection) return;

        for (let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.cssText = `
                position: absolute;
                width: 2px;
                height: 2px;
                background: var(--primary-color);
                border-radius: 50%;
                opacity: 0.3;
                pointer-events: none;
                animation: float ${3 + Math.random() * 4}s infinite ease-in-out;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
            `;
            heroSection.appendChild(particle);
        }
    }

    // Add CSS for particles
    const style = document.createElement('style');
    style.textContent = `
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 0.3; }
            50% { transform: translateY(-20px) rotate(180deg); opacity: 0.6; }
        }
        
        .hero-section {
            position: relative;
            overflow: hidden;
        }
        
        .particle {
            z-index: 1;
        }
    `;
    document.head.appendChild(style);

    // Initialize particles
    createParticles();

    console.log('ImageCrypt Interface initialized successfully! 🚀');
});