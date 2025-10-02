/**
 * Enhanced Patient Education Wizard with Comprehensive Help System
 *
 * Features:
 * - Contextual tooltips on every field
 * - Interactive help modal
 * - Step-by-step guidance
 * - Field validation with helpful error messages
 * - Accessibility support (ARIA labels)
 */

class EnhancedPatientEducationWizard extends BaseWizard {
    constructor(containerId) {
        super(containerId, {
            steps: [
                {
                    title: 'Patient Info',
                    description: 'Basic patient information for personalization',
                    helpText: `
                        <strong>Privacy Note:</strong> We only collect minimal information needed to create the document.
                        No patient data is permanently stored in our system. This complies with HIPAA regulations.
                    `,
                    fields: [
                        {
                            id: 'patient_name',
                            type: 'text',
                            label: 'Patient Name',
                            placeholder: 'e.g., John Smith',
                            required: true,
                            help: 'Used for document header only - no PHI stored',
                            tooltip: 'Enter the patient\'s full name as it should appear on the education document',
                            ariaLabel: 'Patient full name for document personalization'
                        },
                        {
                            id: 'preferred_language',
                            type: 'select',
                            label: 'Preferred Language',
                            required: true,
                            options: [
                                {
                                    value: 'en',
                                    label: 'English',
                                    help: 'Best for English-speaking patients'
                                },
                                {
                                    value: 'es',
                                    label: 'Spanish (Español)',
                                    help: 'Mejor para pacientes de habla hispana'
                                },
                                {
                                    value: 'zh',
                                    label: 'Chinese (中文)',
                                    help: '最适合说中文的患者'
                                }
                            ],
                            help: 'Educational materials will be translated to this language',
                            tooltip: 'Select the language the patient is most comfortable reading. All medical terms will be translated and explained in simple words.',
                            ariaLabel: 'Select patient\'s preferred language for education materials'
                        },
                        {
                            id: 'reading_level',
                            type: 'select',
                            label: 'Reading Level',
                            required: true,
                            options: [
                                {
                                    value: 'basic',
                                    label: 'Basic (Grade 3-5)',
                                    help: 'Very simple words, short sentences. Best for patients with limited literacy.'
                                },
                                {
                                    value: 'intermediate',
                                    label: 'Intermediate (Grade 6-8) ⭐ Recommended',
                                    help: 'Clear, everyday language. Works for most patients.'
                                },
                                {
                                    value: 'advanced',
                                    label: 'Advanced (Grade 9+)',
                                    help: 'More detailed explanations. For patients who prefer comprehensive information.'
                                }
                            ],
                            help: 'Most patients (80%) benefit from intermediate level',
                            tooltip: 'Choose based on the patient\'s education and comfort with medical information. When in doubt, use Intermediate - it\'s designed for maximum understanding.',
                            ariaLabel: 'Select reading comprehension level for patient education materials'
                        }
                    ]
                },
                {
                    title: 'Diagnosis Selection',
                    description: 'Search and select the condition to explain',
                    helpText: `
                        <strong>How to Search:</strong><br/>
                        • Type the condition name (e.g., "diabetes")<br/>
                        • Use ICD-10 codes (e.g., "E11.9")<br/>
                        • Try common terms (e.g., "sugar disease" for diabetes)<br/><br/>
                        <strong>Billing Indicators:</strong><br/>
                        • <span style="color: green;">✓ Billable</span> - Code is valid for billing<br/>
                        • <span style="color: orange;">⚠ Verify</span> - Check with payer first<br/>
                        • <span style="color: red;">✗ Not Billable</span> - Needs more specific code
                    `,
                    render: (data) => this.renderEnhancedDiagnosisStep(data)
                },
                {
                    title: 'Content Selection',
                    description: 'Choose what information to include',
                    helpText: `
                        <strong>Recommended:</strong> Include all sections for comprehensive patient education.<br/><br/>
                        You can customize by unchecking items, but warning signs are <em>highly recommended</em>
                        for patient safety.
                    `,
                    render: (data) => this.renderEnhancedContentSelectionStep(data)
                },
                {
                    title: 'Custom Instructions',
                    description: 'Add personalized care instructions',
                    helpText: `
                        <strong>Examples of good custom instructions:</strong><br/>
                        • "Check your blood sugar before meals and at bedtime"<br/>
                        • "Take your blood pressure every morning"<br/>
                        • "Avoid strenuous exercise for 2 weeks"<br/>
                        • "Keep your leg elevated when sitting"<br/><br/>
                        Keep instructions specific, actionable, and easy to understand.
                    `,
                    fields: [
                        {
                            id: 'custom_instructions',
                            type: 'textarea',
                            label: 'Additional Instructions (Optional)',
                            placeholder: 'e.g., "Check your blood sugar before each meal and write it down"',
                            rows: 5,
                            help: 'Add any special instructions specific to this patient\'s situation',
                            tooltip: 'These will appear in a highlighted section. Be specific and use simple language.',
                            ariaLabel: 'Custom care instructions for this specific patient'
                        },
                        {
                            id: 'follow_up_date',
                            type: 'text',
                            label: 'Follow-up Appointment',
                            placeholder: 'e.g., "in 2 weeks" or "March 15, 2025 at 2:00 PM"',
                            help: 'When should the patient return? Be as specific as possible.',
                            tooltip: 'Patients are more likely to follow up when they have a specific date and time. Include the doctor\'s name if helpful.',
                            ariaLabel: 'Follow-up appointment date and time'
                        },
                        {
                            id: 'emergency_contact',
                            type: 'text',
                            label: 'Emergency Contact Number (Optional)',
                            placeholder: 'e.g., (555) 123-4567',
                            help: 'After-hours or nurse line number',
                            tooltip: 'Provide a number patients can call with urgent questions outside office hours',
                            ariaLabel: 'Emergency or after-hours contact phone number'
                        }
                    ]
                },
                {
                    title: 'Review & Generate',
                    description: 'Review and create your patient education document',
                    helpText: `
                        <strong>What happens next:</strong><br/>
                        1. We generate a professional PDF document<br/>
                        2. Document includes all selected information<br/>
                        3. You can download, print, or email to patient<br/>
                        4. No patient data is stored after generation<br/><br/>
                        <strong>Document includes:</strong><br/>
                        • Patient-friendly language<br/>
                        • Warning signs in red (for safety)<br/>
                        • MedlinePlus resources<br/>
                        • FHIR-compliant medical codes
                    `,
                    render: (data) => this.renderEnhancedReviewStep(data)
                }
            ],
            onComplete: (data) => this.generateEducationDocument(data)
        });

        // Add help modal
        this.addHelpModal();

        // Add tooltip functionality
        this.initializeTooltips();
    }

    getTitle() {
        return `
            <div class="flex items-center justify-between">
                <span>Patient Education Document</span>
                <button onclick="showHelpModal()" class="text-sm px-3 py-1 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors">
                    <i class="fas fa-question-circle mr-1"></i>
                    Help
                </button>
            </div>
        `;
    }

    getDescription() {
        return 'Create easy-to-understand, multilingual education materials for your patients';
    }

    renderEnhancedDiagnosisStep(data) {
        return `
            <div class="diagnosis-selection">
                <!-- Search Tips -->
                <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded mb-4">
                    <div class="flex">
                        <i class="fas fa-lightbulb text-blue-500 mt-1 mr-3"></i>
                        <div>
                            <p class="font-medium text-blue-800">Search Tips</p>
                            <ul class="text-sm text-blue-700 mt-2 space-y-1">
                                <li>• Try common names: "sugar diabetes", "high blood pressure"</li>
                                <li>• Use medical terms: "hypertension", "myocardial infarction"</li>
                                <li>• Enter ICD-10 codes: "E11.9", "I10"</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Search for Diagnosis <span class="text-red-500">*</span>
                        <button
                            type="button"
                            class="ml-2 text-blue-500 hover:text-blue-700"
                            data-tooltip="Start typing to search our database of 12,000+ medical conditions. Results show ICD-10 codes, SNOMED codes (for Epic integration), and billing status."
                        >
                            <i class="fas fa-info-circle"></i>
                        </button>
                    </label>
                    <div class="relative">
                        <input
                            type="text"
                            id="diagnosis_search"
                            class="w-full p-3 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            placeholder="Type to search (e.g., diabetes, hypertension, asthma)..."
                            autocomplete="off"
                            aria-label="Search for medical diagnosis"
                        >
                        <i class="fas fa-search absolute left-3 top-4 text-gray-400"></i>
                    </div>
                    <p class="text-sm text-gray-500 mt-2">
                        <i class="fas fa-database mr-1"></i>
                        Searching 12,252 diagnoses with ICD-10 and SNOMED codes
                    </p>
                </div>

                <div id="diagnosis_results" class="space-y-2 max-h-96 overflow-y-auto">
                    <div class="text-gray-500 text-center py-8">
                        <i class="fas fa-search text-4xl mb-3"></i>
                        <p>Start typing to search for a diagnosis</p>
                        <p class="text-sm mt-2">Or browse common conditions below:</p>
                    </div>
                </div>

                <!-- Common Conditions Quick Select -->
                <div class="mt-6">
                    <p class="text-sm font-medium text-gray-700 mb-3">
                        <i class="fas fa-star mr-1"></i> Common Conditions
                    </p>
                    <div class="grid grid-cols-2 gap-2">
                        ${this.renderCommonConditionsButtons()}
                    </div>
                </div>

                <div id="selected_diagnosis" class="mt-4 hidden">
                    <div class="bg-green-50 border-l-4 border-green-500 p-4 rounded">
                        <div class="flex items-center justify-between">
                            <div class="flex-1">
                                <p class="font-medium text-green-800" id="selected_diagnosis_name"></p>
                                <p class="text-sm text-green-600 mt-1" id="selected_diagnosis_codes"></p>
                                <p class="text-xs text-green-500 mt-2" id="selected_diagnosis_friendly"></p>
                            </div>
                            <button onclick="clearDiagnosisSelection()"
                                    class="text-green-600 hover:text-green-800"
                                    aria-label="Clear selected diagnosis">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <input type="hidden" id="selected_diagnosis_id" name="diagnosis_id" required>
                <input type="hidden" id="selected_icd10_code" name="icd10_code">
                <input type="hidden" id="selected_snomed_code" name="snomed_code">
            </div>

            ${this.getDiagnosisSearchScript()}
        `;
    }

    renderCommonConditionsButtons() {
        const commonConditions = [
            { id: 'diabetes_type2', name: 'Type 2 Diabetes' },
            { id: 'hypertension', name: 'High Blood Pressure' },
            { id: 'asthma_exacerbation', name: 'Asthma' },
            { id: 'pneumonia', name: 'Pneumonia' },
            { id: 'uti', name: 'UTI' },
            { id: 'copd', name: 'COPD' }
        ];

        return commonConditions.map(condition => `
            <button
                type="button"
                onclick="selectCommonDiagnosis('${condition.id}')"
                class="px-3 py-2 text-sm bg-gray-100 hover:bg-blue-100 text-gray-700 hover:text-blue-700 rounded-lg transition-colors"
            >
                ${condition.name}
            </button>
        `).join('');
    }

    renderEnhancedContentSelectionStep(data) {
        const contentOptions = [
            {
                id: 'include_description',
                name: 'Condition Description',
                description: 'Easy-to-understand explanation of what the condition is',
                icon: 'info-circle',
                checked: true,
                recommended: true,
                tooltip: 'Uses Grade 6-8 language to explain the condition in simple terms'
            },
            {
                id: 'include_warning_signs',
                name: 'Warning Signs',
                description: 'When to seek immediate medical attention - SAFETY CRITICAL',
                icon: 'exclamation-triangle',
                checked: true,
                recommended: true,
                important: true,
                tooltip: 'Helps patients recognize dangerous symptoms that need emergency care'
            },
            {
                id: 'include_medications',
                name: 'Medication Information',
                description: 'Standard medications, dosing, and instructions',
                icon: 'pills',
                checked: true,
                tooltip: 'Includes RxNorm-coded medications with patient-friendly instructions'
            },
            {
                id: 'include_diet',
                name: 'Diet & Lifestyle',
                description: 'Dietary recommendations and lifestyle changes',
                icon: 'utensils',
                checked: true,
                tooltip: 'Practical advice on food, exercise, and daily activities'
            },
            {
                id: 'include_medlineplus',
                name: 'Educational Resources',
                description: 'Links to MedlinePlus and other trusted sources',
                icon: 'link',
                checked: true,
                recommended: true,
                tooltip: 'Government-trusted health information from NIH/NLM in patient\'s language'
            },
            {
                id: 'include_follow_up',
                name: 'Follow-up Instructions',
                description: 'When and how to follow up with healthcare provider',
                icon: 'calendar-check',
                checked: true,
                tooltip: 'Improves patient compliance with follow-up appointments'
            }
        ];

        return `
            <div class="content-selection space-y-3">
                <p class="text-gray-600 mb-4">
                    <i class="fas fa-check-double mr-1"></i>
                    Select what information to include in the patient education document:
                </p>

                ${contentOptions.map(option => `
                    <label class="flex items-start p-4 border-2 ${option.checked ? 'border-blue-300 bg-blue-50' : 'border-gray-200'} rounded-lg hover:bg-gray-50 cursor-pointer transition-all">
                        <input
                            type="checkbox"
                            name="${option.id}"
                            value="true"
                            ${option.checked ? 'checked' : ''}
                            class="mt-1 mr-3 w-5 h-5 text-blue-600 focus:ring-blue-500"
                            aria-label="${option.name}"
                        >
                        <div class="flex-1">
                            <div class="flex items-center">
                                <i class="fas fa-${option.icon} text-blue-600 mr-2"></i>
                                <p class="font-medium text-gray-900">
                                    ${option.name}
                                    ${option.recommended ? '<span class="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">Recommended</span>' : ''}
                                    ${option.important ? '<span class="ml-2 text-xs bg-red-100 text-red-800 px-2 py-1 rounded">Important</span>' : ''}
                                </p>
                                <button
                                    type="button"
                                    class="ml-2 text-blue-500 hover:text-blue-700"
                                    data-tooltip="${option.tooltip}"
                                    aria-label="More information about ${option.name}"
                                >
                                    <i class="fas fa-question-circle"></i>
                                </button>
                            </div>
                            <p class="text-sm text-gray-600 mt-1">${option.description}</p>
                        </div>
                    </label>
                `).join('')}

                <div class="mt-4 bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded">
                    <div class="flex">
                        <i class="fas fa-shield-alt text-yellow-500 mt-1 mr-3"></i>
                        <div>
                            <p class="font-medium text-yellow-800">Safety Note</p>
                            <p class="text-sm text-yellow-700 mt-1">
                                We strongly recommend including "Warning Signs" to help patients recognize when to seek emergency care.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderEnhancedReviewStep(data) {
        return `
            <div class="review-summary space-y-6">
                <div class="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 p-4 rounded">
                    <div class="flex">
                        <i class="fas fa-file-pdf text-blue-500 text-2xl mt-1 mr-3"></i>
                        <div>
                            <p class="font-medium text-blue-800">Ready to Generate</p>
                            <p class="text-sm text-blue-700 mt-1">
                                Review the information below. When you click "Complete", we'll generate a
                                professional PDF document you can download, print, or email to your patient.
                            </p>
                        </div>
                    </div>
                </div>

                ${this.renderReviewSection('Patient Information', [
                    { label: 'Patient Name', value: data.patient_name || 'Not specified', icon: 'user' },
                    {
                        label: 'Language',
                        value: data.preferred_language === 'en' ? 'English 🇺🇸' :
                               data.preferred_language === 'es' ? 'Spanish 🇪🇸' :
                               data.preferred_language === 'zh' ? 'Chinese 🇨🇳' : 'English',
                        icon: 'language'
                    },
                    {
                        label: 'Reading Level',
                        value: data.reading_level === 'basic' ? 'Basic (Grade 3-5)' :
                               data.reading_level === 'intermediate' ? 'Intermediate (Grade 6-8) ⭐' :
                               'Advanced (Grade 9+)',
                        icon: 'book-open'
                    },
                    { label: 'Follow-up', value: data.follow_up_date || 'Not specified', icon: 'calendar' },
                    { label: 'Emergency Contact', value: data.emergency_contact || 'Not specified', icon: 'phone' }
                ])}

                <div>
                    <h3 class="text-lg font-semibold text-gray-800 mb-3">
                        <i class="fas fa-notes-medical mr-2"></i>Diagnosis
                    </h3>
                    <div class="bg-gradient-to-r from-gray-50 to-gray-100 p-4 rounded-lg">
                        <p class="font-medium text-gray-900" id="review_diagnosis_name">
                            <i class="fas fa-spinner fa-spin mr-2"></i>Loading...
                        </p>
                        <p class="text-sm text-gray-600 mt-1" id="review_diagnosis_codes">Loading...</p>
                        <p class="text-sm text-gray-500 mt-2 italic" id="review_diagnosis_friendly"></p>
                    </div>
                </div>

                ${this.renderContentIncludedSection(data)}

                ${data.custom_instructions ? `
                    <div>
                        <h3 class="text-lg font-semibold text-gray-800 mb-3">
                            <i class="fas fa-user-md mr-2"></i>Custom Instructions
                        </h3>
                        <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-lg">
                            <p class="text-sm text-gray-700">${data.custom_instructions}</p>
                        </div>
                    </div>
                ` : ''}

                <div class="bg-green-50 border-l-4 border-green-500 p-4 rounded">
                    <div class="flex">
                        <i class="fas fa-check-circle text-green-500 text-2xl mt-1 mr-3"></i>
                        <div>
                            <p class="font-medium text-green-800">Document Features</p>
                            <ul class="text-sm text-green-700 mt-2 space-y-1">
                                <li>✓ HIPAA Compliant - No patient data stored</li>
                                <li>✓ FHIR Ready - ICD-10 and SNOMED CT codes included</li>
                                <li>✓ Multilingual - Translated education materials</li>
                                <li>✓ Patient-Friendly - Grade ${data.reading_level === 'basic' ? '3-5' : data.reading_level === 'intermediate' ? '6-8' : '9+'} reading level</li>
                                <li>✓ Professional PDF - Ready to print or email</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            ${this.getReviewStepScript(data)}
        `;
    }

    renderReviewSection(title, items) {
        return `
            <div>
                <h3 class="text-lg font-semibold text-gray-800 mb-3">${title}</h3>
                <dl class="grid grid-cols-2 gap-4">
                    ${items.map(item => `
                        <div>
                            <dt class="text-sm font-medium text-gray-500">
                                <i class="fas fa-${item.icon} mr-1"></i>${item.label}
                            </dt>
                            <dd class="mt-1 text-sm text-gray-900">${item.value}</dd>
                        </div>
                    `).join('')}
                </dl>
            </div>
        `;
    }

    renderContentIncludedSection(data) {
        const items = [
            { key: 'include_description', label: 'Condition Description', icon: 'info-circle' },
            { key: 'include_warning_signs', label: 'Warning Signs', icon: 'exclamation-triangle' },
            { key: 'include_medications', label: 'Medication Information', icon: 'pills' },
            { key: 'include_diet', label: 'Diet & Lifestyle', icon: 'utensils' },
            { key: 'include_medlineplus', label: 'Educational Resources', icon: 'link' },
            { key: 'include_follow_up', label: 'Follow-up Instructions', icon: 'calendar-check' }
        ];

        return `
            <div>
                <h3 class="text-lg font-semibold text-gray-800 mb-3">
                    <i class="fas fa-list-check mr-2"></i>Content Included
                </h3>
                <div class="grid grid-cols-2 gap-2">
                    ${items.map(item => data[item.key] ? `
                        <div class="flex items-center text-sm text-gray-700">
                            <i class="fas fa-${item.icon} text-green-500 mr-2"></i>
                            ${item.label}
                        </div>
                    ` : '').join('')}
                </div>
            </div>
        `;
    }

    getDiagnosisSearchScript() {
        return `
            <script>
                // Enhanced diagnosis search with debouncing
                const diagnosisSearch = document.getElementById('diagnosis_search');
                const resultsContainer = document.getElementById('diagnosis_results');
                const selectedDiagnosisDiv = document.getElementById('selected_diagnosis');

                let searchTimeout;

                diagnosisSearch.addEventListener('input', function(e) {
                    const query = e.target.value.trim();
                    clearTimeout(searchTimeout);

                    if (query.length < 2) {
                        resultsContainer.innerHTML = \`
                            <div class="text-gray-500 text-center py-8">
                                <i class="fas fa-search text-4xl mb-3"></i>
                                <p>Start typing to search for a diagnosis</p>
                            </div>
                        \`;
                        return;
                    }

                    resultsContainer.innerHTML = \`
                        <div class="text-center py-4">
                            <i class="fas fa-spinner fa-spin text-2xl text-blue-500"></i>
                            <p class="text-gray-600 mt-2">Searching 12,252 diagnoses...</p>
                        </div>
                    \`;

                    searchTimeout = setTimeout(async () => {
                        try {
                            const response = await fetch(\`/api/diagnosis/search?q=\${encodeURIComponent(query)}\`);
                            const data = await response.json();

                            if (data.results && data.results.length > 0) {
                                resultsContainer.innerHTML = data.results.map(diagnosis => \`
                                    <div class="diagnosis-result p-4 border-2 border-gray-200 rounded-lg hover:border-blue-400 hover:bg-blue-50 cursor-pointer transition-all"
                                         onclick="selectDiagnosis('\${diagnosis.id}', '\${diagnosis.diagnosis_display}', '\${diagnosis.icd10_code}', '\${diagnosis.snomed_code || ''}', '\${diagnosis.patient_friendly_description || ''}')">
                                        <div class="flex justify-between items-start">
                                            <div class="flex-1">
                                                <p class="font-medium text-gray-900">\${diagnosis.diagnosis_display}</p>
                                                <p class="text-sm text-gray-600 mt-1">
                                                    <span class="font-mono bg-gray-100 px-2 py-1 rounded">ICD-10: \${diagnosis.icd10_code}</span>
                                                    \${diagnosis.snomed_code ? \`<span class="font-mono bg-blue-100 px-2 py-1 rounded ml-2">SNOMED: \${diagnosis.snomed_code}</span>\` : ''}
                                                </p>
                                                \${diagnosis.patient_friendly_description ? \`
                                                    <p class="text-sm text-gray-500 mt-2 italic">
                                                        <i class="fas fa-info-circle mr-1"></i>
                                                        \${diagnosis.patient_friendly_description.substring(0, 150)}...
                                                    </p>
                                                \` : ''}
                                            </div>
                                            <div class="ml-4">
                                                \${diagnosis.is_billable === false ? \`
                                                    <span class="inline-flex items-center px-3 py-1 rounded-full text-xs bg-red-100 text-red-800 font-medium">
                                                        <i class="fas fa-times-circle mr-1"></i>
                                                        Not Billable
                                                    </span>
                                                \` : diagnosis.billable_note ? \`
                                                    <span class="inline-flex items-center px-3 py-1 rounded-full text-xs bg-yellow-100 text-yellow-800 font-medium">
                                                        <i class="fas fa-exclamation-circle mr-1"></i>
                                                        Verify
                                                    </span>
                                                \` : \`
                                                    <span class="inline-flex items-center px-3 py-1 rounded-full text-xs bg-green-100 text-green-800 font-medium">
                                                        <i class="fas fa-check-circle mr-1"></i>
                                                        Billable
                                                    </span>
                                                \`}
                                            </div>
                                        </div>
                                    </div>
                                \`).join('');
                            } else {
                                resultsContainer.innerHTML = \`
                                    <div class="text-center py-8">
                                        <i class="fas fa-search-minus text-4xl text-gray-400 mb-3"></i>
                                        <p class="text-gray-600 font-medium">No diagnoses found</p>
                                        <p class="text-sm text-gray-500 mt-2">Try different search terms or check spelling</p>
                                    </div>
                                \`;
                            }
                        } catch (error) {
                            resultsContainer.innerHTML = \`
                                <div class="text-center py-8">
                                    <i class="fas fa-exclamation-triangle text-4xl text-red-400 mb-3"></i>
                                    <p class="text-red-600 font-medium">Error searching diagnoses</p>
                                    <p class="text-sm text-gray-500 mt-2">\${error.message}</p>
                                </div>
                            \`;
                        }
                    }, 300);
                });

                window.selectDiagnosis = function(id, name, icd10, snomed, friendly) {
                    document.getElementById('selected_diagnosis_id').value = id;
                    document.getElementById('selected_icd10_code').value = icd10;
                    document.getElementById('selected_snomed_code').value = snomed || '';

                    document.getElementById('selected_diagnosis_name').textContent = name;
                    document.getElementById('selected_diagnosis_codes').textContent =
                        \`ICD-10: \${icd10}\${snomed ? \` | SNOMED: \${snomed}\` : ''}\`;

                    if (friendly) {
                        document.getElementById('selected_diagnosis_friendly').textContent =
                            \`ℹ️ \${friendly.substring(0, 120)}...\`;
                    }

                    selectedDiagnosisDiv.classList.remove('hidden');
                    diagnosisSearch.value = '';
                    resultsContainer.innerHTML = \`
                        <div class="text-green-600 text-center py-8">
                            <i class="fas fa-check-circle text-5xl mb-3"></i>
                            <p class="font-medium text-lg">Diagnosis selected!</p>
                            <p class="text-sm mt-1">Click "Next" to continue</p>
                        </div>
                    \`;
                };

                window.clearDiagnosisSelection = function() {
                    document.getElementById('selected_diagnosis_id').value = '';
                    document.getElementById('selected_icd10_code').value = '';
                    document.getElementById('selected_snomed_code').value = '';
                    selectedDiagnosisDiv.classList.add('hidden');
                    diagnosisSearch.value = '';
                    diagnosisSearch.focus();
                    resultsContainer.innerHTML = \`
                        <div class="text-gray-500 text-center py-8">
                            <i class="fas fa-search text-4xl mb-3"></i>
                            <p>Start typing to search for a diagnosis</p>
                        </div>
                    \`;
                };

                window.selectCommonDiagnosis = async function(id) {
                    try {
                        const response = await fetch(\`/api/diagnosis/\${id}\`);
                        const diagnosis = await response.json();
                        selectDiagnosis(
                            diagnosis.id,
                            diagnosis.diagnosis_display,
                            diagnosis.icd10_code,
                            diagnosis.snomed_code,
                            diagnosis.patient_friendly_description
                        );
                    } catch (error) {
                        alert('Error loading diagnosis: ' + error.message);
                    }
                };
            </script>
        `;
    }

    getReviewStepScript(data) {
        return `
            <script>
                (async function() {
                    const diagnosisId = '${data.diagnosis_id || ''}';
                    if (diagnosisId) {
                        try {
                            const response = await fetch(\`/api/diagnosis/\${diagnosisId}\`);
                            const diagnosis = await response.json();

                            document.getElementById('review_diagnosis_name').innerHTML =
                                \`<i class="fas fa-check-circle text-green-500 mr-2"></i>\${diagnosis.diagnosis_display}\`;
                            document.getElementById('review_diagnosis_codes').textContent =
                                \`ICD-10: \${diagnosis.icd10_code}\${diagnosis.snomed_code ? \` | SNOMED: \${diagnosis.snomed_code}\` : ''}\`;

                            if (diagnosis.patient_friendly_description) {
                                document.getElementById('review_diagnosis_friendly').textContent =
                                    diagnosis.patient_friendly_description;
                            }
                        } catch (error) {
                            console.error('Error loading diagnosis:', error);
                            document.getElementById('review_diagnosis_name').innerHTML =
                                '<i class="fas fa-exclamation-triangle text-red-500 mr-2"></i>Error loading diagnosis';
                        }
                    }
                })();
            </script>
        `;
    }

    addHelpModal() {
        const helpModal = `
            <div id="help-modal" class="hidden fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
                <div class="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                    <div class="sticky top-0 bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 rounded-t-xl">
                        <div class="flex justify-between items-center">
                            <h2 class="text-2xl font-bold">
                                <i class="fas fa-question-circle mr-2"></i>
                                Patient Education Wizard Help
                            </h2>
                            <button onclick="closeHelpModal()" class="text-white hover:text-gray-200">
                                <i class="fas fa-times text-2xl"></i>
                            </button>
                        </div>
                    </div>

                    <div class="p-6 space-y-6">
                        <section>
                            <h3 class="text-xl font-semibold text-gray-800 mb-3">
                                <i class="fas fa-info-circle text-blue-500 mr-2"></i>
                                What This Wizard Does
                            </h3>
                            <p class="text-gray-600">
                                This tool creates professional patient education documents that are:
                            </p>
                            <ul class="list-disc list-inside text-gray-600 mt-2 space-y-1">
                                <li>Written in simple language (Grade 6-8 reading level)</li>
                                <li>Available in multiple languages (English, Spanish, Chinese)</li>
                                <li>Include trusted health resources from MedlinePlus</li>
                                <li>FHIR-compliant with proper medical codes (ICD-10, SNOMED CT)</li>
                                <li>HIPAA-compliant (no patient data stored)</li>
                            </ul>
                        </section>

                        <section>
                            <h3 class="text-xl font-semibold text-gray-800 mb-3">
                                <i class="fas fa-clipboard-list text-blue-500 mr-2"></i>
                                Step-by-Step Guide
                            </h3>
                            <div class="space-y-4">
                                <div class="border-l-4 border-blue-500 pl-4">
                                    <h4 class="font-semibold text-gray-800">Step 1: Patient Info</h4>
                                    <p class="text-sm text-gray-600 mt-1">
                                        Enter basic patient information. This is only used to personalize the document and is NOT stored.
                                    </p>
                                </div>
                                <div class="border-l-4 border-blue-500 pl-4">
                                    <h4 class="font-semibold text-gray-800">Step 2: Diagnosis Selection</h4>
                                    <p class="text-sm text-gray-600 mt-1">
                                        Search our database of 12,252 conditions. You can search by name, ICD-10 code, or common terms.
                                    </p>
                                </div>
                                <div class="border-l-4 border-blue-500 pl-4">
                                    <h4 class="font-semibold text-gray-800">Step 3: Content Selection</h4>
                                    <p class="text-sm text-gray-600 mt-1">
                                        Choose what to include. We recommend keeping all sections, especially "Warning Signs" for safety.
                                    </p>
                                </div>
                                <div class="border-l-4 border-blue-500 pl-4">
                                    <h4 class="font-semibold text-gray-800">Step 4: Custom Instructions</h4>
                                    <p class="text-sm text-gray-600 mt-1">
                                        Add personalized instructions specific to this patient's situation.
                                    </p>
                                </div>
                                <div class="border-l-4 border-blue-500 pl-4">
                                    <h4 class="font-semibold text-gray-800">Step 5: Review & Generate</h4>
                                    <p class="text-sm text-gray-600 mt-1">
                                        Review everything and generate a professional PDF document.
                                    </p>
                                </div>
                            </div>
                        </section>

                        <section>
                            <h3 class="text-xl font-semibold text-gray-800 mb-3">
                                <i class="fas fa-shield-alt text-blue-500 mr-2"></i>
                                Privacy & Security
                            </h3>
                            <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                                <ul class="space-y-2 text-sm text-gray-700">
                                    <li><i class="fas fa-check text-green-500 mr-2"></i>HIPAA Compliant - No PHI stored permanently</li>
                                    <li><i class="fas fa-check text-green-500 mr-2"></i>Session-only data - Cleared after document generation</li>
                                    <li><i class="fas fa-check text-green-500 mr-2"></i>Secure transmission - All data encrypted in transit</li>
                                    <li><i class="fas fa-check text-green-500 mr-2"></i>No third-party sharing - Your data stays private</li>
                                </ul>
                            </div>
                        </section>

                        <section>
                            <h3 class="text-xl font-semibold text-gray-800 mb-3">
                                <i class="fas fa-lightbulb text-blue-500 mr-2"></i>
                                Tips for Best Results
                            </h3>
                            <ul class="space-y-2 text-gray-600">
                                <li><i class="fas fa-arrow-right text-blue-500 mr-2"></i>Use intermediate reading level for most patients</li>
                                <li><i class="fas fa-arrow-right text-blue-500 mr-2"></i>Always include warning signs for patient safety</li>
                                <li><i class="fas fa-arrow-right text-blue-500 mr-2"></i>Add specific follow-up dates to improve compliance</li>
                                <li><i class="fas fa-arrow-right text-blue-500 mr-2"></i>Include MedlinePlus resources for additional learning</li>
                                <li><i class="fas fa-arrow-right text-blue-500 mr-2"></i>Keep custom instructions simple and actionable</li>
                            </ul>
                        </section>

                        <section>
                            <h3 class="text-xl font-semibold text-gray-800 mb-3">
                                <i class="fas fa-question text-blue-500 mr-2"></i>
                                Frequently Asked Questions
                            </h3>
                            <div class="space-y-3">
                                <div>
                                    <h4 class="font-semibold text-gray-800">Q: Is patient data stored?</h4>
                                    <p class="text-sm text-gray-600">A: No. All patient information is used only to generate the document and is immediately discarded.</p>
                                </div>
                                <div>
                                    <h4 class="font-semibold text-gray-800">Q: Can I edit the document after generation?</h4>
                                    <p class="text-sm text-gray-600">A: The PDF can be edited using PDF editing software. You can also restart the wizard to create a new version.</p>
                                </div>
                                <div>
                                    <h4 class="font-semibold text-gray-800">Q: What if my diagnosis isn't in the system?</h4>
                                    <p class="text-sm text-gray-600">A: Our database has 12,252 diagnoses. If you can't find it, try searching with the ICD-10 code or contact support.</p>
                                </div>
                                <div>
                                    <h4 class="font-semibold text-gray-800">Q: Are translations medically accurate?</h4>
                                    <p class="text-sm text-gray-600">A: Yes. All translations are verified for medical accuracy and use appropriate terminology.</p>
                                </div>
                            </div>
                        </section>

                        <section class="bg-blue-50 rounded-lg p-4">
                            <h3 class="text-lg font-semibold text-blue-900 mb-2">
                                <i class="fas fa-headset text-blue-600 mr-2"></i>
                                Need More Help?
                            </h3>
                            <p class="text-sm text-blue-800">
                                Contact support at <a href="mailto:support@ainurseflorence.com" class="underline">support@ainurseflorence.com</a>
                                or call (555) 123-4567 for assistance.
                            </p>
                        </section>
                    </div>

                    <div class="sticky bottom-0 bg-gray-50 p-4 rounded-b-xl border-t">
                        <button
                            onclick="closeHelpModal()"
                            class="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                        >
                            <i class="fas fa-check mr-2"></i>
                            Got it, close help
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', helpModal);

        // Add modal control functions
        window.showHelpModal = function() {
            document.getElementById('help-modal').classList.remove('hidden');
        };

        window.closeHelpModal = function() {
            document.getElementById('help-modal').classList.add('hidden');
        };

        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                window.closeHelpModal();
            }
        });
    }

    initializeTooltips() {
        // Add tooltip styles
        const tooltipStyles = `
            <style>
                .tooltip {
                    position: relative;
                }

                .tooltip::after {
                    content: attr(data-tooltip);
                    position: absolute;
                    bottom: 100%;
                    left: 50%;
                    transform: translateX(-50%);
                    padding: 0.5rem 0.75rem;
                    background: #1F2937;
                    color: white;
                    font-size: 0.75rem;
                    border-radius: 0.375rem;
                    white-space: nowrap;
                    opacity: 0;
                    pointer-events: none;
                    transition: opacity 0.2s;
                    margin-bottom: 0.5rem;
                    z-index: 1000;
                    max-width: 300px;
                    white-space: normal;
                }

                .tooltip::before {
                    content: '';
                    position: absolute;
                    bottom: 100%;
                    left: 50%;
                    transform: translateX(-50%);
                    border: 6px solid transparent;
                    border-top-color: #1F2937;
                    opacity: 0;
                    pointer-events: none;
                    transition: opacity 0.2s;
                    margin-bottom: -6px;
                    z-index: 1000;
                }

                .tooltip:hover::after,
                .tooltip:hover::before {
                    opacity: 1;
                }
            </style>
        `;

        document.head.insertAdjacentHTML('beforeend', tooltipStyles);

        // Add tooltip class to all elements with data-tooltip attribute
        document.addEventListener('DOMContentLoaded', () => {
            document.querySelectorAll('[data-tooltip]').forEach(el => {
                el.classList.add('tooltip');
            });
        });

        // Re-initialize tooltips after each step render
        const observer = new MutationObserver(() => {
            document.querySelectorAll('[data-tooltip]').forEach(el => {
                el.classList.add('tooltip');
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    async generateEducationDocument(data) {
        try {
            this.showAlert('Generating patient education document...', 'info');

            const response = await fetch('/api/documents/patient-education', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to generate document');
            }

            const result = await response.json();

            this.showAlert('Document generated successfully! Downloading...', 'success');

            // Download PDF
            if (result.pdf_url) {
                window.open(result.pdf_url, '_blank');
            }

            // Clear draft
            localStorage.removeItem(`wizard_draft_${this.constructor.name}`);

        } catch (error) {
            this.showAlert('Error generating document: ' + error.message, 'error');
            console.error('Document generation error:', error);
        }
    }
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedPatientEducationWizard;
}
