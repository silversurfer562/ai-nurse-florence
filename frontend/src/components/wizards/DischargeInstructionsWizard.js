/**
 * Discharge Instructions Wizard
 * Multi-step wizard for creating comprehensive discharge instructions
 * Integrates with FHIR-ready backend and content settings
 */

class DischargeInstructionsWizard extends BaseWizard {
    constructor(containerId, config = {}) {
        const defaultSteps = [
            {
                title: 'Patient & Visit Info',
                description: 'Enter patient and encounter information',
                fields: [
                    {
                        id: 'patient_given_name',
                        type: 'text',
                        label: 'Patient First Name',
                        placeholder: 'Enter first name',
                        required: false,
                        help: 'Optional - Patient data not saved to database (HIPAA-safe)'
                    },
                    {
                        id: 'patient_family_name',
                        type: 'text',
                        label: 'Patient Last Name',
                        placeholder: 'Enter last name',
                        required: false
                    },
                    {
                        id: 'encounter_type',
                        type: 'select',
                        label: 'Visit Type',
                        required: true,
                        options: [
                            { value: 'emergency', label: 'Emergency Department' },
                            { value: 'inpatient', label: 'Inpatient' },
                            { value: 'outpatient', label: 'Outpatient' },
                            { value: 'observation', label: 'Observation' }
                        ]
                    },
                    {
                        id: 'reading_level',
                        type: 'select',
                        label: 'Patient Reading Level',
                        required: true,
                        options: [
                            { value: 'basic', label: 'Basic (4th-6th grade)' },
                            { value: 'intermediate', label: 'Intermediate (7th-9th grade)' },
                            { value: 'advanced', label: 'Advanced (10th+ grade)' }
                        ],
                        help: 'Choose based on patient literacy, not nurse credentials'
                    },
                    {
                        id: 'language',
                        type: 'select',
                        label: 'Language',
                        required: true,
                        options: [
                            { value: 'en', label: 'English' },
                            { value: 'es', label: 'Spanish' },
                            { value: 'zh-CN', label: 'Chinese (Simplified)' },
                            { value: 'zh-TW', label: 'Chinese (Traditional)' }
                        ]
                    }
                ]
            },
            {
                title: 'Diagnosis',
                description: 'Select primary diagnosis and auto-load standard content',
                render: (data) => this.renderDiagnosisStep(data)
            },
            {
                title: 'Medications',
                description: 'Review and customize medications',
                render: (data) => this.renderMedicationsStep(data)
            },
            {
                title: 'Instructions & Restrictions',
                description: 'Activity, diet, and follow-up instructions',
                render: (data) => this.renderInstructionsStep(data)
            },
            {
                title: 'Warning Signs',
                description: 'Warning signs and emergency criteria',
                render: (data) => this.renderWarningSignsStep(data)
            },
            {
                title: 'Review & Export',
                description: 'Review all information and export document',
                render: (data) => this.renderReviewStep(data)
            }
        ];

        super(containerId, {
            ...config,
            steps: config.steps || defaultSteps
        });

        this.diagnosisContent = null;
        this.workPreset = null;
        this.personalLibrary = null;

        // Load user settings
        this.loadUserSettings();
    }

    async loadUserSettings() {
        try {
            // Get work preset based on user's work setting
            const userProfile = await this.fetchUserProfile();
            if (userProfile && userProfile.work_setting) {
                const response = await fetch(`/api/v1/content-settings/work-preset/${userProfile.work_setting}`);
                if (response.ok) {
                    this.workPreset = await response.json();

                    // Pre-fill defaults from work setting
                    if (this.workPreset.default_reading_level) {
                        this.data.reading_level = this.workPreset.default_reading_level;
                    }
                    if (this.workPreset.default_language) {
                        this.data.language = this.workPreset.default_language;
                    }
                }
            }

            // Get personal library
            if (userProfile && userProfile.id) {
                const response = await fetch(`/api/v1/content-settings/personal/${userProfile.id}`);
                if (response.ok) {
                    this.personalLibrary = await response.json();
                }
            }

        } catch (error) {
            console.error('Error loading user settings:', error);
        }
    }

    async fetchUserProfile() {
        // This should come from your auth system
        // For now, return mock data
        return {
            id: 'user_123',
            work_setting: 'emergency_department'
        };
    }

    renderDiagnosisStep(data) {
        return `
            <div class="space-y-4">
                <!-- Diagnosis Search -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Primary Diagnosis <span class="text-red-500">*</span>
                    </label>
                    <input type="text" id="diagnosis-search"
                        class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="Search by diagnosis name or ICD-10 code..."
                        value="${data.diagnosis_search || ''}">
                    <div id="diagnosis-results" class="mt-2 max-h-60 overflow-y-auto"></div>
                </div>

                <!-- Selected Diagnosis -->
                <div id="selected-diagnosis" class="hidden bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div class="flex justify-between items-start">
                        <div>
                            <h4 class="font-bold text-blue-900" id="diagnosis-display"></h4>
                            <p class="text-sm text-blue-700" id="diagnosis-codes"></p>
                        </div>
                        <button id="clear-diagnosis" class="text-red-600 hover:text-red-800">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div id="diagnosis-content-preview" class="mt-4 text-sm text-gray-700"></div>
                </div>

                <!-- Secondary Diagnoses (Optional) -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Secondary Diagnoses (Optional)
                    </label>
                    <div id="secondary-diagnoses-list" class="space-y-2">
                        ${(data.secondary_diagnoses || []).map((dx, idx) => `
                            <div class="flex items-center space-x-2 bg-gray-50 p-2 rounded">
                                <span class="flex-1 text-sm">${dx.condition_display}</span>
                                <button class="text-red-600 hover:text-red-800" onclick="removeSecondaryDiagnosis(${idx})">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                    <button id="add-secondary-dx" class="mt-2 text-blue-600 hover:text-blue-800 text-sm">
                        <i class="fas fa-plus mr-1"></i>Add Secondary Diagnosis
                    </button>
                </div>
            </div>
        `;
    }

    renderMedicationsStep(data) {
        const medications = data.medications || this.diagnosisContent?.standard_medications || [];

        return `
            <div class="space-y-4">
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p class="text-sm text-blue-800">
                        <i class="fas fa-info-circle mr-2"></i>
                        Medications loaded from diagnosis. Click to edit or add new medications.
                    </p>
                </div>

                <!-- Medications List -->
                <div id="medications-list" class="space-y-3">
                    ${medications.map((med, idx) => this.renderMedicationCard(med, idx)).join('')}
                </div>

                <!-- Add Medication -->
                <button id="add-medication-btn" class="w-full py-3 border-2 border-dashed border-blue-300 rounded-lg text-blue-600 hover:bg-blue-50 transition-colors">
                    <i class="fas fa-plus mr-2"></i>Add Medication
                </button>

                <!-- Quick Add from Library -->
                ${this.personalLibrary?.favorite_medications?.length > 0 ? `
                    <div class="mt-4">
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Quick Add from Your Favorites
                        </label>
                        <div class="flex flex-wrap gap-2">
                            ${this.personalLibrary.favorite_medications.slice(0, 5).map(med => `
                                <button class="px-3 py-1 bg-gray-100 text-sm rounded hover:bg-gray-200"
                                    onclick="quickAddMedication('${med.id}')">
                                    ${med.medication_display}
                                </button>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderMedicationCard(med, idx) {
        return `
            <div class="bg-white border border-gray-200 rounded-lg p-4 medication-card" data-index="${idx}">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <h5 class="font-bold text-gray-900">${med.medication_display}</h5>
                        <p class="text-sm text-gray-600 mt-1">
                            ${med.dosage_value} ${med.dosage_unit} - ${med.frequency_display}
                        </p>
                        ${med.instructions ? `
                            <p class="text-sm text-gray-500 mt-2">
                                <i class="fas fa-info-circle mr-1"></i>${med.instructions}
                            </p>
                        ` : ''}
                    </div>
                    <div class="flex space-x-2">
                        <button class="text-blue-600 hover:text-blue-800" onclick="editMedication(${idx})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="text-red-600 hover:text-red-800" onclick="removeMedication(${idx})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    renderInstructionsStep(data) {
        const activityRestrictions = data.activity_restrictions ||
            this.diagnosisContent?.standard_activity_restrictions || [];
        const dietInstructions = data.diet_instructions ||
            this.diagnosisContent?.standard_diet_instructions || '';
        const followUpInstructions = data.follow_up_instructions ||
            this.diagnosisContent?.standard_follow_up_instructions || '';

        return `
            <div class="space-y-6">
                <!-- Activity Restrictions -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Activity Restrictions
                    </label>
                    <div id="activity-restrictions-list" class="space-y-2 mb-3">
                        ${activityRestrictions.map((activity, idx) => `
                            <div class="flex items-center space-x-2 bg-gray-50 p-3 rounded">
                                <input type="checkbox" checked class="text-blue-600">
                                <input type="text" value="${activity}"
                                    class="flex-1 bg-transparent border-none focus:outline-none"
                                    onchange="updateActivityRestriction(${idx}, this.value)">
                                <button class="text-red-600 hover:text-red-800" onclick="removeActivity(${idx})">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                    <button id="add-activity-btn" class="text-blue-600 hover:text-blue-800 text-sm">
                        <i class="fas fa-plus mr-1"></i>Add Activity Restriction
                    </button>

                    <!-- Quick Add from Work Preset -->
                    ${this.workPreset?.common_activity_restrictions?.length > 0 ? `
                        <div class="mt-3">
                            <label class="text-xs text-gray-600">Quick Add (Common for your unit):</label>
                            <div class="flex flex-wrap gap-2 mt-1">
                                ${this.workPreset.common_activity_restrictions.slice(0, 3).map(activity => `
                                    <button class="px-2 py-1 bg-blue-50 text-xs rounded hover:bg-blue-100"
                                        onclick="addActivity('${activity.replace(/'/g, "\\'")}')">
                                        + ${activity}
                                    </button>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>

                <!-- Diet Instructions -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Diet Instructions
                    </label>
                    <textarea id="diet-instructions" rows="3"
                        class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="Enter diet instructions...">${dietInstructions}</textarea>
                </div>

                <!-- Follow-up Instructions -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Follow-up Instructions <span class="text-red-500">*</span>
                    </label>
                    <textarea id="follow-up-instructions" rows="2" required
                        class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., Follow up with primary care doctor in 7-10 days">${followUpInstructions}</textarea>

                    ${this.workPreset?.default_follow_up_timeframe ? `
                        <button class="mt-2 text-blue-600 hover:text-blue-800 text-sm"
                            onclick="document.getElementById('follow-up-instructions').value = '${this.workPreset.default_follow_up_timeframe}'">
                            <i class="fas fa-magic mr-1"></i>Use default: "${this.workPreset.default_follow_up_timeframe}"
                        </button>
                    ` : ''}
                </div>

                <!-- Wound Care (Optional) -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Wound Care Instructions (Optional)
                    </label>
                    <textarea id="wound-care" rows="2"
                        class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="Enter wound care instructions if applicable...">${data.wound_care || ''}</textarea>
                </div>
            </div>
        `;
    }

    renderWarningSignsStep(data) {
        const warningSignsconst = data.warning_signs ||
            this.diagnosisContent?.standard_warning_signs || [];
        const emergencyCriteria = data.emergency_criteria ||
            this.workPreset?.common_warning_signs?.filter(s => s.includes('911') || s.includes('emergency')) || [
                'Chest pain',
                'Difficulty breathing',
                'Loss of consciousness',
                'Severe bleeding'
            ];

        return `
            <div class="space-y-6">
                <!-- Warning Signs -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Warning Signs - Contact Your Doctor If: <span class="text-red-500">*</span>
                    </label>
                    <p class="text-sm text-gray-600 mb-3">
                        Signs that require contacting healthcare provider but not emergency
                    </p>
                    <div id="warning-signs-list" class="space-y-2 mb-3">
                        ${warningSignsconst.map((sign, idx) => `
                            <div class="flex items-center space-x-2 bg-yellow-50 border border-yellow-200 p-3 rounded">
                                <i class="fas fa-exclamation-triangle text-yellow-600"></i>
                                <input type="text" value="${sign}"
                                    class="flex-1 bg-transparent border-none focus:outline-none"
                                    onchange="updateWarningSign(${idx}, this.value)">
                                <button class="text-red-600 hover:text-red-800" onclick="removeWarningSign(${idx})">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                    <button id="add-warning-sign-btn" class="text-blue-600 hover:text-blue-800 text-sm">
                        <i class="fas fa-plus mr-1"></i>Add Warning Sign
                    </button>
                </div>

                <!-- Emergency Criteria -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Call 911 or Go to Emergency Room If: <span class="text-red-500">*</span>
                    </label>
                    <p class="text-sm text-gray-600 mb-3">
                        Life-threatening symptoms requiring immediate emergency care
                    </p>
                    <div id="emergency-criteria-list" class="space-y-2 mb-3">
                        ${emergencyCriteria.map((criteria, idx) => `
                            <div class="flex items-center space-x-2 bg-red-50 border border-red-200 p-3 rounded">
                                <i class="fas fa-ambulance text-red-600"></i>
                                <input type="text" value="${criteria}"
                                    class="flex-1 bg-transparent border-none focus:outline-none"
                                    onchange="updateEmergencyCriteria(${idx}, this.value)">
                                <button class="text-red-600 hover:text-red-800" onclick="removeEmergencyCriteria(${idx})">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                    <button id="add-emergency-criteria-btn" class="text-blue-600 hover:text-blue-800 text-sm">
                        <i class="fas fa-plus mr-1"></i>Add Emergency Criteria
                    </button>
                </div>
            </div>
        `;
    }

    renderReviewStep(data) {
        return `
            <div class="space-y-6">
                <div class="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-6">
                    <h4 class="text-lg font-bold text-blue-900 mb-2">
                        <i class="fas fa-file-medical mr-2"></i>Discharge Instructions Ready
                    </h4>
                    <p class="text-blue-800">
                        Review the summary below and choose your export format.
                    </p>
                </div>

                <!-- Summary -->
                <div class="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
                    <div>
                        <h5 class="font-bold text-gray-700 mb-1">Patient</h5>
                        <p class="text-gray-600">
                            ${data.patient_given_name && data.patient_family_name ?
                                `${data.patient_given_name} ${data.patient_family_name}` :
                                'No patient name entered'}
                        </p>
                        <p class="text-sm text-gray-500">Language: ${this.getLanguageLabel(data.language)} | Reading Level: ${data.reading_level}</p>
                    </div>

                    <div>
                        <h5 class="font-bold text-gray-700 mb-1">Primary Diagnosis</h5>
                        <p class="text-gray-600">${data.diagnosis_display || 'Not selected'}</p>
                        ${data.diagnosis_icd10 ? `<p class="text-sm text-gray-500">ICD-10: ${data.diagnosis_icd10}</p>` : ''}
                    </div>

                    <div>
                        <h5 class="font-bold text-gray-700 mb-1">Medications</h5>
                        <p class="text-gray-600">${(data.medications || []).length} medication(s)</p>
                    </div>

                    <div>
                        <h5 class="font-bold text-gray-700 mb-1">Warning Signs</h5>
                        <p class="text-gray-600">${(data.warning_signs || []).length} warning sign(s) listed</p>
                    </div>
                </div>

                <!-- Export Options -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-3">
                        Export Format <span class="text-red-500">*</span>
                    </label>
                    <div class="grid grid-cols-3 gap-4">
                        <label class="export-option-card">
                            <input type="radio" name="export_format" value="pdf" checked class="hidden">
                            <div class="border-2 border-gray-200 rounded-lg p-4 cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-all">
                                <i class="fas fa-file-pdf text-3xl text-red-600 mb-2"></i>
                                <h6 class="font-bold">PDF</h6>
                                <p class="text-xs text-gray-600">Print-ready format</p>
                            </div>
                        </label>

                        <label class="export-option-card">
                            <input type="radio" name="export_format" value="docx" class="hidden">
                            <div class="border-2 border-gray-200 rounded-lg p-4 cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-all">
                                <i class="fas fa-file-word text-3xl text-blue-600 mb-2"></i>
                                <h6 class="font-bold">Word</h6>
                                <p class="text-xs text-gray-600">Editable format</p>
                            </div>
                        </label>

                        <label class="export-option-card">
                            <input type="radio" name="export_format" value="text" class="hidden">
                            <div class="border-2 border-gray-200 rounded-lg p-4 cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-all">
                                <i class="fas fa-file-alt text-3xl text-gray-600 mb-2"></i>
                                <h6 class="font-bold">Plain Text</h6>
                                <p class="text-xs text-gray-600">Simple format</p>
                            </div>
                        </label>
                    </div>
                </div>

                <!-- Privacy Notice -->
                <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                    <p class="text-sm text-green-800">
                        <i class="fas fa-shield-alt mr-2"></i>
                        <strong>HIPAA-Safe:</strong> Patient information is NOT saved to our servers.
                        This document will be generated and downloaded directly to your device.
                    </p>
                </div>
            </div>
        `;
    }

    getLanguageLabel(code) {
        const labels = {
            'en': 'English',
            'es': 'Spanish',
            'zh-CN': 'Chinese (Simplified)',
            'zh-TW': 'Chinese (Traditional)'
        };
        return labels[code] || code;
    }

    getTitle() {
        return 'Discharge Instructions Wizard';
    }

    getDescription() {
        return 'Create comprehensive discharge instructions with pre-loaded content based on diagnosis and work setting.';
    }

    async complete() {
        this.collectStepData();

        // Show loading
        this.showAlert('Generating discharge instructions...', 'info');

        try {
            // Prepare FHIR-aligned request
            const request = {
                patient: {
                    patient_given_name: this.data.patient_given_name,
                    patient_family_name: this.data.patient_family_name
                },
                primary_diagnosis: {
                    condition_code_icd10: this.data.diagnosis_icd10,
                    condition_code_snomed: this.data.diagnosis_snomed,
                    condition_display: this.data.diagnosis_display
                },
                medications: this.data.medications || [],
                warning_signs: this.data.warning_signs || [],
                emergency_criteria: this.data.emergency_criteria || [],
                activity_restrictions: this.data.activity_restrictions || [],
                diet_instructions: this.data.diet_instructions,
                follow_up_instructions: this.data.follow_up_instructions,
                wound_care: this.data.wound_care,
                language: this.data.language,
                reading_level: this.data.reading_level,
                format: this.data.export_format || 'pdf'
            };

            // Call API
            const response = await fetch('/api/v1/patient-documents/discharge-instructions-fhir', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
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

            this.showAlert('Discharge instructions generated successfully!', 'success');

            // Track usage (NO PHI)
            if (this.data.diagnosis_id) {
                await fetch(`/api/v1/content-settings/track-usage/${this.data.user_id}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        content_type: 'diagnosis',
                        content_id: this.data.diagnosis_id
                    })
                });
            }

            // Clear draft
            localStorage.removeItem(`wizard_draft_${this.constructor.name}`);

            // Callback
            if (this.onComplete) {
                this.onComplete(this.data);
            }

        } catch (error) {
            console.error('Error generating discharge instructions:', error);
            this.showAlert('Error generating document. Please try again.', 'error');
        }
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DischargeInstructionsWizard;
}
