/* Create interactive JavaScript following your API Design Standards */
cat > static/js/app.js << 'EOF'
// AI Nurse Florence - Frontend JavaScript
// Following API Design Standards from coding instructions

class AINurseFlorence {
    constructor() {
        this.apiBase = '/api/v1';
        this.currentWizardId = null;
        this.init();
    }

    init() {
        this.initTabs();
        this.initWizards();
        this.initSearch();
        this.initModal();
    }

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
    }

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
        } catch (error) {
            console.error('Error starting wizard:', error);
            alert('Failed to start wizard. Please try again.');
        }
    }

    showWizardModal(wizardData) {
        const modal = document.getElementById('wizard-modal');
        const content = document.getElementById('wizard-content');
        
        content.innerHTML = `
            <div class="wizard-header">
                <h2>🧙‍♀️ ${wizardData.step_title}</h2>
                <div class="progress-bar">
                    <div class="progress" style="width: ${(wizardData.current_step / wizardData.total_steps) * 100}%"></div>
                </div>
                <p>Step ${wizardData.current_step} of ${wizardData.total_steps}</p>
            </div>
            
            <div class="wizard-body">
                <p class="step-description">${wizardData.step_description || ''}</p>
                
                <div class="educational-banner">
                    ⚠️ ${wizardData.educational_note || wizardData.banner}
                </div>
                
                <div class="wizard-form">
                    <p>Wizard ID: ${wizardData.wizard_id}</p>
                    <p>Wizard Type: ${wizardData.wizard_type}</p>
                    
                    <div class="wizard-actions">
                        <button class="btn btn-primary" onclick="app.getWizardStatus()">Check Status</button>
                        <button class="btn btn-secondary" onclick="app.closeModal()">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        modal.classList.remove('hidden');
    }

    async getWizardStatus() {
        if (!this.currentWizardId) return;
        
        try {
            const response = await fetch(`${this.apiBase}/wizard/medication-reconciliation/${this.currentWizardId}/status`);
            const data = await response.json();
            
            console.log('Wizard Status:', data);
            alert(`Wizard Progress: ${data.progress}%\nStatus: ${data.status}`);
        } catch (error) {
            console.error('Error getting wizard status:', error);
        }
    }

    initSearch() {
        document.getElementById('search-btn').addEventListener('click', () => {
            const query = document.getElementById('disease-search').value;
            if (query) this.searchDisease(query);
        });

        document.getElementById('pubmed-btn').addEventListener('click', () => {
            const query = document.getElementById('pubmed-search').value;
            if (query) this.searchPubMed(query);
        });
    }

    async searchDisease(query) {
        const resultsPanel = document.getElementById('search-results');
        resultsPanel.innerHTML = '<div class="loading">🔍 Searching...</div>';

        try {
            const response = await fetch(`${this.apiBase}/disease/?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            resultsPanel.innerHTML = `
                <div class="search-result">
                    <h3>Disease Information</h3>
                    <div class="educational-banner">${data.banner}</div>
                    <p><strong>Query:</strong> ${data.query}</p>
                    <div class="result-content">${data.description || 'Information retrieved successfully.'}</div>
                </div>
            `;
        } catch (error) {
            resultsPanel.innerHTML = `<div class="error">❌ Search failed: ${error.message}</div>`;
        }
    }

    async searchPubMed(query) {
        const resultsPanel = document.getElementById('pubmed-results');
        resultsPanel.innerHTML = '<div class="loading">📚 Searching literature...</div>';

        try {
            const response = await fetch(`${this.apiBase}/literature/?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            resultsPanel.innerHTML = `
                <div class="search-result">
                    <h3>Literature Search Results</h3>
                    <div class="educational-banner">${data.banner}</div>
                    <p><strong>Query:</strong> ${data.query}</p>
                    <div class="result-content">Literature search completed successfully.</div>
                </div>
            `;
        } catch (error) {
            resultsPanel.innerHTML = `<div class="error">❌ Search failed: ${error.message}</div>`;
        }
    }

    initModal() {
        const modal = document.getElementById('wizard-modal');
        const closeBtn = document.querySelector('.close');
        
        closeBtn.addEventListener('click', () => this.closeModal());
        
        window.addEventListener('click', (e) => {
            if (e.target === modal) this.closeModal();
        });
    }

    closeModal() {
        document.getElementById('wizard-modal').classList.add('hidden');
        this.currentWizardId = null;
    }
}

// Initialize the application
const app = new AINurseFlorence();

// Add some CSS for new elements
const additionalCSS = `
    .wizard-header {
        text-align: center;
        margin-bottom: 20px;
    }
    
    .progress-bar {
        background: #e2e8f0;
        height: 8px;
        border-radius: 4px;
        margin: 10px 0;
        overflow: hidden;
    }
    
    .progress {
        background: #16a34a;
        height: 100%;
        transition: width 0.3s ease;
    }
    
    .educational-banner {
        background: #fef2f2;
        border-left: 4px solid #dc2626;
        padding: 10px;
        margin: 15px 0;
        border-radius: 4px;
        color: #dc2626;
        font-weight: 500;
    }
    
    .wizard-actions {
        margin-top: 20px;
        display: flex;
        gap: 10px;
    }
    
    .btn {
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-weight: 500;
    }
    
    .btn-primary {
        background: #2563eb;
        color: white;
    }
    
    .btn-secondary {
        background: #6b7280;
        color: white;
    }
    
    .loading {
        text-align: center;
        padding: 20px;
        color: #6b7280;
    }
    
    .error {
        color: #dc2626;
        padding: 10px;
        background: #fef2f2;
        border-radius: 5px;
    }
    
    .search-result {
        padding: 20px;
    }
`;

const style = document.createElement('style');
style.textContent = additionalCSS;
document.head.appendChild(style);
EOF