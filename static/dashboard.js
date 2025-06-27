// Dashboard JavaScript for ExcuseGenie

// DOM Elements
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const sidebar = document.getElementById('sidebar');
const navItems = document.querySelectorAll('.nav-item');
const contentSections = document.querySelectorAll('.content-section');
const generateBtn = document.getElementById('generateBtn');
const excuseResult = document.getElementById('excuseResult');
const excuseText = document.getElementById('excuseText');
const copyBtn = document.getElementById('copyBtn');
const saveBtn = document.getElementById('saveBtn');
const regenerateBtn = document.getElementById('regenerateBtn');
const searchHistory = document.getElementById('searchHistory');
const filterCategory = document.getElementById('filterCategory');
const historyList = document.getElementById('historyList');
const sendSmsBtn = document.getElementById('sendSmsBtn');
const makeCallBtn = document.getElementById('makeCallBtn');
const logList = document.getElementById('logList');

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    loadHistoryFromBackend();
    loadSmsCallLogs();
});

// Initialize dashboard functionality
function initializeDashboard() {
    // Mobile menu toggle
    mobileMenuBtn.addEventListener('click', toggleMobileMenu);
    
    // Navigation
    navItems.forEach(item => {
        item.addEventListener('click', handleNavigation);
    });
    
    // Generate excuse
    generateBtn.addEventListener('click', generateExcuse);
    
    // Excuse actions
    copyBtn.addEventListener('click', copyExcuse);
    saveBtn.addEventListener('click', saveExcuse);
    regenerateBtn.addEventListener('click', generateExcuse);
    
    // History search and filter
    searchHistory.addEventListener('input', filterHistory);
    filterCategory.addEventListener('change', filterHistory);
    
    // SMS/Call functionality
    sendSmsBtn.addEventListener('click', sendSms);
    makeCallBtn.addEventListener('click', makeCall);
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!sidebar.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });
}

// Mobile menu toggle
function toggleMobileMenu() {
    sidebar.classList.toggle('open');
}

// Navigation handling
function handleNavigation(e) {
    e.preventDefault();
    
    const targetSection = e.currentTarget.getAttribute('data-section');
    
    // Update active nav item
    navItems.forEach(item => item.classList.remove('active'));
    e.currentTarget.classList.add('active');
    
    // Show target section
    contentSections.forEach(section => section.classList.remove('active'));
    document.getElementById(targetSection).classList.add('active');
    
    // Close mobile menu
    sidebar.classList.remove('open');
}

// Generate excuse using backend API
async function generateExcuse() {
    const category = document.getElementById('category').value;
    const context = document.getElementById('context').value;
    const tone = document.getElementById('tone').value;
    
    if (!category || !context) {
        showNotification('Please select a category and provide context.', 'error');
        return;
    }
    
    // Get selected proof options
    const proofOptions = [];
    if (document.getElementById('proof-document').checked) proofOptions.push('document');
    if (document.getElementById('proof-chat').checked) proofOptions.push('chat');
    if (document.getElementById('proof-audio').checked) proofOptions.push('audio');
    if (document.getElementById('proof-location').checked) proofOptions.push('location');
    
    // Show loading state
    generateBtn.textContent = 'Generating...';
    generateBtn.disabled = true;
    
    try {
        // Create prompt for the backend
        const prompt = `Generate a ${tone} excuse for ${category} situation: ${context}`;
        
        // Call backend API
        const response = await fetch('/api/generate_excuse', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: prompt,
                category: category,
                context: context,
                tone: tone
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate excuse');
        }
        
        const data = await response.json();
        const excuse = data.excuse;
        
        displayExcuse(excuse, category, context, tone);
        showNotification('Excuse generated successfully!', 'success');
        
        // Generate proof documents if requested
        if (proofOptions.length > 0) {
            await generateProofDocuments(excuse, proofOptions);
        }
        
    } catch (error) {
        console.error('Error generating excuse:', error);
        showNotification('Failed to generate excuse. Please try again.', 'error');
    } finally {
        // Reset button
        generateBtn.textContent = 'Generate Excuse';
        generateBtn.disabled = false;
    }
}

// Generate proof documents
async function generateProofDocuments(excuse, proofTypes) {
    try {
        showNotification('Generating proof documents...', 'info');
        
        const response = await fetch('/api/generate_proof', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                excuse: excuse,
                proof_types: proofTypes
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate proof documents');
        }
        
        const data = await response.json();
        displayProofFiles(data, proofTypes);
        showNotification('Proof documents generated successfully!', 'success');
        
    } catch (error) {
        console.error('Error generating proof documents:', error);
        showNotification('Failed to generate proof documents.', 'error');
    }
}

// Display proof files
function displayProofFiles(data, proofTypes) {
    const proofResult = document.getElementById('proofResult');
    const proofFiles = document.getElementById('proofFiles');
    
    let proofHTML = '';
    let downloadUrls = [];
    
    proofTypes.forEach(type => {
        switch(type) {
            case 'document':
                if (data.pdf_path) {
                    proofHTML += createProofFileHTML('📄', 'Official Document', 'Professional excuse document in PDF format', data.pdf_path, 'Download PDF');
                    downloadUrls.push({url: data.pdf_path, title: 'Official Document'});
                }
                break;
            case 'chat':
                if (data.chat_image_path) {
                    proofHTML += createProofFileHTML('💬', 'Chat Screenshot', 'WhatsApp-style conversation screenshot', data.chat_image_path, 'Download Image');
                    downloadUrls.push({url: data.chat_image_path, title: 'Chat Screenshot'});
                }
                break;
            case 'audio':
                if (data.voice_path) {
                    proofHTML += createProofFileHTML('🎵', 'Audio Recording', 'Voice recording of the excuse', data.voice_path, 'Download Audio');
                    downloadUrls.push({url: data.voice_path, title: 'Audio Recording'});
                }
                break;
            case 'location':
                if (data.location_data) {
                    proofHTML += createLocationDataHTML(data.location_data);
                }
                break;
        }
    });
    
    // Add bulk download option if multiple files
    if (downloadUrls.length > 1) {
        proofHTML = `
            <div class="bulk-download-section" style="margin-bottom: 1rem; padding: 1rem; background: #f0f9ff; border-radius: 8px; border: 1px solid #bae6fd;">
                <h4 style="margin-bottom: 0.5rem; color: #0369a1;">📦 Download All Files</h4>
                <p style="margin-bottom: 1rem; color: #64748b; font-size: 0.875rem;">Download all generated proof documents at once</p>
                <button class="btn btn-primary" onclick="downloadAllFiles(${JSON.stringify(downloadUrls).replace(/"/g, '&quot;')})">
                    📥 Download All (${downloadUrls.length} files)
                </button>
            </div>
        ` + proofHTML;
    }
    
    if (proofHTML) {
        proofFiles.innerHTML = proofHTML;
        proofResult.style.display = 'block';
        proofResult.scrollIntoView({ behavior: 'smooth' });
    }
}

// Download all files function
function downloadAllFiles(downloadUrls) {
    showNotification(`Starting download of ${downloadUrls.length} files...`, 'info');
    
    downloadUrls.forEach((file, index) => {
        setTimeout(() => {
            downloadFile(file.url, file.title);
        }, index * 1000); // Delay each download by 1 second
    });
}

// Create proof file HTML
function createProofFileHTML(icon, title, description, filePath, buttonText) {
    // Convert download URL to preview URL
    const previewPath = filePath.replace('/download_proof/', '/preview_proof/');
    
    return `
        <div class="proof-file">
            <div class="proof-file-header">
                <div class="proof-file-icon">${icon}</div>
                <div class="proof-file-title">${title}</div>
            </div>
            <div class="proof-file-desc">${description}</div>
            <div class="proof-file-actions">
                <button class="btn btn-primary" onclick="downloadFile('${filePath}', '${title}')">${buttonText}</button>
                <button class="btn btn-outline" onclick="previewFile('${previewPath}')">Preview</button>
            </div>
        </div>
    `;
}

// Download file function
function downloadFile(filePath, title) {
    const button = event.target;
    const originalText = button.textContent;
    
    // Show loading state
    button.textContent = 'Downloading...';
    button.disabled = true;
    button.classList.add('loading');
    
    try {
        // Create a temporary link element
        const link = document.createElement('a');
        link.href = filePath;
        link.download = getFilenameFromTitle(title);
        link.style.display = 'none';
        
        // Add to document and trigger download
        document.body.appendChild(link);
        link.click();
        
        // Clean up
        document.body.removeChild(link);
        
        showNotification('Download started!', 'success');
        
    } catch (error) {
        console.error('Error downloading file:', error);
        showNotification('Failed to download file. Please try again.', 'error');
    } finally {
        // Reset button state
        setTimeout(() => {
            button.textContent = originalText;
            button.disabled = false;
            button.classList.remove('loading');
        }, 2000);
    }
}

// Get filename from title
function getFilenameFromTitle(title) {
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    const sanitizedTitle = title.toLowerCase().replace(/[^a-z0-9]/g, '_');
    return `${sanitizedTitle}_${timestamp}`;
}

// Create location data HTML
function createLocationDataHTML(locationData) {
    let locationHTML = `
        <div class="proof-file">
            <div class="proof-file-header">
                <div class="proof-file-icon">📍</div>
                <div class="proof-file-title">Location Data</div>
            </div>
            <div class="proof-file-desc">GPS location history for the excuse period</div>
            <div class="location-data">
    `;
    
    locationData.forEach(location => {
        locationHTML += `
            <div class="location-item">
                <div class="location-info">
                    <div class="location-name">${location.location}</div>
                    <div class="location-time">${location.timestamp}</div>
                </div>
                <span class="location-status">${location.status}</span>
            </div>
        `;
    });
    
    locationHTML += `
            </div>
            <div class="proof-file-actions">
                <button class="btn btn-outline" onclick="copyLocationData()">Copy Data</button>
            </div>
        </div>
    `;
    
    return locationHTML;
}

// Preview file function
function previewFile(filePath) {
    const fileType = filePath.split('.').pop().toLowerCase();
    
    if (fileType === 'pdf') {
        // For PDFs, open in new tab
        window.open(filePath, '_blank');
    } else if (['png', 'jpg', 'jpeg', 'gif'].includes(fileType)) {
        // For images, open in new tab
        window.open(filePath, '_blank');
    } else if (['mp3', 'wav', 'ogg'].includes(fileType)) {
        // For audio, create a modal or use browser's audio player
        showAudioPreview(filePath);
    } else {
        // For other files, trigger download
        downloadFile(filePath, 'File');
    }
}

// Show audio preview
function showAudioPreview(audioPath) {
    // Create a simple audio player modal
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;
    
    const audioPlayer = document.createElement('div');
    audioPlayer.style.cssText = `
        background: white;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        max-width: 400px;
        width: 90%;
    `;
    
    audioPlayer.innerHTML = `
        <h3 style="margin-bottom: 1rem; color: #3b82f6;">Audio Preview</h3>
        <audio controls style="width: 100%; margin-bottom: 1rem;">
            <source src="${audioPath}" type="audio/mpeg">
            Your browser does not support the audio element.
        </audio>
        <button onclick="this.closest('.audio-modal').remove()" class="btn btn-secondary">Close</button>
    `;
    
    audioPlayer.className = 'audio-modal';
    modal.appendChild(audioPlayer);
    document.body.appendChild(modal);
    
    // Close modal when clicking outside
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// Copy location data
function copyLocationData() {
    try {
        // Get the location data from the current proof file
        const locationData = document.querySelector('.location-data');
        if (!locationData) {
            showNotification('No location data found', 'error');
            return;
        }
        
        // Extract location information
        const locationItems = locationData.querySelectorAll('.location-item');
        let locationText = 'Location History:\n\n';
        
        locationItems.forEach(item => {
            const name = item.querySelector('.location-name').textContent;
            const time = item.querySelector('.location-time').textContent;
            const status = item.querySelector('.location-status').textContent;
            locationText += `${name} - ${time} (${status})\n`;
        });
        
        // Copy to clipboard
        if (navigator.clipboard) {
            navigator.clipboard.writeText(locationText).then(() => {
                showNotification('Location data copied to clipboard!', 'success');
            }).catch(() => {
                fallbackCopyTextToClipboard(locationText);
            });
        } else {
            fallbackCopyTextToClipboard(locationText);
        }
        
    } catch (error) {
        console.error('Error copying location data:', error);
        showNotification('Failed to copy location data', 'error');
    }
}

// Display generated excuse
function displayExcuse(excuse, category, context, tone) {
    excuseText.textContent = excuse;
    excuseResult.style.display = 'block';
    
    // Store current excuse data for saving
    excuseResult.dataset.excuse = excuse;
    excuseResult.dataset.category = category;
    excuseResult.dataset.context = context;
    excuseResult.dataset.tone = tone;
    
    // Scroll to result
    excuseResult.scrollIntoView({ behavior: 'smooth' });
}

// Copy excuse to clipboard
function copyExcuse() {
    const text = excuseText.textContent;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Excuse copied to clipboard!', 'success');
        }).catch(() => {
            fallbackCopyTextToClipboard(text);
        });
    } else {
        fallbackCopyTextToClipboard(text);
    }
}

// Fallback copy method
function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showNotification('Excuse copied to clipboard!', 'success');
    } catch (err) {
        showNotification('Failed to copy excuse', 'error');
    }
    
    document.body.removeChild(textArea);
}

// Save excuse to backend
async function saveExcuse() {
    const excuse = excuseResult.dataset.excuse;
    const category = excuseResult.dataset.category;
    const context = excuseResult.dataset.context;
    const tone = excuseResult.dataset.tone;
    
    if (!excuse) {
        showNotification('No excuse to save', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/save_excuse', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: context,
                excuse: excuse,
                apology: '', // Will be generated by backend
                category: category,
                tone: tone
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to save excuse');
        }
        
        const data = await response.json();
        showNotification('Excuse saved to history!', 'success');
        
        // Reload history
        loadHistoryFromBackend();
        
    } catch (error) {
        console.error('Error saving excuse:', error);
        showNotification('Failed to save excuse. Please try again.', 'error');
    }
}

// Load history from backend
async function loadHistoryFromBackend() {
    try {
        const response = await fetch('/api/get_excuses');
        
        if (!response.ok) {
            throw new Error('Failed to load history');
        }
        
        const data = await response.json();
        displayHistory(data.excuses || []);
        
    } catch (error) {
        console.error('Error loading history:', error);
        showNotification('Failed to load excuse history.', 'error');
        // Fallback to empty state
        displayHistory([]);
    }
}

// Display history items
function displayHistory(history) {
    if (history.length === 0) {
        historyList.innerHTML = '<p style="text-align: center; color: #666; padding: 2rem;">No excuses saved yet. Generate your first excuse!</p>';
        return;
    }
    
    historyList.innerHTML = history.map(item => createHistoryItemHTML(item)).join('');
    
    // Add event listeners to new history items
    document.querySelectorAll('.history-copy-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const excuse = e.target.closest('.history-item').dataset.excuse;
            copyTextToClipboard(excuse);
        });
    });
    
    document.querySelectorAll('.history-delete-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = parseInt(e.target.closest('.history-item').dataset.id);
            deleteHistoryItem(id);
        });
    });
    
    document.querySelectorAll('.history-proof-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const excuse = e.target.closest('.history-item').dataset.excuse;
            generateProof(excuse);
        });
    });
}

// Create history item HTML
function createHistoryItemHTML(item) {
    const date = new Date(item.timestamp || item.created_at).toLocaleDateString();
    const time = new Date(item.timestamp || item.created_at).toLocaleTimeString();
    
    return `
        <div class="history-item" data-id="${item.excuse_id || item.id}" data-excuse="${item.excuse}">
            <div class="history-header">
                <div class="history-meta">
                    <span>${date} at ${time}</span>
                    <span class="history-category">${item.category || 'General'}</span>
                </div>
            </div>
            <div class="history-text">${item.excuse}</div>
            <div class="history-actions">
                <button class="btn btn-secondary history-copy-btn">📋 Copy</button>
                <button class="btn btn-outline history-proof-btn">📄 Generate Proof</button>
                <button class="btn btn-outline history-delete-btn">🗑️ Delete</button>
            </div>
        </div>
    `;
}

// Delete history item
async function deleteHistoryItem(id) {
    if (confirm('Are you sure you want to delete this excuse?')) {
        try {
            const response = await fetch(`/api/delete_excuse/${id}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error('Failed to delete excuse');
            }
            
            loadHistoryFromBackend();
            showNotification('Excuse deleted from history', 'success');
            
        } catch (error) {
            console.error('Error deleting excuse:', error);
            showNotification('Failed to delete excuse.', 'error');
        }
    }
}

// Filter history
function filterHistory() {
    const searchTerm = searchHistory.value.toLowerCase();
    const filterValue = filterCategory.value;
    
    // This will be handled by the backend in a real implementation
    // For now, we'll reload with filters
    loadHistoryFromBackend();
}

// Generate proof (document, chat image, etc.)
async function generateProof(excuse) {
    try {
        showNotification('Generating proof documents...', 'info');
        
        const response = await fetch('/api/generate_proof', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                excuse: excuse,
                proof_types: ['document', 'chat', 'audio', 'location']
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate proof');
        }
        
        const data = await response.json();
        
        // Display proof files in a modal or new section
        displayProofFiles(data, ['document', 'chat', 'audio', 'location']);
        showNotification('Proof documents generated successfully!', 'success');
        
    } catch (error) {
        console.error('Error generating proof:', error);
        showNotification('Failed to generate proof.', 'error');
    }
}

// Send SMS
async function sendSms() {
    const excuse = excuseResult.dataset.excuse;
    
    if (!excuse) {
        showNotification('Please generate an excuse first', 'error');
        return;
    }
    
    const phoneNumber = prompt('Enter phone number to send SMS:');
    if (!phoneNumber) return;
    
    try {
        const response = await fetch('/api/send_sms', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                to_number: phoneNumber,
                excuse_text: excuse
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to send SMS');
        }
        
        const data = await response.json();
        showNotification('SMS sent successfully!', 'success');
        loadSmsCallLogs(); // Refresh logs
        
    } catch (error) {
        console.error('Error sending SMS:', error);
        showNotification('Failed to send SMS. Please try again.', 'error');
    }
}

// Make call
async function makeCall() {
    const excuse = excuseResult.dataset.excuse;
    
    if (!excuse) {
        showNotification('Please generate an excuse first', 'error');
        return;
    }
    
    const phoneNumber = prompt('Enter phone number to call:');
    if (!phoneNumber) return;
    
    try {
        const response = await fetch('/api/make_call', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                to_number: phoneNumber,
                excuse_text: excuse
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to make call');
        }
        
        const data = await response.json();
        showNotification('Call initiated successfully!', 'success');
        loadSmsCallLogs(); // Refresh logs
        
    } catch (error) {
        console.error('Error making call:', error);
        showNotification('Failed to make call. Please try again.', 'error');
    }
}

// Load SMS/Call logs
async function loadSmsCallLogs() {
    try {
        const response = await fetch('/api/get_sms_logs');
        
        if (!response.ok) {
            throw new Error('Failed to load logs');
        }
        
        const data = await response.json();
        displaySmsCallLogs(data.logs || []);
        
    } catch (error) {
        console.error('Error loading SMS/Call logs:', error);
        // Keep default sample logs
    }
}

// Display SMS/Call logs
function displaySmsCallLogs(logs) {
    if (logs.length === 0) {
        logList.innerHTML = '<p style="text-align: center; color: #666; padding: 2rem;">No SMS or call logs yet.</p>';
        return;
    }
    
    logList.innerHTML = logs.map(log => `
        <div class="log-item">
            <div class="log-icon">${log.method === 'sms' ? '📱' : '📞'}</div>
            <div class="log-content">
                <div class="log-title">${log.method === 'sms' ? 'SMS Sent' : 'Call Made'}</div>
                <div class="log-details">To: ${log.phone} | Time: ${new Date(log.timestamp).toLocaleString()}</div>
            </div>
        </div>
    `).join('');
}

// Copy text to clipboard helper
function copyTextToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Excuse copied to clipboard!', 'success');
        }).catch(() => {
            fallbackCopyTextToClipboard(text);
        });
    } else {
        fallbackCopyTextToClipboard(text);
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        max-width: 300px;
    `;
    
    // Set background color based on type
    switch(type) {
        case 'success':
            notification.style.background = '#10b981';
            break;
        case 'error':
            notification.style.background = '#ef4444';
            break;
        default:
            notification.style.background = '#3b82f6';
    }
    
    // Add to page
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style); 