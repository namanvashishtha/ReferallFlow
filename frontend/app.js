// ReferralFlow Client Logic
const API_BASE = 'http://localhost:8000/api/v1';

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const userEmail = document.getElementById('userEmail');
const uploadStatus = document.getElementById('uploadStatus');
const progressBar = document.getElementById('progressBar');
const statusText = document.getElementById('statusText');
const activityList = document.getElementById('activityList');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupDragAndDrop();
    loadDashboardMock();
});

function setupDragAndDrop() {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', (e) => handleFiles(e.target.files));
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

function handleFiles(files) {
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

async function uploadFile(file) {
    const email = userEmail.value;
    if (!email) {
        showNotification('Please enter an email for the outreach', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    // Update UI for upload
    uploadStatus.classList.remove('hidden');
    statusText.innerText = `Uploading ${file.name}...`;
    progressBar.style.width = '20%';

    try {
        const response = await fetch(`${API_BASE}/orchestrator/upload?email=${encodeURIComponent(email)}`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Upload failed');

        const result = await response.json();

        progressBar.style.width = '100%';
        statusText.innerText = 'Processing started!';

        showNotification('File uploaded successfully!', 'success');
        addActivity('Resume Uploaded', `${file.name} is being analyzed by AI.`, 'Just now');

        // Hide status after delay
        setTimeout(() => {
            uploadStatus.classList.add('hidden');
            progressBar.style.width = '0%';
        }, 3000);

    } catch (error) {
        console.error('Error:', error);
        statusText.innerText = 'Upload failed.';
        showNotification(error.message, 'error');
    }
}

function addActivity(title, desc, time) {
    const item = document.createElement('div');
    item.className = 'activity-item';
    item.innerHTML = `
        <div class="activity-icon"><i data-lucide="info"></i></div>
        <div class="activity-text">
            <strong>${title}</strong>
            <span>${desc}</span>
        </div>
        <div class="activity-time">${time}</div>
    `;
    activityList.prepend(item);
    lucide.createIcons();
}

function showNotification(message, type = 'info') {
    const container = document.getElementById('notification-container');
    const note = document.createElement('div');
    note.className = `notification ${type}`;
    note.innerText = message;

    container.appendChild(note);

    // Animate in and out
    setTimeout(() => note.remove(), 4000);
}

function loadDashboardMock() {
    // This would ideally fetch from /campaigns in the future
    console.log('Dashboard initialized');
}

// Add simple CSS for notifications
const style = document.createElement('style');
style.innerHTML = `
    #notification-container {
        position: fixed;
        top: 24px;
        right: 24px;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    .notification {
        padding: 16px 24px;
        border-radius: 12px;
        background: #1e2030;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        border-left: 4px solid var(--primary);
        font-size: 14px;
        min-width: 300px;
        animation: slideIn 0.3s ease;
    }
    .notification.error { border-left-color: var(--error); }
    .notification.success { border-left-color: var(--success); }
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
`;
document.head.appendChild(style);
