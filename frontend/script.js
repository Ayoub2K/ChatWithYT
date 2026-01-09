const API_BASE = 'http://localhost:8000';
let currentAccessLink = null;
let statusCheckInterval = null;
let lastSubmittedUrl = null;

// Initialize
loadHistory();
checkUrlForAccessLink();

function checkUrlForAccessLink() {
    const urlParams = new URLSearchParams(window.location.search);
    const link = urlParams.get('link');
    if (link) {
        document.getElementById('youtubeUrl').value = link;
        handleSubmit();
    }
}

function handleSubmit() {
    const input = document.getElementById('youtubeUrl').value.trim();
    
    if (!input) {
        showError('Please enter a YouTube URL or access link');
        return;
    }

    // Check if it's a YouTube URL or an access link
    if (input.includes('youtube.com') || input.includes('youtu.be')) {
        submitVideo();
    } else {
        // It's an access link - load directly
        loadSharedLink(input);
    }
}

async function loadSharedLink(accessLink) {
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loader"></span> Loading...';

    document.getElementById('errorSection').classList.add('hidden');
    document.getElementById('statusSection').classList.add('hidden');

    try {
        currentAccessLink = accessLink;
        const response = await fetch(`${API_BASE}/jobs/${currentAccessLink}/result`);
        
        if (!response.ok) {
            throw new Error('Invalid access link or results not found');
        }

        const data = await response.json();

        if (data.status === 'done') {
            document.getElementById('resultsSection').classList.remove('hidden');
            document.getElementById('transcriptBox').textContent = data.transcript;
            document.getElementById('summaryBox').textContent = data.summary;
            document.getElementById('accessLink').textContent = currentAccessLink;
            document.getElementById('chatMessages').innerHTML = '';
        } else if (data.status === 'processing' || data.status === 'queued') {
            // Job still processing - start status check
            document.getElementById('statusSection').classList.remove('hidden');
            updateStatus(data.status);
            startStatusCheck();
        } else if (data.status === 'failed') {
            showError('This job failed to process: ' + (data.error || 'Unknown error'));
        } else {
            showError('Job status: ' + data.status);
        }

    } catch (error) {
        showError('Error loading shared link: ' + error.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit';
    }
}

async function submitVideo() {
    const url = document.getElementById('youtubeUrl').value.trim();
    const whisperModel = document.getElementById('whisperModel').value;
    
    if (!url) {
        showError('Please enter a YouTube URL');
        return;
    }

    lastSubmittedUrl = url;
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loader"></span> Processing...';

    document.getElementById('errorSection').classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE}/jobs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                url,
                whisper_model: whisperModel 
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        currentAccessLink = data.access_link;

        document.getElementById('statusSection').classList.remove('hidden');
        document.getElementById('resultsSection').classList.add('hidden');
        document.getElementById('chatMessages').innerHTML = '';

        updateStatus(data.status);
        startStatusCheck();

    } catch (error) {
        showError('Error submitting video: ' + error.message);
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit';
    }
}

function retryProcessing() {
    if (lastSubmittedUrl) {
        document.getElementById('youtubeUrl').value = lastSubmittedUrl;
        submitVideo();
    }
}

function showError(message) {
    document.getElementById('errorSection').classList.remove('hidden');
    document.getElementById('errorMessage').textContent = message;
}

function startStatusCheck() {
    if (statusCheckInterval) clearInterval(statusCheckInterval);

    statusCheckInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE}/jobs/${currentAccessLink}/status`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            updateStatus(data.status);

            if (data.status === 'done' || data.status === 'failed') {
                clearInterval(statusCheckInterval);
                if (data.status === 'done') {
                    loadResults();
                } else if (data.status === 'failed') {
                    showError('Processing failed. Please try again.');
                }
                document.getElementById('submitBtn').disabled = false;
                document.getElementById('submitBtn').textContent = 'Submit';
            }
        } catch (error) {
            console.error('Status check error:', error);
            showError('Lost connection to server');
            clearInterval(statusCheckInterval);
            document.getElementById('submitBtn').disabled = false;
            document.getElementById('submitBtn').textContent = 'Submit';
        }
    }, 2000);
}

function updateStatus(status) {
    const statusBox = document.getElementById('statusBox');
    statusBox.className = `status ${status}`;
    
    const messages = {
        queued: 'Queued - Waiting to start...',
        processing: 'Processing - Downloading and transcribing video (this may take a few minutes)...',
        done: 'Complete - Results ready',
        failed: 'Failed - Something went wrong'
    };
    
    statusBox.textContent = messages[status] || status;
}

async function loadResults() {
    try {
        const response = await fetch(`${API_BASE}/jobs/${currentAccessLink}/result`);
        const data = await response.json();

        if (data.status === 'done') {
            document.getElementById('resultsSection').classList.remove('hidden');
            document.getElementById('transcriptBox').textContent = data.transcript;
            document.getElementById('summaryBox').textContent = data.summary;
            document.getElementById('accessLink').textContent = currentAccessLink;

            // Save to history
            saveToHistory(lastSubmittedUrl, currentAccessLink);
        }
    } catch (error) {
        showError('Error loading results: ' + error.message);
    }
}

async function askQuestion() {
    const questionInput = document.getElementById('questionInput');
    const question = questionInput.value.trim();

    if (!question) return;

    const chatMessages = document.getElementById('chatMessages');
    
    // Add user message
    const userMsg = document.createElement('div');
    userMsg.className = 'message user';
    userMsg.innerHTML = `<strong>You:</strong>${question}`;
    chatMessages.appendChild(userMsg);

    questionInput.value = '';
    questionInput.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/jobs/${currentAccessLink}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Add assistant message
        const assistantMsg = document.createElement('div');
        assistantMsg.className = 'message assistant';
        assistantMsg.innerHTML = `<strong>Assistant:</strong>${data.answer}`;
        chatMessages.appendChild(assistantMsg);

        chatMessages.scrollTop = chatMessages.scrollHeight;

    } catch (error) {
        showError('Error asking question: ' + error.message);
    } finally {
        questionInput.disabled = false;
        questionInput.focus();
    }
}

function copyAccessLink() {
    const link = document.getElementById('accessLink').textContent;
    copyToClipboard(link, 'Access link copied! Share this token with others.');
}

function copySummary() {
    const summary = document.getElementById('summaryBox').textContent;
    copyToClipboard(summary, 'Summary copied!');
}

function copyTranscript() {
    const transcript = document.getElementById('transcriptBox').textContent;
    copyToClipboard(transcript, 'Transcript copied!');
}

function copyToClipboard(text, message) {
    navigator.clipboard.writeText(text).then(() => {
        alert(message);
    }).catch(err => {
        showError('Failed to copy: ' + err);
    });
}

function downloadSummary() {
    const summary = document.getElementById('summaryBox').textContent;
    downloadText(summary, 'summary.txt');
}

function downloadTranscript() {
    const transcript = document.getElementById('transcriptBox').textContent;
    downloadText(transcript, 'transcript.txt');
}

function downloadText(text, filename) {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// History management
function saveToHistory(url, accessLink) {
    const history = JSON.parse(localStorage.getItem('videoHistory') || '[]');
    const entry = {
        url,
        accessLink,
        timestamp: new Date().toISOString(),
        title: url.includes('youtube.com') ? 'YouTube Video' : url
    };
    
    // Remove duplicates
    const filtered = history.filter(item => item.url !== url);
    filtered.unshift(entry);
    
    // Keep only last 10
    const trimmed = filtered.slice(0, 10);
    localStorage.setItem('videoHistory', JSON.stringify(trimmed));
    loadHistory();
}

function loadHistory() {
    const history = JSON.parse(localStorage.getItem('videoHistory') || '[]');
    const historyList = document.getElementById('historyList');
    
    if (history.length === 0) {
        historyList.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No recent videos</p>';
        return;
    }

    historyList.innerHTML = history.map(item => `
        <div class="history-item" onclick="loadFromHistory('${item.accessLink}')">
            <div class="history-item-info">
                <div class="history-item-title">${item.title}</div>
                <div class="history-item-date">${new Date(item.timestamp).toLocaleString()}</div>
            </div>
            <button class="btn-small btn-secondary" onclick="event.stopPropagation(); deleteHistoryItem('${item.url}')">Delete</button>
        </div>
    `).join('');
}

function loadFromHistory(accessLink) {
    currentAccessLink = accessLink;
    loadResults();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function deleteHistoryItem(url) {
    const history = JSON.parse(localStorage.getItem('videoHistory') || '[]');
    const filtered = history.filter(item => item.url !== url);
    localStorage.setItem('videoHistory', JSON.stringify(filtered));
    loadHistory();
}

function clearHistory() {
    if (confirm('Clear all history?')) {
        localStorage.removeItem('videoHistory');
        loadHistory();
    }
}