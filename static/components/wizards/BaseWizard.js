/**
 * Base Wizard Component
 * Provides common wizard functionality and structure
 */

class BaseWizard {
    constructor(containerId, config = {}) {
        this.container = document.getElementById(containerId);
        this.currentStep = 0;
        this.steps = config.steps || [];
        this.onComplete = config.onComplete || (() => {});
        this.onStepChange = config.onStepChange || (() => {});
        this.data = {};
        
        this.init();
    }

    init() {
        this.render();
        this.attachEventListeners();
    }

    render() {
        this.container.innerHTML = `
            <div class="wizard-container bg-white rounded-lg shadow-lg">
                <!-- Wizard Header -->
                <div class="wizard-header bg-blue-600 text-white p-6 rounded-t-lg">
                    <h2 class="text-2xl font-bold">${this.getTitle()}</h2>
                    <p class="text-blue-100 mt-2">${this.getDescription()}</p>
                </div>

                <!-- Progress Bar -->
                <div class="wizard-progress bg-gray-50 p-4">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-sm font-medium text-gray-700">Progress</span>
                        <span class="text-sm text-gray-500">${this.currentStep + 1} of ${this.steps.length}</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                        <div class="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                             style="width: ${((this.currentStep + 1) / this.steps.length) * 100}%"></div>
                    </div>
                    <div class="flex justify-between mt-2">
                        ${this.steps.map((step, index) => `
                            <div class="flex flex-col items-center">
                                <button type="button"
                                    onclick="window.wizardInstance.goToStep(${index})"
                                    class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all
                                    ${index <= this.currentStep
                                        ? 'bg-blue-600 text-white hover:bg-blue-700'
                                        : 'bg-gray-300 text-gray-600 hover:bg-gray-400'}
                                    ${index === this.currentStep ? 'ring-2 ring-blue-400 ring-offset-2' : ''}"
                                    title="Go to step ${index + 1}: ${step.title}">
                                    ${index + 1}
                                </button>
                                <span class="text-xs text-gray-600 mt-1">${step.title}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- Step Content -->
                <div class="wizard-content p-6">
                    <div id="step-content">
                        ${this.renderStepContent()}
                    </div>
                </div>

                <!-- Navigation -->
                <div class="wizard-navigation bg-gray-50 p-4 rounded-b-lg flex justify-between">
                    <button id="prev-btn" class="px-4 py-2 text-gray-600 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors
                        ${this.currentStep === 0 ? 'opacity-50 cursor-not-allowed' : ''}" 
                        ${this.currentStep === 0 ? 'disabled' : ''}>
                        <i class="fas fa-arrow-left mr-2"></i>Previous
                    </button>
                    
                    <div class="flex space-x-2">
                        <button id="save-draft-btn" class="px-4 py-2 text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
                            <i class="fas fa-save mr-2"></i>Save Draft
                        </button>
                        
                        <button id="next-btn" class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                            ${this.currentStep === this.steps.length - 1 ? 
                                '<i class="fas fa-check mr-2"></i>Complete' : 
                                'Next<i class="fas fa-arrow-right ml-2"></i>'
                            }
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    renderStepContent() {
        if (this.currentStep >= this.steps.length) return '';
        
        const step = this.steps[this.currentStep];
        return `
            <div class="step-content">
                <h3 class="text-xl font-bold text-gray-800 mb-4">${step.title}</h3>
                <p class="text-gray-600 mb-6">${step.description || ''}</p>
                <div class="step-fields">
                    ${step.render ? step.render(this.data) : this.renderDefaultFields(step.fields || [])}
                </div>
            </div>
        `;
    }

    renderDefaultFields(fields) {
        return fields.map(field => {
            switch (field.type) {
                case 'text':
                case 'email':
                case 'number':
                    return `
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2" for="${field.id}">
                                ${field.label} ${field.required ? '<span class="text-red-500">*</span>' : ''}
                            </label>
                            <input type="${field.type}" id="${field.id}" name="${field.id}"
                                class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="${field.placeholder || ''}"
                                value="${this.data[field.id] || ''}"
                                ${field.required ? 'required' : ''}>
                            ${field.help ? `<p class="text-sm text-gray-500 mt-1">${field.help}</p>` : ''}
                        </div>
                    `;
                
                case 'textarea':
                    return `
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2" for="${field.id}">
                                ${field.label} ${field.required ? '<span class="text-red-500">*</span>' : ''}
                            </label>
                            <textarea id="${field.id}" name="${field.id}" rows="${field.rows || 4}"
                                class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="${field.placeholder || ''}"
                                ${field.required ? 'required' : ''}>${this.data[field.id] || ''}</textarea>
                            ${field.help ? `<p class="text-sm text-gray-500 mt-1">${field.help}</p>` : ''}
                        </div>
                    `;
                
                case 'select':
                    return `
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2" for="${field.id}">
                                ${field.label} ${field.required ? '<span class="text-red-500">*</span>' : ''}
                            </label>
                            <select id="${field.id}" name="${field.id}"
                                class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                ${field.required ? 'required' : ''}>
                                <option value="">Select ${field.label}</option>
                                ${field.options.map(option => `
                                    <option value="${option.value}" ${this.data[field.id] === option.value ? 'selected' : ''}>
                                        ${option.label}
                                    </option>
                                `).join('')}
                            </select>
                            ${field.help ? `<p class="text-sm text-gray-500 mt-1">${field.help}</p>` : ''}
                        </div>
                    `;
                
                case 'radio':
                    return `
                        <div class="mb-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2">
                                ${field.label} ${field.required ? '<span class="text-red-500">*</span>' : ''}
                            </label>
                            <div class="space-y-2">
                                ${field.options.map(option => `
                                    <label class="flex items-center">
                                        <input type="radio" name="${field.id}" value="${option.value}"
                                            class="mr-2 text-blue-600 focus:ring-blue-500"
                                            ${this.data[field.id] === option.value ? 'checked' : ''}
                                            ${field.required ? 'required' : ''}>
                                        <span class="text-gray-700">${option.label}</span>
                                    </label>
                                `).join('')}
                            </div>
                            ${field.help ? `<p class="text-sm text-gray-500 mt-1">${field.help}</p>` : ''}
                        </div>
                    `;
                
                default:
                    return '';
            }
        }).join('');
    }

    attachEventListeners() {
        // Navigation buttons
        const prevBtn = this.container.querySelector('#prev-btn');
        const nextBtn = this.container.querySelector('#next-btn');
        const saveDraftBtn = this.container.querySelector('#save-draft-btn');

        prevBtn?.addEventListener('click', () => this.previousStep());
        nextBtn?.addEventListener('click', () => this.nextStep());
        saveDraftBtn?.addEventListener('click', () => this.saveDraft());

        // Form field change listeners
        this.container.addEventListener('change', (e) => {
            if (e.target.name) {
                this.data[e.target.name] = e.target.value;
                this.onStepChange(this.currentStep, this.data);
            }
        });

        this.container.addEventListener('input', (e) => {
            if (e.target.name) {
                this.data[e.target.name] = e.target.value;
                this.onStepChange(this.currentStep, this.data);
            }
        });
    }

    nextStep() {
        if (!this.validateCurrentStep()) {
            return;
        }

        this.collectStepData();

        if (this.currentStep === this.steps.length - 1) {
            this.complete();
        } else {
            this.currentStep++;
            this.render();
            this.attachEventListeners();
            this.onStepChange(this.currentStep, this.data);
        }
    }

    previousStep() {
        if (this.currentStep > 0) {
            // Don't validate when going backwards
            this.collectStepData();
            this.currentStep--;
            this.render();
            this.attachEventListeners();
            this.onStepChange(this.currentStep, this.data);

            // Restore any previously entered data to the form
            this.restoreFormData();
        }
    }

    goToStep(stepIndex) {
        // Allow jumping to any step
        if (stepIndex >= 0 && stepIndex < this.steps.length) {
            this.collectStepData();
            this.currentStep = stepIndex;
            this.render();
            this.attachEventListeners();
            this.onStepChange(this.currentStep, this.data);
            this.restoreFormData();
        }
    }

    restoreFormData() {
        // Restore form values from this.data when navigating back
        const stepContainer = this.container.querySelector('#step-content');
        if (!stepContainer) return;

        Object.keys(this.data).forEach(key => {
            const field = stepContainer.querySelector(`[name="${key}"]`);
            if (field && this.data[key]) {
                if (field.type === 'checkbox') {
                    field.checked = this.data[key] === 'true' || this.data[key] === true;
                } else if (field.type === 'radio') {
                    const radio = stepContainer.querySelector(`[name="${key}"][value="${this.data[key]}"]`);
                    if (radio) radio.checked = true;
                } else {
                    field.value = this.data[key];
                }
            }
        });
    }

    validateCurrentStep() {
        const stepContainer = this.container.querySelector('#step-content');
        const requiredFields = stepContainer.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            // Skip validation for hidden fields (type="hidden")
            if (field.type === 'hidden') {
                return;
            }

            if (!field.value.trim()) {
                field.classList.add('border-red-500');
                isValid = false;
            } else {
                field.classList.remove('border-red-500');
            }
        });

        if (!isValid) {
            this.showAlert('Please fill in all required fields.', 'error');
        }

        return isValid;
    }

    collectStepData() {
        const stepContainer = this.container.querySelector('#step-content');
        const inputs = stepContainer.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            if (input.type === 'radio') {
                if (input.checked) {
                    this.data[input.name] = input.value;
                }
            } else {
                this.data[input.name] = input.value;
            }
        });
    }

    complete() {
        this.collectStepData();
        this.onComplete(this.data);
    }

    saveDraft() {
        this.collectStepData();
        localStorage.setItem(`wizard_draft_${this.constructor.name}`, JSON.stringify({
            currentStep: this.currentStep,
            data: this.data,
            timestamp: new Date().toISOString()
        }));
        this.showAlert('Draft saved successfully!', 'success');
    }

    loadDraft() {
        const draft = localStorage.getItem(`wizard_draft_${this.constructor.name}`);
        if (draft) {
            const { currentStep, data } = JSON.parse(draft);
            this.currentStep = currentStep;
            this.data = data;
            this.render();
            this.attachEventListeners();
            return true;
        }
        return false;
    }

    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm`;
        
        const bgColors = {
            success: 'bg-green-100 border-green-500 text-green-700',
            error: 'bg-red-100 border-red-500 text-red-700',
            info: 'bg-blue-100 border-blue-500 text-blue-700'
        };
        
        alertDiv.className += ' ' + bgColors[type];
        alertDiv.innerHTML = `
            <div class="flex items-center">
                <span class="flex-1">${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-gray-500 hover:text-gray-700">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(alertDiv);
        
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 5000);
    }

    // Override these methods in subclasses
    getTitle() {
        return 'Clinical Wizard';
    }

    getDescription() {
        return 'Complete the steps below to generate your clinical documentation.';
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BaseWizard;
}
