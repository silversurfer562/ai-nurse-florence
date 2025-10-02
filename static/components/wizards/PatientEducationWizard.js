/**
 * Patient Education Wizard
 *
 * Comprehensive wizard for creating patient-friendly education materials that:
 * - Use Grade 6-8 reading level descriptions
 * - Include MedlinePlus educational resources
 * - Support multiple languages (English, Spanish, Chinese)
 * - Generate FHIR-ready documents with proper coding
 * - Check billing code validity
 */

class PatientEducationWizard extends BaseWizard {
    constructor(containerId) {
        super(containerId, {
            steps: [
                {
                    title: 'Patient Info',
                    description: 'Basic patient information for personalization.',
                    fields: [
                        {
                            id: 'patient_name',
                            type: 'text',
                            label: 'Patient Name',
                            placeholder: 'Enter patient name',
                            required: true,
                            help: 'Used for document header only - no PHI stored.'
                        },
                        {
                            id: 'preferred_language',
                            type: 'select',
                            label: 'Preferred Language',
                            required: true,
                            options: [
                                { value: 'en', label: 'English' },
                                { value: 'es', label: 'Spanish (Español)' },
                                { value: 'zh', label: 'Chinese (中文)' },
                                { value: 'fr', label: 'French (Français)' },
                                { value: 'de', label: 'German (Deutsch)' },
                                { value: 'pt', label: 'Portuguese (Português)' },
                                { value: 'ar', label: 'Arabic (العربية)' },
                                { value: 'hi', label: 'Hindi (हिन्दी)' },
                                { value: 'ru', label: 'Russian (Русский)' },
                                { value: 'ja', label: 'Japanese (日本語)' },
                                { value: 'ko', label: 'Korean (한국어)' },
                                { value: 'vi', label: 'Vietnamese (Tiếng Việt)' },
                                { value: 'tl', label: 'Tagalog (Filipino)' },
                                { value: 'it', label: 'Italian (Italiano)' },
                                { value: 'pl', label: 'Polish (Polski)' }
                            ],
                            help: 'Educational materials will be provided in this language.'
                        },
                        {
                            id: 'reading_level',
                            type: 'select',
                            label: 'Reading Level',
                            required: true,
                            options: [
                                { value: 'basic', label: 'Basic (Grade 3-5)' },
                                { value: 'intermediate', label: 'Intermediate (Grade 6-8) - Recommended' },
                                { value: 'advanced', label: 'Advanced (Grade 9+)' }
                            ],
                            help: 'Most patients benefit from intermediate level.'
                        }
                    ]
                },
                {
                    title: 'Diagnosis',
                    description: 'Select the condition to explain to the patient.',
                    render: (data) => this.renderDiagnosisStep(data)
                },
                {
                    title: 'What to Include',
                    description: 'Choose what information to include.',
                    render: (data) => this.renderContentSelectionStep(data)
                },
                {
                    title: 'Custom Instructions',
                    description: 'Add personalized instructions for this patient.',
                    fields: [
                        {
                            id: 'custom_instructions',
                            type: 'textarea',
                            label: 'Additional Instructions (Optional)',
                            placeholder: 'e.g., "Check your blood sugar before meals and at bedtime"',
                            rows: 4,
                            help: 'Any special instructions specific to this patient.'
                        },
                        {
                            id: 'follow_up_date',
                            type: 'date',
                            label: 'Follow-up Appointment Date',
                            help: 'Select the date for the patient\'s follow-up appointment.'
                        }
                    ]
                },
                {
                    title: 'Review & Generate',
                    description: 'Review your selections and generate the document.',
                    render: (data) => this.renderReviewStep(data)
                }
            ],
            onComplete: (data) => this.generateEducationDocument(data)
        });
    }

    getTitle() {
        return 'Patient Education Document';
    }

    getDescription() {
        return 'Create easy-to-understand education materials for your patient.';
    }

    renderDiagnosisStep(data) {
        return `
            <div class="diagnosis-selection">
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Search for Diagnosis <span class="text-red-500">*</span>
                    </label>
                    <input
                        type="text"
                        id="diagnosis_search"
                        class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="Type to search (e.g., diabetes, hypertension, asthma)..."
                        autocomplete="off"
                    >
                    <p class="text-sm text-gray-500 mt-1">
                        Search by name, ICD-10 code, or common terms
                    </p>
                </div>

                <div id="diagnosis_results" class="space-y-2 max-h-96 overflow-y-auto">
                    <!-- Search results will appear here -->
                    <div class="text-gray-500 text-center py-8">
                        <i class="fas fa-search text-4xl mb-3"></i>
                        <p>Start typing to search for a diagnosis</p>
                    </div>
                </div>

                <div id="selected_diagnosis" class="mt-4 hidden">
                    <div class="bg-green-50 border-l-4 border-green-500 p-4 rounded">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="font-medium text-green-800" id="selected_diagnosis_name"></p>
                                <p class="text-sm text-green-600 mt-1" id="selected_diagnosis_codes"></p>
                            </div>
                            <button onclick="clearDiagnosisSelection()" class="text-green-600 hover:text-green-800">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <input type="hidden" id="selected_diagnosis_id" name="diagnosis_id" required>
                <input type="hidden" id="selected_icd10_code" name="icd10_code">
                <input type="hidden" id="selected_snomed_code" name="snomed_code">
            </div>

            <script>
                // Diagnosis search functionality
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
                            <p class="text-gray-600 mt-2">Searching...</p>
                        </div>
                    \`;

                    searchTimeout = setTimeout(async () => {
                        try {
                            const response = await fetch(\`/api/v1/content-settings/diagnosis/search?q=\${encodeURIComponent(query)}&limit=20\`);

                            if (!response.ok) {
                                throw new Error(\`HTTP error! status: \${response.status}\`);
                            }

                            const data = await response.json();

                            if (Array.isArray(data) && data.length > 0) {
                                resultsContainer.innerHTML = data.map(diagnosis => \`
                                    <div class="diagnosis-result p-4 border border-gray-200 rounded-lg hover:bg-blue-50 cursor-pointer transition-colors"
                                         onclick="selectDiagnosis('\${diagnosis.id}', '\${diagnosis.diagnosis_display}', '\${diagnosis.icd10_code}', '\${diagnosis.snomed_code || ''}')">
                                        <div class="flex justify-between items-start">
                                            <div class="flex-1">
                                                <p class="font-medium text-gray-900">\${diagnosis.diagnosis_display}</p>
                                                <p class="text-sm text-gray-600 mt-1">
                                                    ICD-10: <span class="font-mono">\${diagnosis.icd10_code}</span>
                                                    \${diagnosis.snomed_code ? \` | SNOMED: <span class="font-mono">\${diagnosis.snomed_code}</span>\` : ''}
                                                </p>
                                                \${diagnosis.patient_friendly_description ? \`
                                                    <p class="text-sm text-gray-500 mt-2 italic">
                                                        <i class="fas fa-info-circle mr-1"></i>
                                                        \${diagnosis.patient_friendly_description.substring(0, 120)}...
                                                    </p>
                                                \` : ''}
                                            </div>
                                            <div class="ml-4">
                                                \${diagnosis.is_billable === false ? \`
                                                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-red-100 text-red-800">
                                                        <i class="fas fa-exclamation-triangle mr-1"></i>
                                                        Not Billable
                                                    </span>
                                                \` : diagnosis.billable_note ? \`
                                                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-yellow-100 text-yellow-800">
                                                        <i class="fas fa-exclamation-circle mr-1"></i>
                                                        Verify
                                                    </span>
                                                \` : \`
                                                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                                                        <i class="fas fa-check mr-1"></i>
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
                                        <p class="text-gray-600">No diagnoses found</p>
                                        <p class="text-sm text-gray-500 mt-2">Try different search terms or check spelling</p>
                                    </div>
                                \`;
                            }
                        } catch (error) {
                            console.error('Diagnosis search error:', error);
                            resultsContainer.innerHTML = \`
                                <div class="text-center py-8">
                                    <i class="fas fa-exclamation-triangle text-4xl text-red-400 mb-3"></i>
                                    <p class="text-red-600">Error searching diagnoses</p>
                                    <p class="text-sm text-gray-500 mt-2">\${error.message}</p>
                                    <p class="text-xs text-gray-400 mt-1">Check browser console for details</p>
                                </div>
                            \`;
                        }
                    }, 300);
                });

                window.selectDiagnosis = function(id, name, icd10, snomed) {
                    document.getElementById('selected_diagnosis_id').value = id;
                    document.getElementById('selected_icd10_code').value = icd10;
                    document.getElementById('selected_snomed_code').value = snomed || '';

                    document.getElementById('selected_diagnosis_name').textContent = name;
                    document.getElementById('selected_diagnosis_codes').textContent =
                        \`ICD-10: \${icd10}\${snomed ? \` | SNOMED: \${snomed}\` : ''}\`;

                    selectedDiagnosisDiv.classList.remove('hidden');
                    diagnosisSearch.value = '';
                    resultsContainer.innerHTML = \`
                        <div class="text-green-600 text-center py-4">
                            <i class="fas fa-check-circle text-4xl mb-3"></i>
                            <p>Diagnosis selected!</p>
                        </div>
                    \`;
                };

                window.clearDiagnosisSelection = function() {
                    document.getElementById('selected_diagnosis_id').value = '';
                    document.getElementById('selected_icd10_code').value = '';
                    document.getElementById('selected_snomed_code').value = '';
                    selectedDiagnosisDiv.classList.add('hidden');
                    diagnosisSearch.value = '';
                    resultsContainer.innerHTML = \`
                        <div class="text-gray-500 text-center py-8">
                            <i class="fas fa-search text-4xl mb-3"></i>
                            <p>Start typing to search for a diagnosis</p>
                        </div>
                    \`;
                };
            </script>
        `;
    }

    renderContentSelectionStep(data) {
        return `
            <div class="content-selection space-y-4">
                <p class="text-gray-600 mb-4">
                    Select what information to include in the patient education document.
                </p>

                <label class="flex items-start p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input type="checkbox" name="include_description" value="true" checked class="mt-1 mr-3">
                    <div>
                        <p class="font-medium text-gray-900">Condition Description</p>
                        <p class="text-sm text-gray-600 mt-1">Easy-to-understand explanation of the condition.</p>
                    </div>
                </label>

                <label class="flex items-start p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input type="checkbox" name="include_warning_signs" value="true" checked class="mt-1 mr-3">
                    <div>
                        <p class="font-medium text-gray-900">Warning Signs</p>
                        <p class="text-sm text-gray-600 mt-1">When to seek immediate medical attention.</p>
                    </div>
                </label>

                <label class="flex items-start p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input type="checkbox" name="include_medications" value="true" checked class="mt-1 mr-3">
                    <div>
                        <p class="font-medium text-gray-900">Medication Information</p>
                        <p class="text-sm text-gray-600 mt-1">Standard medications and instructions.</p>
                    </div>
                </label>

                <label class="flex items-start p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input type="checkbox" name="include_diet" value="true" checked class="mt-1 mr-3">
                    <div>
                        <p class="font-medium text-gray-900">Diet & Lifestyle</p>
                        <p class="text-sm text-gray-600 mt-1">Dietary recommendations and lifestyle changes.</p>
                    </div>
                </label>

                <label class="flex items-start p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input type="checkbox" name="include_medlineplus" value="true" checked class="mt-1 mr-3">
                    <div>
                        <p class="font-medium text-gray-900">Educational Resources</p>
                        <p class="text-sm text-gray-600 mt-1">Links to MedlinePlus and other trusted sources.</p>
                    </div>
                </label>

                <label class="flex items-start p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input type="checkbox" name="include_follow_up" value="true" checked class="mt-1 mr-3">
                    <div>
                        <p class="font-medium text-gray-900">Follow-up Instructions</p>
                        <p class="text-sm text-gray-600 mt-1">When and how to follow up with healthcare provider.</p>
                    </div>
                </label>
            </div>
        `;
    }

    renderReviewStep(data) {
        return `
            <div class="review-summary space-y-6">
                <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
                    <div class="flex">
                        <i class="fas fa-info-circle text-blue-500 mt-1 mr-3"></i>
                        <div>
                            <p class="font-medium text-blue-800">Document Preview</p>
                            <p class="text-sm text-blue-700 mt-1">
                                Review the information below before generating the document.
                            </p>
                        </div>
                    </div>
                </div>

                <div>
                    <h3 class="text-lg font-semibold text-gray-800 mb-3">Patient Information</h3>
                    <dl class="grid grid-cols-2 gap-4">
                        <div>
                            <dt class="text-sm font-medium text-gray-500">Patient Name</dt>
                            <dd class="mt-1 text-sm text-gray-900">${data.patient_name || 'Not specified'}</dd>
                        </div>
                        <div>
                            <dt class="text-sm font-medium text-gray-500">Language</dt>
                            <dd class="mt-1 text-sm text-gray-900">
                                ${data.preferred_language === 'en' ? 'English' :
                                  data.preferred_language === 'es' ? 'Spanish' :
                                  data.preferred_language === 'zh' ? 'Chinese' : 'English'}
                            </dd>
                        </div>
                        <div>
                            <dt class="text-sm font-medium text-gray-500">Reading Level</dt>
                            <dd class="mt-1 text-sm text-gray-900">
                                ${data.reading_level === 'basic' ? 'Basic (Grade 3-5)' :
                                  data.reading_level === 'intermediate' ? 'Intermediate (Grade 6-8)' :
                                  'Advanced (Grade 9+)'}
                            </dd>
                        </div>
                        <div>
                            <dt class="text-sm font-medium text-gray-500">Follow-up</dt>
                            <dd class="mt-1 text-sm text-gray-900">${data.follow_up_date || 'Not specified'}</dd>
                        </div>
                    </dl>
                </div>

                <div>
                    <h3 class="text-lg font-semibold text-gray-800 mb-3">Diagnosis</h3>
                    <div class="bg-gray-50 p-4 rounded-lg">
                        <p class="font-medium text-gray-900" id="review_diagnosis_name">Loading...</p>
                        <p class="text-sm text-gray-600 mt-1" id="review_diagnosis_codes">Loading...</p>
                    </div>
                </div>

                <div>
                    <h3 class="text-lg font-semibold text-gray-800 mb-3">Content Included</h3>
                    <div class="space-y-2">
                        ${data.include_description ? '<div class="flex items-center text-sm text-gray-700"><i class="fas fa-check text-green-500 mr-2"></i> Condition Description</div>' : ''}
                        ${data.include_warning_signs ? '<div class="flex items-center text-sm text-gray-700"><i class="fas fa-check text-green-500 mr-2"></i> Warning Signs</div>' : ''}
                        ${data.include_medications ? '<div class="flex items-center text-sm text-gray-700"><i class="fas fa-check text-green-500 mr-2"></i> Medication Information</div>' : ''}
                        ${data.include_diet ? '<div class="flex items-center text-sm text-gray-700"><i class="fas fa-check text-green-500 mr-2"></i> Diet & Lifestyle</div>' : ''}
                        ${data.include_medlineplus ? '<div class="flex items-center text-sm text-gray-700"><i class="fas fa-check text-green-500 mr-2"></i> Educational Resources</div>' : ''}
                        ${data.include_follow_up ? '<div class="flex items-center text-sm text-gray-700"><i class="fas fa-check text-green-500 mr-2"></i> Follow-up Instructions</div>' : ''}
                    </div>
                </div>

                ${data.custom_instructions ? `
                    <div>
                        <h3 class="text-lg font-semibold text-gray-800 mb-3">Custom Instructions</h3>
                        <div class="bg-yellow-50 p-4 rounded-lg">
                            <p class="text-sm text-gray-700">${data.custom_instructions}</p>
                        </div>
                    </div>
                ` : ''}
            </div>

            <script>
                // Load diagnosis details for review
                (async function() {
                    const diagnosisId = '${data.diagnosis_id || ''}';
                    if (diagnosisId) {
                        try {
                            const response = await fetch(\`/api/diagnosis/\${diagnosisId}\`);
                            const diagnosis = await response.json();

                            document.getElementById('review_diagnosis_name').textContent = diagnosis.diagnosis_display;
                            document.getElementById('review_diagnosis_codes').textContent =
                                \`ICD-10: \${diagnosis.icd10_code}\${diagnosis.snomed_code ? \` | SNOMED: \${diagnosis.snomed_code}\` : ''}\`;
                        } catch (error) {
                            console.error('Error loading diagnosis:', error);
                        }
                    }
                })();
            </script>
        `;
    }

    async generateEducationDocument(data) {
        try {
            // Show loading state
            this.showAlert('Generating patient education document...', 'info');

            // Call API to generate document
            const response = await fetch('/api/v1/documents/patient-education', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error('Failed to generate document');
            }

            const result = await response.json();

            // Show success and download options
            this.showAlert('Document generated successfully!', 'success');

            // Redirect to document view or download
            if (result.document_url) {
                window.location.href = result.document_url;
            } else if (result.pdf_url) {
                window.open(result.pdf_url, '_blank');
            }

        } catch (error) {
            this.showAlert('Error generating document: ' + error.message, 'error');
            console.error('Document generation error:', error);
        }
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PatientEducationWizard;
}
