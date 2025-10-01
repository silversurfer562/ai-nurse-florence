// AI Nurse Florence - Frontend JavaScript
// Following API Design Standards from coding instructions

class AINurseFlorence {
    constructor() {
        this.apiBase = '/api/v1';
        this.currentWizardId = null;
        this.systemStatus = null;
        this.init();
    }

    init() {
        this.initTabs();
        this.initWizards();
        this.initSearch();
        this.initModal();
        this.loadSystemStatus();
    }

    // Tab Management
    initTabs() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tabId = e.target.dataset.tab;
                this.switchTab(tabId);
            });
        });
    }

    switchTab(tabId) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabId).classList.add('active');

        // Load tab-specific content
        if (tabId === 'api') {
            this.updateSystemStatus();
        }
    }

    // System Status Management
    async loadSystemStatus() {
        try {
            const response = await fetch(`${this.apiBase}/health/`);
            if (response.ok) {
                this.systemStatus = await response.json();
                this.updateSystemStatus();
                console.log('✅ AI Nurse Florence System Status:', this.systemStatus);
            }
        } catch (error) {
            console.warn('⚠️ Could not load system status:', error);
            this.systemStatus = {
                status: 'unknown',
                service: 'AI Nurse Florence',
                services: { available: 0, total: 0 }
            };
        }
    }

    updateSystemStatus() {
        const statusElement = document.getElementById('system-status');
        if (!statusElement || !this.systemStatus) return;

        const { status, service, version, services } = this.systemStatus;
        const available = services?.available || 0;
        const total = services?.total || 0;
        const details = services?.details || {};

        const statusHtml = `
            <h3>System Status</h3>
            <div class="status-grid">
                <div class="status-item">
                    <span class="status-label">Service:</span>
                    <span class="status-value">${service}${version ? ` v${version}` : ''}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Status:</span>
                    <span class="status-value status-${status}">${status.toUpperCase()}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Services:</span>
                    <span class="status-value">${available}/${total} Ready</span>
                </div>
                <div class="service-details">
                    <h4>Service Details:</h4>
                    ${Object.entries(details).map(([name, active]) => `
                        <div class="service-item">
                            <span class="service-name">${name}:</span>
                            <span class="service-status ${active ? 'active' : 'inactive'}">
                                ${active ? '✅ Ready' : '⚠️ Graceful degradation'}
                            </span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        statusElement.innerHTML = statusHtml;
    }

    // Wizard Management Following Wizard Pattern Implementation
    initWizards() {
        document.querySelectorAll('.start-wizard').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const wizardType = e.target.closest('.wizard-card').dataset.wizard;
                this.startWizard(wizardType);
            });
        });
    }

    async startWizard(wizardType) {
        try {
            this.showLoading('Starting Clinical Wizard', 'Initializing workflow...');
            
            const response = await fetch(`${this.apiBase}/wizard/${wizardType}/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.currentWizardId = data.wizard_id;
            this.showWizardModal(data);
            
            // Analytics
            this.trackEvent('wizard_started', { wizard_type: wizardType });
            
        } catch (error) {
            console.error('Error starting wizard:', error);
            this.showError('Failed to start wizard. Please check the API documentation for details.');
        }
    }

    showWizardModal(wizardData) {
        const modal = document.getElementById('wizard-modal');
        const content = document.getElementById('wizard-content');
        
        const progressPercent = (wizardData.current_step / wizardData.total_steps) * 100;
        const wizardTitle = wizardData.wizard_type.replace(/-/g, ' ').toUpperCase();
        
        content.innerHTML = `
            <div class="wizard-header">
                <h2>🧙‍♀️ ${wizardData.step_title}</h2>
                <div class="wizard-meta">
                    <span class="wizard-type-badge">${wizardTitle}</span>
                    <span class="step-indicator">Step ${wizardData.current_step} of ${wizardData.total_steps}</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progressPercent}%"></div>
                    </div>
                    <div class="progress-text">${progressPercent.toFixed(0)}% Complete</div>
                </div>
            </div>
            
            <div class="wizard-body">
                
                <div class="wizard-info">
                    <div class="info-section">
                        <h4>Wizard Information</h4>
                        <div class="info-grid">
                            <div class="info-item">
                                <strong>Wizard ID:</strong> 
                                <code class="wizard-id">${wizardData.wizard_id}</code>
                                <button onclick="app.copyToClipboard('${wizardData.wizard_id}')" class="copy-btn" title="Copy ID">📋</button>
                            </div>
                            <div class="info-item">
                                <strong>Workflow Type:</strong> 
                                <span class="workflow-type">${wizardTitle}</span>
                            </div>
                            <div class="info-item">
                                <strong>Current Step:</strong> 
                                <span class="current-step">${wizardData.step_title}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="next-steps-section">
                        <h4>📋 Next Steps:</h4>
                        <ol class="next-steps-list">
                            <li>Use the <strong>Interactive API Documentation</strong> below to continue this workflow</li>
                            <li>Copy the Wizard ID above for API requests</li>
                            <li>Submit data for the next step using the wizard endpoints</li>
                            <li>Check wizard status to track progress</li>
                        </ol>
                    </div>
                </div>
                
                <div class="wizard-actions">
                    <button class="btn btn-primary" onclick="app.getWizardStatus()">
                        📊 Check Status
                    </button>
                    <button class="btn btn-info" onclick="app.openApiDocs()">
                        📚 Open API Docs
                    </button>
                    <button class="btn btn-success" onclick="app.copyWizardInfo()">
                        📋 Copy Info
                    </button>
                    <button class="btn btn-secondary" onclick="app.closeModal()">
                        ✕ Close
                    </button>
                </div>
            </div>
        `;
        
        modal.classList.remove('hidden');
        
        // Focus management for accessibility
        const firstButton = content.querySelector('.btn');
        if (firstButton) firstButton.focus();
    }

    async getWizardStatus() {
        if (!this.currentWizardId) {
            this.showError('No active wizard session');
            return;
        }
        
        try {
            // Try different endpoints based on wizard type
            let statusResponse = null;
            const endpoints = [
                `/wizard/nursing-assessment/${this.currentWizardId}/status`,
                `/wizard/medication-reconciliation/${this.currentWizardId}/status`,
                `/wizard/sbar-report/${this.currentWizardId}/status`,
                `/wizard/care-plan/${this.currentWizardId}/status`,
                `/wizard/discharge-planning/${this.currentWizardId}/status`
            ];
            
            for (const endpoint of endpoints) {
                try {
                    const response = await fetch(`${this.apiBase}${endpoint}`);
                    if (response.ok) {
                        statusResponse = await response.json();
                        break;
                    }
                } catch (e) {
                    continue;
                }
            }
            
            if (statusResponse) {
                const progress = statusResponse.progress || 0;
                const status = statusResponse.status || 'in_progress';
                this.showSuccess(`Wizard Progress: ${progress}%\nStatus: ${status}`);
            } else {
                this.showError('Could not retrieve wizard status. Use the API documentation to check status manually.');
            }
            
        } catch (error) {
            console.error('Error getting wizard status:', error);
            this.showError('Could not retrieve wizard status. Check console for details.');
        }
    }

    // Search Functionality Following External Service Integration
    initSearch() {
        // Disease search
        const diseaseBtn = document.getElementById('search-btn');
        const diseaseInput = document.getElementById('disease-search');
        
        if (diseaseBtn && diseaseInput) {
            diseaseBtn.addEventListener('click', () => {
                const query = diseaseInput.value.trim();
                if (query) this.searchDisease(query);
            });
            
            diseaseInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    const query = e.target.value.trim();
                    if (query) this.searchDisease(query);
                }
            });
        }

        // PubMed search
        const pubmedBtn = document.getElementById('pubmed-btn');
        const pubmedInput = document.getElementById('pubmed-search');
        
        if (pubmedBtn && pubmedInput) {
            pubmedBtn.addEventListener('click', () => {
                const query = pubmedInput.value.trim();
                if (query) this.searchPubMed(query);
            });
            
            pubmedInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    const query = e.target.value.trim();
                    if (query) this.searchPubMed(query);
                }
            });
        }
    }

    async searchDisease(query) {
        const resultsPanel = document.getElementById('search-results');
        resultsPanel.innerHTML = '<div class="loading">🔍 Searching disease information...</div>';

        try {
            const response = await fetch(`${this.apiBase}/disease/lookup?q=${encodeURIComponent(query)}`);
            
            if (!response.ok) {
                throw new Error(`Search failed with status: ${response.status}`);
            }
            
            const data = await response.json();
            
            resultsPanel.innerHTML = `
                <div class="search-result">
                    <h3>🔬 Disease Information Results</h3>
                    <div class="result-header">
                        <strong>Query:</strong> ${data.query || query}
                    </div>
                    <div class="result-content">
                        ${data.description || data.summary || 'Disease information retrieved successfully. Use the API documentation for detailed results.'}
                    </div>
                    <div class="result-footer">
                        <small>Source: MyDisease.info • For detailed information, use the <a href="/docs" target="_blank">API documentation</a></small>
                    </div>
                </div>
            `;
            
            this.trackEvent('search_disease', { query });
            
        } catch (error) {
            console.error('Disease search error:', error);
            resultsPanel.innerHTML = `
                <div class="error">
                    ❌ Search failed: ${error.message}
                    <br><small>Check the <a href="/docs" target="_blank">API documentation</a> for details</small>
                </div>
            `;
        }
    }

    async searchPubMed(query) {
        const resultsPanel = document.getElementById('pubmed-results');
        resultsPanel.innerHTML = '<div class="loading">📚 Searching medical literature...</div>';

        try {
            const response = await fetch(`${this.apiBase}/literature/search?q=${encodeURIComponent(query)}`);
            
            if (!response.ok) {
                throw new Error(`Literature search failed with status: ${response.status}`);
            }
            
            const data = await response.json();
            
            resultsPanel.innerHTML = `
                <div class="search-result">
                    <h3>📚 Literature Search Results</h3>
                    <div class="result-header">
                        <strong>Query:</strong> ${data.query || query}
                    </div>
                    <div class="result-content">
                        ${data.results_summary || 'Literature search completed successfully. Use the API documentation for detailed results and citations.'}
                        ${data.total_results ? `<br><strong>Results found:</strong> ${data.total_results}` : ''}
                    </div>
                    <div class="result-footer">
                        <small>Source: PubMed • For complete literature results, use the <a href="/docs" target="_blank">API documentation</a></small>
                    </div>
                </div>
            `;
            
            this.trackEvent('search_literature', { query });
            
        } catch (error) {
            console.error('PubMed search error:', error);
            resultsPanel.innerHTML = `
                <div class="error">
                    ❌ Search failed: ${error.message}
                    <br><small>Check the <a href="/docs" target="_blank">API documentation</a> for details</small>
                </div>
            `;
        }
    }

    // Modal Management
    initModal() {
        const modal = document.getElementById('wizard-modal');
        const closeBtn = document.querySelector('.close');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeModal());
        }
        
        // Close on outside click
        window.addEventListener('click', (e) => {
            if (e.target === modal) this.closeModal();
        });
        
        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                this.closeModal();
            }
        });
    }

    showLoading(title = 'Loading', message = 'Please wait...') {
        const modal = document.getElementById('wizard-modal');
        const content = document.getElementById('wizard-content');
        
        content.innerHTML = `
            <div class="loading-content">
                <h2>🔄 ${title}</h2>
                <div class="spinner"></div>
                <p>${message}</p>
            </div>
        `;
        
        modal.classList.remove('hidden');
    }

    closeModal() {
        const modal = document.getElementById('wizard-modal');
        modal.classList.add('hidden');
        this.currentWizardId = null;
    }

    // Utility Functions
    openApiDocs() {
        window.open('/docs', '_blank');
        this.trackEvent('open_api_docs');
    }

    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showSuccess('Copied to clipboard!');
        } catch (error) {
            console.error('Copy failed:', error);
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            this.showSuccess('Copied to clipboard!');
        }
    }

    copyWizardInfo() {
        if (!this.currentWizardId) return;
        
        const info = `AI Nurse Florence - Wizard Session
Wizard ID: ${this.currentWizardId}
API Base: ${window.location.origin}${this.apiBase}
Documentation: ${window.location.origin}/docs`;
        
        this.copyToClipboard(info);
    }

    // Notification System
    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    // Analytics (Simple event tracking)
    trackEvent(eventName, properties = {}) {
        console.log('📊 Event:', eventName, properties);
        // Could integrate with analytics service here
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new AINurseFlorence();
});

// Additional CSS for new components
const additionalCSS = `
    /* Wizard Modal Enhancements */
    .wizard-header {
        text-align: center;
        margin-bottom: 30px;
        padding-bottom: 25px;
        border-bottom: 2px solid var(--border-color);
    }
    
    .wizard-meta {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
        margin: 15px 0;
        flex-wrap: wrap;
    }
    
    .wizard-type-badge {
        background: var(--primary-color);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .step-indicator {
        color: var(--text-muted);
        font-weight: 500;
    }
    
    .progress-container {
        margin: 20px 0;
    }
    
    .progress-bar {
        background: #e2e8f0;
        height: 12px;
        border-radius: 6px;
        overflow: hidden;
        margin-bottom: 8px;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, var(--success-color), var(--primary-color));
        height: 100%;
        transition: width 0.5s ease;
        border-radius: 6px;
    }
    
    .progress-text {
        text-align: center;
        color: var(--success-color);
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    .educational-banner {
        background: #fef2f2;
        border-left: 4px solid var(--secondary-color);
        padding: 20px;
        margin: 25px 0;
        border-radius: 6px;
        color: var(--secondary-color);
        font-weight: 500;
        line-height: 1.5;
    }
    
    .wizard-info {
        background: var(--bg-color);
        padding: 25px;
        border-radius: var(--border-radius-lg);
        margin: 25px 0;
    }
    
    .info-section {
        margin-bottom: 25px;
    }
    
    .info-grid {
        display: grid;
        gap: 15px;
        margin-top: 15px;
    }
    
    .info-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid var(--border-color);
    }
    
    .info-item:last-child {
        border-bottom: none;
    }
    
    .wizard-id {
        background: #f1f5f9;
        padding: 4px 8px;
        border-radius: 4px;
        font-family: 'Monaco', 'Menlo', monospace;
        font-size: 0.85rem;
        margin-right: 8px;
    }
    
    .copy-btn {
        background: none;
        border: none;
        cursor: pointer;
        padding: 4px;
        border-radius: 4px;
        transition: background 0.2s;
    }
    
    .copy-btn:hover {
        background: var(--border-color);
    }
    
    .workflow-type {
        background: var(--info-color);
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .current-step {
        color: var(--primary-color);
        font-weight: 600;
    }
    
    .next-steps-section {
        background: #f0f9ff;
        border-left: 4px solid var(--primary-color);
        padding: 20px;
        border-radius: 6px;
    }
    
    .next-steps-section h4 {
        color: var(--primary-color);
        margin-bottom: 15px;
        font-size: 1.1rem;
    }
    
    .next-steps-list {
        margin-left: 20px;
    }
    
    .next-steps-list li {
        margin-bottom: 10px;
        line-height: 1.6;
    }
    
    .wizard-actions {
        margin-top: 30px;
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .btn {
        padding: 12px 24px;
        border: none;
        border-radius: var(--border-radius);
        cursor: pointer;
        font-weight: 600;
        font-size: 0.95rem;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        transition: all 0.2s ease;
        min-width: 120px;
        justify-content: center;
    }
    
    .btn-primary {
        background: var(--primary-color);
        color: white;
    }
    
    .btn-primary:hover {
        background: #1d4ed8;
        transform: translateY(-1px);
    }
    
    .btn-info {
        background: var(--info-color);
        color: white;
    }
    
    .btn-info:hover {
        background: #0e7490;
        transform: translateY(-1px);
    }
    
    .btn-success {
        background: var(--success-color);
        color: white;
    }
    
    .btn-success:hover {
        background: #15803d;
        transform: translateY(-1px);
    }
    
    .btn-secondary {
        background: #6b7280;
        color: white;
    }
    
    .btn-secondary:hover {
        background: #4b5563;
        transform: translateY(-1px);
    }
    
    /* System Status Styles */
    .status-grid {
        display: grid;
        gap: 15px;
    }
    
    .status-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid var(--border-color);
    }
    
    .status-label {
        font-weight: 600;
        color: var(--text-muted);
    }
    
    .status-value {
        font-weight: 600;
    }
    
    .status-healthy {
        color: var(--success-color);
    }
    
    .status-unknown {
        color: var(--warning-color);
    }
    
    .service-details {
        margin-top: 20px;
        padding-top: 15px;
        border-top: 2px solid var(--border-color);
    }
    
    .service-details h4 {
        color: var(--primary-color);
        margin-bottom: 12px;
        font-size: 1rem;
    }
    
    .service-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        font-size: 0.9rem;
    }
    
    .service-name {
        font-weight: 500;
        text-transform: capitalize;
    }
    
    .service-status.active {
        color: var(--success-color);
    }
    
    .service-status.inactive {
        color: var(--warning-color);
    }
    
    /* Search Results */
    .search-result {
        padding: 25px;
    }
    
    .search-result h3 {
        color: var(--primary-color);
        margin-bottom: 20px;
        font-size: 1.4rem;
    }
    
    .result-header {
        background: var(--bg-color);
        padding: 15px;
        border-radius: var(--border-radius);
        margin: 20px 0;
        font-weight: 500;
    }
    
    .result-content {
        line-height: 1.7;
        margin: 20px 0;
        font-size: 1rem;
    }
    
    .result-footer {
        margin-top: 25px;
        padding-top: 20px;
        border-top: 1px solid var(--border-color);
        color: var(--text-muted);
        font-size: 0.9rem;
    }
    
    .result-footer a {
        color: var(--primary-color);
        text-decoration: none;
        font-weight: 500;
    }
    
    .result-footer a:hover {
        text-decoration: underline;
    }
    
    /* Notification System */
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1100;
        max-width: 400px;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-hover);
        animation: slideInRight 0.3s ease;
    }
    
    .notification-success {
        background: #f0fdf4;
        border-left: 4px solid var(--success-color);
        color: var(--success-color);
    }
    
    .notification-error {
        background: #fef2f2;
        border-left: 4px solid var(--secondary-color);
        color: var(--secondary-color);
    }
    
    .notification-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 20px;
    }
    
    .notification-message {
        flex: 1;
        font-weight: 500;
        white-space: pre-line;
    }
    
    .notification-close {
        background: none;
        border: none;
        font-size: 18px;
        cursor: pointer;
        margin-left: 15px;
        opacity: 0.7;
        transition: opacity 0.2s;
    }
    
    .notification-close:hover {
        opacity: 1;
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    /* Loading States */
    .loading-content {
        text-align: center;
        padding: 60px 40px;
    }
    
    .loading-content h2 {
        color: var(--primary-color);
        margin-bottom: 20px;
    }
    
    .loading-content p {
        color: var(--text-muted);
        margin-top: 20px;
        font-style: italic;
    }
    
    /* Mobile Responsive Enhancements */
    @media (max-width: 768px) {
        .wizard-actions {
            flex-direction: column;
            align-items: stretch;
        }
        
        .btn {
            width: 100%;
        }
        
        .wizard-meta {
            flex-direction: column;
            gap: 10px;
        }
        
        .notification {
            right: 10px;
            left: 10px;
            max-width: none;
        }
        
        .info-item {
            flex-direction: column;
            align-items: flex-start;
            gap: 5px;
        }
        
        .status-item, .service-item {
            flex-direction: column;
            align-items: flex-start;
            gap: 5px;
        }
    }
`;

// Add the additional CSS to the page
const style = document.createElement('style');
style.textContent = additionalCSS;
document.head.appendChild(style);