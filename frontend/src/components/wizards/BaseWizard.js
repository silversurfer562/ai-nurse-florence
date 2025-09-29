/**
 * Base Wizard Component for AI Nurse Florence
 * Provides common wizard functionality and UI patterns
 */

class BaseWizard {
    constructor(wizardType, containerId) {
        this.wizardType = wizardType;
        this.containerId = containerId;
        this.wizardId = null;
        this.currentStep = 1;
        this.steps = [];
        this.data = {};

        this.apiBase = '/api/v1/wizards';
        this.init();
    }

    async init() {
        this.renderContainer();
        await this.startWizard();
    }

    renderContainer() {
        const container = document.getElementById(this.containerId);
        container.innerHTML = `
            <div class="wizard-container">
                <div class="wizard-header">
                    <h2 class="wizard-title">${this.getTitle()}</h2>
                    <div class="wizard-progress">
                        <div class="progress-bar" id="progress-bar"></div>
                    </div>
                </div>
                <div class="wizard-content" id="wizard-content">
                    <!-- Dynamic content -->
                </div>
                <div class="wizard-actions">
                    <button id="prev-btn" class="btn btn-secondary" disabled>Previous</button>
                    <button id="next-btn" class="btn btn-primary">Next</button>
                </div>
            </div>
        `;

        this.bindEvents();
    }

    bindEvents() {
        document.getElementById('prev-btn').addEventListener('click', () => this.previousStep());
        document.getElementById('next-btn').addEventListener('click', () => this.nextStep());
    }

    async startWizard() {
        try {
            const response = await fetch(`${this.apiBase}/${this.wizardType}/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const result = await response.json();

            if (result.success) {
                this.wizardId = result.data.wizard_id;
                this.renderStep(result.data.next_step);
            }
        } catch (error) {
            this.showError('Failed to start wizard');
        }
    }

    async submitStep(stepData) {
        try {
            const response = await fetch(`${this.apiBase}/${this.wizardType}/${this.currentStep}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    wizard_id: this.wizardId,
                    ...stepData
                })
            });

            return await response.json();
        } catch (error) {
            this.showError('Failed to submit step data');
            return null;
        }
    }

    renderStep(stepName) {
        // Override in subclasses
        console.log(`Rendering step: ${stepName}`);
    }

    getTitle() {
        // Override in subclasses
        return 'Clinical Wizard';
    }

    showError(message) {
        const content = document.getElementById('wizard-content');
        content.innerHTML = `
            <div class="alert alert-error">
                <i class="fas fa-exclamation-triangle"></i>
                ${message}
            </div>
        `;
    }

    updateProgress() {
        const progressBar = document.getElementById('progress-bar');
        const percentage = (this.currentStep / this.steps.length) * 100;
        progressBar.style.width = `${percentage}%`;
    }
}

export default BaseWizard;
