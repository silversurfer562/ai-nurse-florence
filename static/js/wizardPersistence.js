/**
 * Wizard Persistence Library
 * Provides localStorage-based draft saving/loading for clinical wizards
 */

const WizardPersistence = {
    /**
     * Save wizard state to localStorage
     * @param {string} wizardId - Unique identifier for the wizard
     * @param {number} currentStep - Current step number
     * @param {Object} formData - Form data for all steps
     */
    saveWizardState(wizardId, currentStep, formData) {
        try {
            const state = {
                currentStep: currentStep,
                timestamp: new Date().toISOString(),
                formData: formData
            };
            localStorage.setItem(`wizard_draft_${wizardId}`, JSON.stringify(state));
            this.showSaveIndicator();
            return true;
        } catch (error) {
            console.error('Error saving wizard state:', error);
            return false;
        }
    },

    /**
     * Load wizard state from localStorage
     * @param {string} wizardId - Unique identifier for the wizard
     * @returns {Object|null} Saved state or null if no draft exists
     */
    loadWizardState(wizardId) {
        try {
            const stateJson = localStorage.getItem(`wizard_draft_${wizardId}`);
            if (!stateJson) return null;
            return JSON.parse(stateJson);
        } catch (error) {
            console.error('Error loading wizard state:', error);
            return null;
        }
    },

    /**
     * Clear wizard state from localStorage
     * @param {string} wizardId - Unique identifier for the wizard
     */
    clearWizardState(wizardId) {
        try {
            localStorage.removeItem(`wizard_draft_${wizardId}`);
            return true;
        } catch (error) {
            console.error('Error clearing wizard state:', error);
            return false;
        }
    },

    /**
     * Check if a saved draft exists
     * @param {string} wizardId - Unique identifier for the wizard
     * @returns {boolean} True if draft exists
     */
    hasSavedDraft(wizardId) {
        return localStorage.getItem(`wizard_draft_${wizardId}`) !== null;
    },

    /**
     * Get human-readable timestamp of last save
     * @param {string} wizardId - Unique identifier for the wizard
     * @returns {string|null} Formatted timestamp or null
     */
    getLastSaveTime(wizardId) {
        const state = this.loadWizardState(wizardId);
        if (!state || !state.timestamp) return null;

        const date = new Date(state.timestamp);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    },

    /**
     * Show temporary save indicator
     */
    showSaveIndicator() {
        // Check if indicator already exists
        let indicator = document.getElementById('saveIndicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'saveIndicator';
            indicator.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #10b981;
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                font-size: 14px;
                font-weight: 500;
                z-index: 10000;
                display: flex;
                align-items: center;
                gap: 8px;
                opacity: 0;
                transition: opacity 0.3s ease;
            `;
            indicator.innerHTML = '<i class="fas fa-check-circle"></i> Draft saved';
            document.body.appendChild(indicator);
        }

        // Show indicator
        setTimeout(() => indicator.style.opacity = '1', 10);

        // Hide after 2 seconds
        setTimeout(() => {
            indicator.style.opacity = '0';
        }, 2000);
    },

    /**
     * Show resume draft modal
     * @param {string} wizardId - Unique identifier for the wizard
     * @param {Function} onResume - Callback when user clicks Resume
     * @param {Function} onStartFresh - Callback when user clicks Start Fresh
     */
    showResumeDraftModal(wizardId, onResume, onStartFresh) {
        const lastSave = this.getLastSaveTime(wizardId);

        const modal = document.createElement('div');
        modal.id = 'resumeDraftModal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        `;

        modal.innerHTML = `
            <div style="background: white; border-radius: 12px; padding: 24px; max-width: 400px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                    <i class="fas fa-file-alt" style="color: #6366f1; font-size: 24px;"></i>
                    <h3 style="margin: 0; font-size: 18px; font-weight: 600; color: #111827;">Draft Found</h3>
                </div>
                <p style="color: #6b7280; margin-bottom: 20px; line-height: 1.5;">
                    You have an unfinished draft from ${lastSave || 'earlier'}. Would you like to continue where you left off?
                </p>
                <div style="display: flex; gap: 12px;">
                    <button id="resumeDraftBtn" style="flex: 1; background: #6366f1; color: white; border: none; padding: 10px 16px; border-radius: 6px; font-weight: 500; cursor: pointer; transition: background 0.2s;">
                        <i class="fas fa-play"></i> Resume Draft
                    </button>
                    <button id="startFreshBtn" style="flex: 1; background: white; color: #6b7280; border: 1px solid #d1d5db; padding: 10px 16px; border-radius: 6px; font-weight: 500; cursor: pointer; transition: all 0.2s;">
                        <i class="fas fa-redo"></i> Start Fresh
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Add hover effects
        const resumeBtn = document.getElementById('resumeDraftBtn');
        const startFreshBtn = document.getElementById('startFreshBtn');

        resumeBtn.addEventListener('mouseenter', () => resumeBtn.style.background = '#4f46e5');
        resumeBtn.addEventListener('mouseleave', () => resumeBtn.style.background = '#6366f1');
        startFreshBtn.addEventListener('mouseenter', () => {
            startFreshBtn.style.background = '#f3f4f6';
            startFreshBtn.style.borderColor = '#9ca3af';
        });
        startFreshBtn.addEventListener('mouseleave', () => {
            startFreshBtn.style.background = 'white';
            startFreshBtn.style.borderColor = '#d1d5db';
        });

        // Button handlers
        resumeBtn.onclick = () => {
            modal.remove();
            onResume();
        };

        startFreshBtn.onclick = () => {
            this.clearWizardState(wizardId);
            modal.remove();
            onStartFresh();
        };
    },

    /**
     * Auto-save form data from current step
     * @param {string} wizardId - Unique identifier for the wizard
     * @param {number} currentStep - Current step number
     * @param {string} stepId - DOM ID of the current step form
     */
    autoSaveCurrentStep(wizardId, currentStep, stepId) {
        const stepForm = document.getElementById(stepId);
        if (!stepForm) return;

        // Get all form inputs
        const inputs = stepForm.querySelectorAll('input, select, textarea');
        const stepData = {};

        inputs.forEach(input => {
            if (input.id) {
                if (input.type === 'checkbox') {
                    stepData[input.id] = input.checked;
                } else if (input.type === 'radio') {
                    if (input.checked) {
                        stepData[input.name] = input.value;
                    }
                } else {
                    stepData[input.id] = input.value;
                }
            }
        });

        // Load existing state and update
        let existingState = this.loadWizardState(wizardId);
        if (!existingState) {
            existingState = { formData: {} };
        }

        existingState.formData[`step${currentStep}`] = stepData;
        this.saveWizardState(wizardId, currentStep, existingState.formData);
    },

    /**
     * Restore form data to current step
     * @param {string} wizardId - Unique identifier for the wizard
     * @param {number} stepNumber - Step number to restore
     * @param {string} stepId - DOM ID of the step form
     */
    restoreStepData(wizardId, stepNumber, stepId) {
        const state = this.loadWizardState(wizardId);
        if (!state || !state.formData || !state.formData[`step${stepNumber}`]) return;

        const stepData = state.formData[`step${stepNumber}`];
        const stepForm = document.getElementById(stepId);
        if (!stepForm) return;

        // Restore all form inputs
        Object.keys(stepData).forEach(fieldId => {
            const input = document.getElementById(fieldId);
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = stepData[fieldId];
                } else if (input.type === 'radio') {
                    const radio = stepForm.querySelector(`input[name="${fieldId}"][value="${stepData[fieldId]}"]`);
                    if (radio) radio.checked = true;
                } else {
                    input.value = stepData[fieldId];
                }

                // Trigger change event for any dependent calculations
                input.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
    }
};
