// Main JavaScript for Nissan Pricing Analyzer

let currentJobId = null;
let progressInterval = null;

// DOM Elements
const analysisForm = document.getElementById('analysis-form');
const inputSection = document.getElementById('input-section');
const progressSection = document.getElementById('progress-section');
const resultsSection = document.getElementById('results-section');
const startBtn = document.getElementById('start-btn');
const downloadBtn = document.getElementById('download-btn');
const newAnalysisBtn = document.getElementById('new-analysis-btn');

// Progress Elements
const statusMessage = document.getElementById('status-message');
const currentCompetitor = document.getElementById('current-competitor');
const completedCompetitors = document.getElementById('completed-competitors');
const totalCompetitors = document.getElementById('total-competitors');
const currentVdp = document.getElementById('current-vdp');
const totalVdps = document.getElementById('total-vdps');
const processedVdps = document.getElementById('processed-vdps');
const progressFill = document.getElementById('progress-fill');
const errorsContainer = document.getElementById('errors-container');
const errorsList = document.getElementById('errors-list');

// Results Elements
const totalResults = document.getElementById('total-results');
const totalErrors = document.getElementById('total-errors');

// Form Submit Handler
analysisForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Get form data
    const formData = {
        gunn_nissan_url: document.getElementById('gunn_nissan_url').value.trim(),
        ingram_park_url: document.getElementById('ingram_park_url').value.trim(),
        boerne_url: document.getElementById('boerne_url').value.trim(),
        champion_nb_url: document.getElementById('champion_nb_url').value.trim(),
        openai_api_key: document.getElementById('openai_api_key').value.trim()
    };

    // Validate at least one sitemap URL
    const hasAtLeastOneUrl = formData.gunn_nissan_url || formData.ingram_park_url ||
                             formData.boerne_url || formData.champion_nb_url;

    if (!hasAtLeastOneUrl) {
        alert('Please enter at least one sitemap URL');
        return;
    }

    if (!formData.openai_api_key) {
        alert('Please enter your OpenAI API key');
        return;
    }

    // Disable form and start analysis
    startBtn.disabled = true;
    startBtn.textContent = '⏳ Starting Analysis...';

    try {
        const response = await fetch('/api/start-analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to start analysis');
        }

        currentJobId = data.job_id;

        // Show progress section
        inputSection.style.display = 'none';
        progressSection.style.display = 'block';

        // Start polling for progress
        startProgressPolling();

    } catch (error) {
        alert('Error starting analysis: ' + error.message);
        startBtn.disabled = false;
        startBtn.textContent = '🚀 Run Analysis';
    }
});

// Start Progress Polling
function startProgressPolling() {
    progressInterval = setInterval(checkProgress, 2000); // Poll every 2 seconds
    checkProgress(); // Check immediately
}

// Stop Progress Polling
function stopProgressPolling() {
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
}

// Check Progress
async function checkProgress() {
    if (!currentJobId) return;

    try {
        const response = await fetch(`/api/job-status/${currentJobId}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to get job status');
        }

        updateProgress(data);

        // Check if completed
        if (data.completed) {
            stopProgressPolling();
            showResults(data);
        }

    } catch (error) {
        console.error('Error checking progress:', error);
        stopProgressPolling();
        statusMessage.textContent = '❌ Error: ' + error.message;
        statusMessage.classList.add('loading');
    }
}

// Update Progress Display
function updateProgress(data) {
    const progress = data.progress;

    // Update status message
    statusMessage.textContent = data.status;
    statusMessage.classList.add('loading');

    // Update stats
    currentCompetitor.textContent = progress.current_competitor || '-';
    completedCompetitors.textContent = progress.completed_competitors || 0;
    totalCompetitors.textContent = progress.total_competitors || 0;
    currentVdp.textContent = progress.current_vdp || 0;
    totalVdps.textContent = progress.total_vdps || 0;
    processedVdps.textContent = progress.processed_vdps || 0;

    // Update progress bar
    const totalPossibleVdps = progress.total_competitors * 3; // VDP_LIMIT
    const progressPercentage = totalPossibleVdps > 0
        ? (progress.processed_vdps / totalPossibleVdps) * 100
        : 0;
    progressFill.style.width = progressPercentage + '%';

    // Update errors
    if (data.errors && data.errors.length > 0) {
        errorsContainer.style.display = 'block';
        errorsList.innerHTML = data.errors.map(error =>
            `<div class="error-item">${escapeHtml(error)}</div>`
        ).join('');
    }
}

// Show Results
function showResults(data) {
    statusMessage.classList.remove('loading');
    statusMessage.textContent = '✅ Analysis Complete!';

    progressSection.style.display = 'none';
    resultsSection.style.display = 'block';

    totalResults.textContent = data.total_results || 0;
    totalErrors.textContent = data.total_errors || 0;
}

// Download CSV
downloadBtn.addEventListener('click', () => {
    if (currentJobId) {
        window.location.href = `/api/download-csv/${currentJobId}`;
    }
});

// New Analysis
newAnalysisBtn.addEventListener('click', () => {
    // Reset everything
    currentJobId = null;
    stopProgressPolling();

    // Reset form
    analysisForm.reset();

    // Reset displays
    inputSection.style.display = 'block';
    progressSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorsContainer.style.display = 'none';
    errorsList.innerHTML = '';

    // Re-enable button
    startBtn.disabled = false;
    startBtn.textContent = '🚀 Run Analysis';
});

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    stopProgressPolling();
});
