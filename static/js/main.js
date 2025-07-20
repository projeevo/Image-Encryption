document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const imageLoader = document.getElementById('image-loader');
    const imageCanvas = document.getElementById('image-canvas');
    const processedImage = document.getElementById('processed-image');
    const encryptBtn = document.getElementById('encrypt-btn');
    const decryptBtn = document.getElementById('decrypt-btn');
    const metricsBtn = document.getElementById('metrics-btn');
    const statusMessage = document.getElementById('status-message');
    const loader = document.getElementById('loader');
    const metricsContainer = document.getElementById('metrics-container');
    const entropyValue = document.getElementById('entropy-value');
    const psnrValue = document.getElementById('psnr-value');

    // --- State ---
    const ctx = imageCanvas.getContext('2d');
    let originalImage = null;
    let roi = {};
    let isDrawing = false;

    // --- Utility Functions ---
    const updateStatus = (message, isError = false) => {
        statusMessage.textContent = message;
        statusMessage.style.color = isError ? 'var(--error-color)' : 'var(--text-color)';
    };

    const setLoading = (isLoading) => {
        loader.style.display = isLoading ? 'block' : 'none';
        if (isLoading) {
            statusMessage.textContent = 'Processing...';
        }
    };

    const enableButtons = (state) => {
        encryptBtn.disabled = !state.encrypt;
        decryptBtn.disabled = !state.decrypt;
        metricsBtn.disabled = !state.metrics;
    };

    // --- API Call Functions ---
    const apiCall = async (endpoint, body) => {
        setLoading(true);
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            updateStatus(`Error: ${error.message}`, true);
            return null;
        } finally {
            setLoading(false);
        }
    };

    // --- Event Handlers ---
    const handleImageUpload = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = async (event) => {
            originalImage = new Image();
            originalImage.onload = async () => {
                // Set canvas to image dimensions
                imageCanvas.width = originalImage.width;
                imageCanvas.height = originalImage.height;
                ctx.drawImage(originalImage, 0, 0, imageCanvas.width, imageCanvas.height);
                
                updateStatus('Uploading and processing image...');
                const result = await apiCall('/upload', { image: event.target.result });

                if (result && result.status === 'success') {
                    updateStatus('Image uploaded. Please select a Region of Interest (ROI) by dragging on the image.');
                    enableButtons({ encrypt: false, decrypt: false, metrics: false });
                    processedImage.src = "data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs="; // Reset processed image
                    metricsContainer.style.display = 'none';
                }
            };
            originalImage.src = event.target.result;
        };
        reader.readAsDataURL(file);
    };

    const startDrawing = (e) => {
        if (!originalImage) return;
        isDrawing = true;
        roi.x = e.offsetX;
        roi.y = e.offsetY;
    };

    const draw = (e) => {
        if (!isDrawing || !originalImage) return;

        // Redraw original image to clear previous rectangle
        ctx.drawImage(originalImage, 0, 0, imageCanvas.width, imageCanvas.height);

        // Draw new rectangle
        ctx.strokeStyle = 'red';
        ctx.lineWidth = 2;
        const width = e.offsetX - roi.x;
        const height = e.offsetY - roi.y;
        ctx.strokeRect(roi.x, roi.y, width, height);
    };

    const stopDrawing = (e) => {
        if (!isDrawing) return;
        isDrawing = false;
        roi.w = e.offsetX - roi.x;
        roi.h = e.offsetY - roi.y;

        // Handle negative width/height
        if (roi.w < 0) {
            roi.x += roi.w;
            roi.w = -roi.w;
        }
        if (roi.h < 0) {
            roi.y += roi.h;
            roi.h = -roi.h;
        }

        if (roi.w > 0 && roi.h > 0) {
            updateStatus(`ROI selected at [x:${Math.round(roi.x)}, y:${Math.round(roi.y)}, w:${Math.round(roi.w)}, h:${Math.round(roi.h)}]`);
            enableButtons({ encrypt: true, decrypt: false, metrics: false });
        }
    };

    const encryptROI = async () => {
        if (!roi.w || !roi.h) {
            updateStatus('Please select a valid ROI first.', true);
            return;
        }
        updateStatus('Encrypting selected region...');
        const result = await apiCall('/encrypt', { roi });
        if (result && result.status === 'success') {
            processedImage.src = result.encrypted_image;
            updateStatus('Encryption successful. You can now decrypt or view metrics.');
            enableButtons({ encrypt: true, decrypt: true, metrics: false });
        }
    };

    const decryptROI = async () => {
        updateStatus('Decrypting selected region...');
        const result = await apiCall('/decrypt', {});
        if (result && result.status === 'success') {
            processedImage.src = result.decrypted_image;
            updateStatus('Decryption successful. You can now view metrics.');
            enableButtons({ encrypt: true, decrypt: true, metrics: true });
        }
    };

    const getMetrics = async () => {
        updateStatus('Calculating metrics...');
        const result = await apiCall('/metrics', {});
        if (result) {
            entropyValue.textContent = result.entropy;
            psnrValue.textContent = result.psnr;
            metricsContainer.style.display = 'block';
            updateStatus('Metrics calculated.');
        }
    };

    // --- Initialization ---
    const init = () => {
        // Button Listeners
        imageLoader.addEventListener('change', handleImageUpload);
        encryptBtn.addEventListener('click', encryptROI);
        decryptBtn.addEventListener('click', decryptROI);
        metricsBtn.addEventListener('click', getMetrics);

        // Canvas Listeners
        imageCanvas.addEventListener('mousedown', startDrawing);
        imageCanvas.addEventListener('mousemove', draw);
        imageCanvas.addEventListener('mouseup', stopDrawing);
        imageCanvas.addEventListener('mouseout', () => {
            if (isDrawing) {
                isDrawing = false;
                // Optionally finalize the ROI if mouse leaves canvas while drawing
            }
        });

        // Initial state
        enableButtons({ encrypt: false, decrypt: false, metrics: false });
    };

    init();
});