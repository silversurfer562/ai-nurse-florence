/**
 * Quick Create Component
 * Fast document generation for routine cases (80% of use cases)
 * One-click creation with smart defaults from diagnosis and work setting
 */

class QuickCreate {
    constructor(containerId, config = {}) {
        this.container = document.getElementById(containerId);
        this.documentType = config.documentType || 'discharge';
        this.onComplete = config.onComplete || (() => {});
        this.workPreset = null;
        this.recentDiagnoses = [];

        this.init();
    }

    async init() {
        await this.loadUserSettings();
        this.render();
        this.attachEventListeners();
    }

    async loadUserSettings() {
        try {
            // Get user profile and work preset
            const userProfile = await this.fetchUserProfile();
            if (userProfile?.work_setting) {
                const response = await fetch(`/api/v1/content-settings/work-preset/${userProfile.work_setting}`);
                if (response.ok) {
                    this.workPreset = await response.json();
                }
            }

            // Get personal library for recent diagnoses
            if (userProfile?.id) {
                const response = await fetch(`/api/v1/content-settings/personal/${userProfile.id}`);
                if (response.ok) {
                    const library = await response.json();
                    this.recentDiagnoses = library.most_used_diagnoses || [];
                    // Sort by count descending
                    this.recentDiagnoses.sort((a, b) => (b.count || 0) - (a.count || 0));
                }
            }
        } catch (error) {
            console.error('Error loading user settings:', error);
        }
    }

    async fetchUserProfile() {
        // Mock for now - will come from auth system
        return {
            id: 'user_123',
            work_setting: 'emergency_department',
            default_reading_level: 'basic',
            default_language: 'en'
        };
    }

    render() {
        this.container.innerHTML = `
            <div class="quick-create-container bg-white rounded-lg shadow-lg max-w-4xl mx-auto">
                <!-- Header -->
                <div class="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 rounded-t-lg">
                    <div class="flex items-center justify-between">
                        <div>
                            <h2 class="text-2xl font-bold flex items-center">
                                <i class="fas fa-bolt mr-3"></i>Quick Create
                            </h2>
                            <p class="text-blue-100 mt-1">Fast document generation for routine cases</p>
                        </div>
                        <button id="use-wizard-btn" class="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors text-sm">
                            <i class="fas fa-magic mr-2"></i>Use Full Wizard
                        </button>
                    </div>
                </div>

                <!-- Quick Create Form -->
                <div class="p-6 space-y-6">
                    ${this.renderQuickStats()}

                    <!-- Diagnosis Quick Select -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-3">
                            <i class="fas fa-stethoscope mr-2 text-blue-600"></i>
                            Select Diagnosis
                        </label>

                        <!-- Recent/Common Diagnoses -->
                        ${this.recentDiagnoses.length > 0 ? `
                            <div class="mb-4">
                                <p class="text-xs text-gray-600 mb-2">Your Most Used:</p>
                                <div class="grid grid-cols-2 gap-2">
                                    ${this.recentDiagnoses.slice(0, 4).map(dx => `
                                        <button class="diagnosis-quick-btn text-left p-3 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors"
                                            data-diagnosis-id="${dx.id}">
                                            <div class="font-semibold text-sm text-blue-900">${dx.name || dx.id}</div>
                                            <div class="text-xs text-blue-700 mt-1">Used ${dx.count} time${dx.count !== 1 ? 's' : ''}</div>
                                        </button>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}

                        <!-- Search -->
                        <div class="relative">
                            <input type="text" id="quick-diagnosis-search"
                                class="w-full p-3 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="Or search by diagnosis name or ICD-10 code...">
                            <i class="fas fa-search absolute right-3 top-4 text-gray-400"></i>
                        </div>
                        <div id="quick-diagnosis-results" class="mt-2"></div>
                    </div>

                    <!-- Selected Diagnosis Preview -->
                    <div id="selected-diagnosis-preview" class="hidden">
                        <div class="bg-gradient-to-r from-green-50 to-green-100 border border-green-300 rounded-lg p-4">
                            <div class="flex items-start justify-between">
                                <div class="flex-1">
                                    <div class="flex items-center">
                                        <i class="fas fa-check-circle text-green-600 mr-2"></i>
                                        <h4 class="font-bold text-green-900" id="selected-dx-name"></h4>
                                    </div>
                                    <p class="text-sm text-green-700 mt-1" id="selected-dx-codes"></p>

                                    <!-- Content Preview -->
                                    <div class="mt-3 grid grid-cols-3 gap-3 text-xs">
                                        <div class="bg-white/50 rounded p-2">
                                            <i class="fas fa-pills text-blue-600"></i>
                                            <span id="preview-meds-count" class="ml-1 font-semibold">0</span> meds
                                        </div>
                                        <div class="bg-white/50 rounded p-2">
                                            <i class="fas fa-exclamation-triangle text-yellow-600"></i>
                                            <span id="preview-warnings-count" class="ml-1 font-semibold">0</span> warnings
                                        </div>
                                        <div class="bg-white/50 rounded p-2">
                                            <i class="fas fa-running text-purple-600"></i>
                                            <span id="preview-activities-count" class="ml-1 font-semibold">0</span> activities
                                        </div>
                                    </div>
                                </div>
                                <button id="change-diagnosis-btn" class="text-green-700 hover:text-green-900 ml-4">
                                    <i class="fas fa-edit"></i> Change
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Patient Info (Optional) -->
                    <div class="border-t border-gray-200 pt-6">
                        <button id="toggle-patient-info" class="text-blue-600 hover:text-blue-800 text-sm font-medium mb-3">
                            <i class="fas fa-chevron-right mr-1 transition-transform" id="patient-info-chevron"></i>
                            Add patient information (optional)
                        </button>
                        <div id="patient-info-section" class="hidden space-y-3">
                            <div class="grid grid-cols-2 gap-3">
                                <input type="text" id="quick-patient-first"
                                    class="p-3 border border-gray-300 rounded-lg"
                                    placeholder="First name (optional)">
                                <input type="text" id="quick-patient-last"
                                    class="p-3 border border-gray-300 rounded-lg"
                                    placeholder="Last name (optional)">
                            </div>
                            <div class="bg-blue-50 border border-blue-200 rounded p-3 text-sm text-blue-800">
                                <i class="fas fa-shield-alt mr-2"></i>
                                Patient names are NOT saved to database (HIPAA-safe)
                            </div>
                        </div>
                    </div>

                    <!-- Settings -->
                    <div class="border-t border-gray-200 pt-6">
                        <label class="block text-sm font-medium text-gray-700 mb-3">Document Settings</label>
                        <div class="grid grid-cols-3 gap-4">
                            <div>
                                <label class="block text-xs text-gray-600 mb-1">Reading Level</label>
                                <select id="quick-reading-level" class="w-full p-2 border border-gray-300 rounded-lg text-sm">
                                    <option value="basic" ${this.workPreset?.default_reading_level === 'basic' ? 'selected' : ''}>
                                        Basic (4th-6th grade)
                                    </option>
                                    <option value="intermediate" ${this.workPreset?.default_reading_level === 'intermediate' ? 'selected' : ''}>
                                        Intermediate (7th-9th)
                                    </option>
                                    <option value="advanced" ${this.workPreset?.default_reading_level === 'advanced' ? 'selected' : ''}>
                                        Advanced (10th+)
                                    </option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-xs text-gray-600 mb-1">Language</label>
                                <select id="quick-language" class="w-full p-2 border border-gray-300 rounded-lg text-sm">
                                    <option value="en">English</option>
                                    <option value="es">Spanish</option>
                                    <option value="zh-CN">Chinese (Simplified)</option>
                                    <option value="zh-TW">Chinese (Traditional)</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-xs text-gray-600 mb-1">Format</label>
                                <select id="quick-format" class="w-full p-2 border border-gray-300 rounded-lg text-sm">
                                    <option value="pdf">PDF</option>
                                    <option value="docx">Word (.docx)</option>
                                    <option value="text">Plain Text</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Action Buttons -->
                <div class="bg-gray-50 p-6 rounded-b-lg flex justify-between items-center">
                    <div class="text-sm text-gray-600">
                        <i class="fas fa-info-circle mr-1"></i>
                        All standard content will be auto-loaded from diagnosis
                    </div>
                    <div class="flex space-x-3">
                        <button id="quick-cancel-btn" class="px-6 py-3 text-gray-600 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors">
                            Cancel
                        </button>
                        <button id="quick-generate-btn" disabled
                            class="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-semibold">
                            <i class="fas fa-bolt mr-2"></i>Generate Document
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    renderQuickStats() {
        if (!this.workPreset) return '';

        return `
            <div class="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-4">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-purple-900">Your Work Setting</p>
                        <p class="text-lg font-bold text-purple-700 capitalize">
                            ${this.workPreset.work_setting.replace(/_/g, ' ')}
                        </p>
                    </div>
                    <div class="text-right">
                        <p class="text-xs text-purple-700">Smart defaults loaded:</p>
                        <div class="flex items-center space-x-3 mt-1">
                            <div class="flex items-center">
                                <i class="fas fa-pills text-purple-600 text-xs"></i>
                                <span class="ml-1 text-sm font-semibold">${this.workPreset.common_medications?.length || 0}</span>
                            </div>
                            <div class="flex items-center">
                                <i class="fas fa-exclamation-triangle text-purple-600 text-xs"></i>
                                <span class="ml-1 text-sm font-semibold">${this.workPreset.common_warning_signs?.length || 0}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        // Use wizard button
        const useWizardBtn = this.container.querySelector('#use-wizard-btn');
        useWizardBtn?.addEventListener('click', () => {
            // Switch to full wizard
            window.location.hash = '#/documents/discharge/wizard';
        });

        // Diagnosis quick buttons
        this.container.querySelectorAll('.diagnosis-quick-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const diagnosisId = btn.dataset.diagnosisId;
                await this.selectDiagnosis(diagnosisId);
            });
        });

        // Diagnosis search
        const searchInput = this.container.querySelector('#quick-diagnosis-search');
        let searchTimeout;
        searchInput?.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.searchDiagnoses(e.target.value);
            }, 300);
        });

        // Toggle patient info
        const toggleBtn = this.container.querySelector('#toggle-patient-info');
        const patientSection = this.container.querySelector('#patient-info-section');
        const chevron = this.container.querySelector('#patient-info-chevron');
        toggleBtn?.addEventListener('click', () => {
            patientSection?.classList.toggle('hidden');
            chevron?.classList.toggle('rotate-90');
        });

        // Change diagnosis
        const changeDxBtn = this.container.querySelector('#change-diagnosis-btn');
        changeDxBtn?.addEventListener('click', () => {
            this.clearSelectedDiagnosis();
        });

        // Generate button
        const generateBtn = this.container.querySelector('#quick-generate-btn');
        generateBtn?.addEventListener('click', () => {
            this.generateDocument();
        });

        // Cancel button
        const cancelBtn = this.container.querySelector('#quick-cancel-btn');
        cancelBtn?.addEventListener('click', () => {
            if (this.onComplete) {
                this.onComplete(null);
            }
        });
    }

    async searchDiagnoses(query) {
        if (!query || query.length < 2) {
            this.container.querySelector('#quick-diagnosis-results').innerHTML = '';
            return;
        }

        try {
            const response = await fetch(`/api/v1/content-settings/diagnosis/search?q=${encodeURIComponent(query)}&limit=5`);
            if (!response.ok) return;

            const results = await response.json();
            const resultsDiv = this.container.querySelector('#quick-diagnosis-results');

            if (results.length === 0) {
                resultsDiv.innerHTML = `
                    <div class="text-sm text-gray-500 p-3 bg-gray-50 rounded">
                        No diagnoses found. Try a different search term.
                    </div>
                `;
                return;
            }

            resultsDiv.innerHTML = results.map(dx => `
                <button class="diagnosis-search-result w-full text-left p-3 border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-colors mb-2"
                    data-diagnosis='${JSON.stringify(dx)}'>
                    <div class="font-semibold text-gray-900">${dx.diagnosis_display}</div>
                    <div class="text-sm text-gray-600 mt-1">ICD-10: ${dx.icd10_code}${dx.snomed_code ? ` | SNOMED: ${dx.snomed_code}` : ''}</div>
                </button>
            `).join('');

            // Attach click handlers to results
            resultsDiv.querySelectorAll('.diagnosis-search-result').forEach(btn => {
                btn.addEventListener('click', () => {
                    const diagnosis = JSON.parse(btn.dataset.diagnosis);
                    this.selectDiagnosis(diagnosis.id, diagnosis);
                });
            });

        } catch (error) {
            console.error('Error searching diagnoses:', error);
        }
    }

    async selectDiagnosis(diagnosisId, diagnosisData = null) {
        try {
            // Fetch full diagnosis data if not provided
            if (!diagnosisData) {
                const response = await fetch(`/api/v1/content-settings/diagnosis/${diagnosisId}`);
                if (!response.ok) throw new Error('Failed to fetch diagnosis');
                diagnosisData = await response.json();
            }

            this.selectedDiagnosis = diagnosisData;

            // Update preview
            this.container.querySelector('#selected-dx-name').textContent = diagnosisData.diagnosis_display;
            this.container.querySelector('#selected-dx-codes').textContent =
                `ICD-10: ${diagnosisData.icd10_code}${diagnosisData.snomed_code ? ` | SNOMED: ${diagnosisData.snomed_code}` : ''}`;

            this.container.querySelector('#preview-meds-count').textContent = diagnosisData.standard_medications?.length || 0;
            this.container.querySelector('#preview-warnings-count').textContent = diagnosisData.standard_warning_signs?.length || 0;
            this.container.querySelector('#preview-activities-count').textContent = diagnosisData.standard_activity_restrictions?.length || 0;

            // Show preview, hide search
            this.container.querySelector('#selected-diagnosis-preview')?.classList.remove('hidden');
            this.container.querySelector('#quick-diagnosis-search').value = '';
            this.container.querySelector('#quick-diagnosis-results').innerHTML = '';

            // Enable generate button
            this.container.querySelector('#quick-generate-btn').disabled = false;

        } catch (error) {
            console.error('Error selecting diagnosis:', error);
            this.showAlert('Error loading diagnosis data', 'error');
        }
    }

    clearSelectedDiagnosis() {
        this.selectedDiagnosis = null;
        this.container.querySelector('#selected-diagnosis-preview')?.classList.add('hidden');
        this.container.querySelector('#quick-generate-btn').disabled = true;
    }

    async generateDocument() {
        if (!this.selectedDiagnosis) {
            this.showAlert('Please select a diagnosis first', 'error');
            return;
        }

        const generateBtn = this.container.querySelector('#quick-generate-btn');
        const originalText = generateBtn.innerHTML;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Generating...';
        generateBtn.disabled = true;

        try {
            // Build FHIR-aligned request
            const request = {
                patient: {
                    patient_given_name: this.container.querySelector('#quick-patient-first')?.value || null,
                    patient_family_name: this.container.querySelector('#quick-patient-last')?.value || null
                },
                primary_diagnosis: {
                    condition_code_icd10: this.selectedDiagnosis.icd10_code,
                    condition_code_snomed: this.selectedDiagnosis.snomed_code,
                    condition_display: this.selectedDiagnosis.diagnosis_display
                },
                medications: this.selectedDiagnosis.standard_medications || [],
                warning_signs: this.selectedDiagnosis.standard_warning_signs || [],
                emergency_criteria: this.workPreset?.common_warning_signs?.filter(s =>
                    s.toLowerCase().includes('911') || s.toLowerCase().includes('emergency')
                ) || [
                    'Difficulty breathing',
                    'Chest pain',
                    'Loss of consciousness',
                    'Severe bleeding'
                ],
                activity_restrictions: this.selectedDiagnosis.standard_activity_restrictions || [],
                diet_instructions: this.selectedDiagnosis.standard_diet_instructions,
                follow_up_instructions: this.selectedDiagnosis.standard_follow_up_instructions ||
                    this.workPreset?.default_follow_up_timeframe ||
                    'Follow up with your doctor in 7-10 days',
                language: this.container.querySelector('#quick-language').value,
                reading_level: this.container.querySelector('#quick-reading-level').value,
                format: this.container.querySelector('#quick-format').value
            };

            // Call API
            const response = await fetch('/api/v1/patient-documents/discharge-instructions-fhir', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(request)
            });

            if (!response.ok) {
                throw new Error('Failed to generate document');
            }

            // Download file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `discharge_instructions_${Date.now()}.${request.format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();

            this.showAlert('Document generated successfully!', 'success');

            // Track usage (NO PHI)
            await fetch(`/api/v1/content-settings/track-usage/user_123`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content_type: 'diagnosis',
                    content_id: this.selectedDiagnosis.id
                })
            });

            // Reset form
            setTimeout(() => {
                this.clearSelectedDiagnosis();
                this.container.querySelector('#quick-patient-first').value = '';
                this.container.querySelector('#quick-patient-last').value = '';
            }, 1000);

        } catch (error) {
            console.error('Error generating document:', error);
            this.showAlert('Error generating document. Please try again.', 'error');
        } finally {
            generateBtn.innerHTML = originalText;
            generateBtn.disabled = false;
        }
    }

    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        const bgColors = {
            success: 'bg-green-100 border-green-500 text-green-700',
            error: 'bg-red-100 border-red-500 text-red-700',
            info: 'bg-blue-100 border-blue-500 text-blue-700'
        };

        alertDiv.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm border-l-4 ${bgColors[type]}`;
        alertDiv.innerHTML = `
            <div class="flex items-center">
                <span class="flex-1">${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-gray-500 hover:text-gray-700">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        document.body.appendChild(alertDiv);
        setTimeout(() => alertDiv.remove(), 5000);
    }
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuickCreate;
}
