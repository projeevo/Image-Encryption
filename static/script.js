const imageInput = document.getElementById('imageInput');
const canvas = document.getElementById('imageCanvas');
const ctx = canvas.getContext('2d');
const encryptBtn = document.getElementById('encryptBtn');
const decryptBtn = document.getElementById('decryptBtn');
const metricsDiv = document.getElementById('metrics');
const outputImagesDiv = document.getElementById('outputImages');

let image = null;
let roi = null;
let startX, startY, endX, endY, isDrawing = false;
let uploadedImageData = null;

// Handle image upload and preview, and upload to backend immediately
imageInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(evt) {
        const img = new Image();
        img.onload = function() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            image = img;
            uploadedImageData = canvas.toDataURL('image/png');
            // Upload image to backend immediately
            uploadImage();
        };
        img.src = evt.target.result;
    };
    reader.readAsDataURL(file);
});

// ROI selection on canvas
canvas.addEventListener('mousedown', function(e) {
    if (!image) return;
    isDrawing = true;
    const rect = canvas.getBoundingClientRect();
    startX = e.clientX - rect.left;
    startY = e.clientY - rect.top;
});

canvas.addEventListener('mousemove', function(e) {
    if (!isDrawing || !image) return;
    const rect = canvas.getBoundingClientRect();
    endX = e.clientX - rect.left;
    endY = e.clientY - rect.top;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = 'red';
    ctx.lineWidth = 2;
    ctx.strokeRect(startX, startY, endX - startX, endY - startY);
});

canvas.addEventListener('mouseup', function(e) {
    if (!isDrawing || !image) return;
    isDrawing = false;
    const rect = canvas.getBoundingClientRect();
    endX = e.clientX - rect.left;
    endY = e.clientY - rect.top;
    roi = {
        x: Math.round(Math.min(startX, endX)),
        y: Math.round(Math.min(startY, endY)),
        w: Math.round(Math.abs(endX - startX)),
        h: Math.round(Math.abs(endY - startY))
    };
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = 'red';
    ctx.lineWidth = 2;
    ctx.strokeRect(roi.x, roi.y, roi.w, roi.h);
});

// Upload image to server immediately after selection
function uploadImage(callback) {
    if (!uploadedImageData) return;
    fetch('/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: uploadedImageData })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            if (callback) callback();
        }
    });
}

encryptBtn.addEventListener('click', function() {
    if (!roi || !uploadedImageData) {
        alert('Please upload an image and select an ROI.');
        return;
    }
    fetch('/encrypt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ roi: roi })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success' && data.encrypted_image) {
            showOutputImage(data.encrypted_image, 'Encrypted ROI');
            fetchMetrics();
        }
    });
});

decryptBtn.addEventListener('click', function() {
    fetch('/decrypt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success' && data.decrypted_image) {
            showOutputImage(data.decrypted_image, 'Decrypted ROI');
            fetchMetrics();
        }
    });
});

function fetchMetrics() {
    fetch('/metrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(res => res.json())
    .then(data => {
        metricsDiv.innerHTML = `<b>Entropy:</b> ${data.entropy} <br> <b>PSNR:</b> ${data.psnr}`;
    });
}

function showOutputImage(dataUrl, label) {
    const div = document.createElement('div');
    const img = document.createElement('img');
    img.src = dataUrl;
    const caption = document.createElement('div');
    caption.textContent = label;
    div.appendChild(img);
    div.appendChild(caption);
    outputImagesDiv.appendChild(div);
} 