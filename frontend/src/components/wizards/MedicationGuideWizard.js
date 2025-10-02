/**
 * Medication Guide Wizard
 * Create comprehensive patient medication guides
 * Integrates with RxNorm-coded medication library
 */

class MedicationGuideWizard extends BaseWizard {
    constructor(containerId, config = {}) {
        const defaultSteps = [
            {
                title: 'Medication Selection',
                description: 'Select medication and basic information',
                render: (data) => this.renderMedicationStep(data)
            },
            {
                title: 'Dosage & Instructions',
                description: 'Dosing information and how to take',
                render: (data) => this.renderDosageStep(data)
            },
            {
                title: 'Side Effects & Warnings',
                description: 'Common and serious side effects',
                render: (data) => this.renderSideEffectsStep(data)
            },
            {
                title: 'Interactions & Storage',
                description: 'Drug and food interactions, storage',
                render: (data) => this.renderInteractionsStep(data)
            },
            {
                title: 'Review & Export',
                description: 'Review and generate medication guide',
                render: (data) => this.renderReviewStep(data)
            }
        ];

        super(containerId, {
            ...config,
            steps: config.steps || defaultSteps
        });

        this.medicationData = null;
    }

    renderMedicationStep(data) {
        return `
            <div class="space-y-4">
                <!-- Medication Search -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Search Medication <span class="text-red-500">*</span>
                    </label>
                    <input type="text" id="medication-search"
                        class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="Search by medication name..."
                        value="${data.medication_search || ''}">
                    <div id="medication-results" class="mt-2 max-h-60 overflow-y-auto"></div>
                </div>

                <!-- Selected Medication -->
                <div id="selected-medication" class="hidden bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div class="flex justify-between items-start">
                        <div>
                            <h4 class="font-bold text-blue-900" id="medication-display"></h4>
                            <p class="text-sm text-blue-700" id="medication-generic"></p>
                            <p class="text-xs text-blue-600 mt-1" id="medication-rxnorm"></p>
                        </div>
                        <button id="clear-medication" class="text-red-600 hover:text-red-800">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>

                <!-- Purpose -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Why is patient taking this medication? <span class="text-red-500">*</span>
                    </label>
                    <textarea id="medication-purpose" rows="2" required
                        class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., To control your blood sugar levels">${data.purpose || ''}</textarea>
                </div>

                <!-- How it Works (Optional) -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        How it works (Simple explanation - Optional)
                    </label>
                    <textarea id="medication-how-works" rows="2"
                        class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., This medicine helps your body use insulin better">${data.how_it_works || ''}</textarea>
                </div>

                <!-- Language & Reading Level -->
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Reading Level</label>
                        <select id="reading-level" class="w-full p-3 border border-gray-300 rounded-lg">
                            <option value="basic">Basic (4th-6th grade)</option>
                            <option value="intermediate" selected>Intermediate (7th-9th grade)</option>
                            <option value="advanced">Advanced (10th+ grade)</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Language</label>
                        <select id="language" class="w-full p-3 border border-gray-300 rounded-lg">
                            <option value="en">English</option>
                            <option value="es">Spanish</option>
                            <option value="zh-CN">Chinese (Simplified)</option>
                            <option value="zh-TW">Chinese (Traditional)</option>
                        </select>
                    </div>
                </div>
            </div>
        `;
    }

    renderDosageStep(data) {
        return `
            <div class="space-y-4">
                <!-- Dosage -->
                <div class="grid grid-cols-3 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Dose Amount <span class="text-red-500">*</span>
                        </label>
                        <input type="text" id="dosage-amount" required
                            class="w-full p-3 border border-gray-300 rounded-lg"
                            placeholder="e.g., 500"
                            value="${data.dosage_amount || ''}">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Unit <span class="text-red-500">*</span>
                        </label>
                        <select id="dosage-unit" required class="w-full p-3 border border-gray-300 rounded-lg">
                            <option value="">Select unit</option>
                            <option value="mg">mg (milligrams)</option>
                            <option value="mcg">mcg (micrograms)</option>
                            <option value="g">g (grams)</option>
                            <option value="mL">mL (milliliters)</option>
                            <option value="units">units</option>
                            <option value="tablets">tablet(s)</option>
                            <option value="capsules">capsule(s)</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Route
                        </label>
                        <select id="route" class="w-full p-3 border border-gray-300 rounded-lg">
                            <option value="oral" selected>By mouth (oral)</option>
                            <option value="injection">Injection</option>
                            <option value="topical">Topical (on skin)</option>
                            <option value="inhaled">Inhaled</option>
                            <option value="rectal">Rectal</option>
                            <option value="sublingual">Under tongue</option>
                        </select>
                    </div>
                </div>

                <!-- Frequency -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        How often to take <span class="text-red-500">*</span>
                    </label>
                    <select id="frequency" required class="w-full p-3 border border-gray-300 rounded-lg">
                        <option value="">Select frequency</option>
                        <option value="QD|Once daily">Once daily</option>
                        <option value="BID|Twice daily">Twice daily</option>
                        <option value="TID|Three times daily">Three times daily</option>
                        <option value="QID|Four times daily">Four times daily</option>
                        <option value="Q4H|Every 4 hours">Every 4 hours</option>
                        <option value="Q6H|Every 6 hours">Every 6 hours</option>
                        <option value="Q8H|Every 8 hours">Every 8 hours</option>
                        <option value="Q12H|Every 12 hours">Every 12 hours</option>
                        <option value="PRN|As needed">As needed</option>
                        <option value="QHS|At bedtime">At bedtime</option>
                        <option value="QAM|In the morning">In the morning</option>
                    </select>
                </div>

                <!-- Special Instructions -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Special Instructions
                    </label>
                    <div id="special-instructions-list" class="space-y-2 mb-3">
                        ${(data.special_instructions || []).map((instruction, idx) => `
                            <div class="flex items-center space-x-2 bg-gray-50 p-3 rounded">
                                <input type="checkbox" checked class="text-blue-600">
                                <input type="text" value="${instruction}"
                                    class="flex-1 bg-transparent border-none focus:outline-none"
                                    onchange="updateInstruction(${idx}, this.value)">
                                <button class="text-red-600 hover:text-red-800" onclick="removeInstruction(${idx})">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                    <button id="add-instruction-btn" class="text-blue-600 hover:text-blue-800 text-sm">
                        <i class="fas fa-plus mr-1"></i>Add Instruction
                    </button>

                    <!-- Common Instructions -->
                    <div class="mt-3">
                        <label class="text-xs text-gray-600">Quick Add:</label>
                        <div class="flex flex-wrap gap-2 mt-1">
                            ${['Take with food', 'Take on empty stomach', 'Take with full glass of water',
                                'Do not crush or chew', 'Avoid alcohol', 'Take at same time each day'].map(instr => `
                                <button class="px-2 py-1 bg-blue-50 text-xs rounded hover:bg-blue-100"
                                    onclick="addInstruction('${instr}')">
                                    + ${instr}
                                </button>
                            `).join('')}
                        </div>
                    </div>
                </div>

                <!-- Missed Dose -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        What to do if dose is missed
                    </label>
                    <textarea id="missed-dose" rows="2"
                        class="w-full p-3 border border-gray-300 rounded-lg"
                        placeholder="e.g., Take as soon as you remember. If almost time for next dose, skip missed dose.">${data.missed_dose || 'Take as soon as you remember. If it\'s almost time for the next dose, skip the missed dose. Do not double the dose.'}</textarea>
                </div>
            </div>
        `;
    }

    renderSideEffectsStep(data) {
        return `
            <div class="space-y-6">
                <!-- Common Side Effects -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Common Side Effects (Usually mild and temporary)
                    </label>
                    <p class="text-sm text-gray-600 mb-3">
                        Side effects that usually don't require calling doctor unless severe
                    </p>
                    <div id="common-side-effects-list" class="space-y-2 mb-3">
                        ${(data.common_side_effects || this.medicationData?.common_side_effects || []).map((effect, idx) => `
                            <div class="flex items-center space-x-2 bg-yellow-50 border border-yellow-200 p-3 rounded">
                                <i class="fas fa-info-circle text-yellow-600"></i>
                                <input type="text" value="${effect}"
                                    class="flex-1 bg-transparent border-none focus:outline-none"
                                    onchange="updateCommonSideEffect(${idx}, this.value)">
                                <button class="text-red-600 hover:text-red-800" onclick="removeCommonSideEffect(${idx})">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                    <button id="add-common-side-effect-btn" class="text-blue-600 hover:text-blue-800 text-sm">
                        <i class="fas fa-plus mr-1"></i>Add Common Side Effect
                    </button>
                </div>

                <!-- Serious Side Effects -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Serious Side Effects (Call doctor immediately) <span class="text-red-500">*</span>
                    </label>
                    <p class="text-sm text-gray-600 mb-3">
                        Side effects that require immediate medical attention
                    </p>
                    <div id="serious-side-effects-list" class="space-y-2 mb-3">
                        ${(data.serious_side_effects || this.medicationData?.serious_warnings || []).map((effect, idx) => `
                            <div class="flex items-center space-x-2 bg-red-50 border border-red-200 p-3 rounded">
                                <i class="fas fa-exclamation-triangle text-red-600"></i>
                                <input type="text" value="${effect}"
                                    class="flex-1 bg-transparent border-none focus:outline-none"
                                    onchange="updateSeriousSideEffect(${idx}, this.value)">
                                <button class="text-red-600 hover:text-red-800" onclick="removeSeriousSideEffect(${idx})">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                    <button id="add-serious-side-effect-btn" class="text-blue-600 hover:text-blue-800 text-sm">
                        <i class="fas fa-plus mr-1"></i>Add Serious Side Effect
                    </button>
                </div>
            </div>
        `;
    }

    renderInteractionsStep(data) {
        return `
            <div class="space-y-6">
                <!-- Food Interactions -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Food & Drink to Avoid
                    </label>
                    <div id="food-interactions-list" class="space-y-2 mb-3">
                        ${(data.food_interactions || this.medicationData?.food_interactions || []).map((interaction, idx) => `
                            <div class="flex items-center space-x-2 bg-gray-50 p-3 rounded">
                                <i class="fas fa-utensils text-orange-600"></i>
                                <input type="text" value="${interaction}"
                                    class="flex-1 bg-transparent border-none focus:outline-none"
                                    onchange="updateFoodInteraction(${idx}, this.value)">
                                <button class="text-red-600 hover:text-red-800" onclick="removeFoodInteraction(${idx})">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                    <button id="add-food-interaction-btn" class="text-blue-600 hover:text-blue-800 text-sm">
                        <i class="fas fa-plus mr-1"></i>Add Food/Drink to Avoid
                    </button>
                </div>

                <!-- Drug Interactions -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Medications that may Interact
                    </label>
                    <p class="text-sm text-gray-600 mb-3">
                        Tell your doctor about all medications you're taking
                    </p>
                    <div id="drug-interactions-list" class="space-y-2 mb-3">
                        ${(data.drug_interactions || this.medicationData?.drug_interactions || []).map((interaction, idx) => `
                            <div class="flex items-center space-x-2 bg-gray-50 p-3 rounded">
                                <i class="fas fa-pills text-purple-600"></i>
                                <input type="text" value="${interaction}"
                                    class="flex-1 bg-transparent border-none focus:outline-none"
                                    onchange="updateDrugInteraction(${idx}, this.value)">
                                <button class="text-red-600 hover:text-red-800" onclick="removeDrugInteraction(${idx})">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                    <button id="add-drug-interaction-btn" class="text-blue-600 hover:text-blue-800 text-sm">
                        <i class="fas fa-plus mr-1"></i>Add Drug Interaction
                    </button>
                </div>

                <!-- Storage Instructions -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        How to Store
                    </label>
                    <textarea id="storage-instructions" rows="2"
                        class="w-full p-3 border border-gray-300 rounded-lg">${data.storage_instructions || this.medicationData?.storage_instructions || 'Store at room temperature away from moisture and heat. Keep out of reach of children.'}</textarea>
                </div>
            </div>
        `;
    }

    renderReviewStep(data) {
        return `
            <div class="space-y-6">
                <div class="bg-gradient-to-r from-green-50 to-green-100 border border-green-200 rounded-lg p-6">
                    <h4 class="text-lg font-bold text-green-900 mb-2">
                        <i class="fas fa-file-prescription mr-2"></i>Medication Guide Ready
                    </h4>
                    <p class="text-green-800">
                        Review the summary and choose export format.
                    </p>
                </div>

                <!-- Summary -->
                <div class="bg-white border border-gray-200 rounded-lg p-6 space-y-3">
                    <div>
                        <h5 class="font-bold text-gray-700 mb-1">Medication</h5>
                        <p class="text-gray-900 font-semibold">${data.medication_display || 'Not selected'}</p>
                        <p class="text-sm text-gray-600">${data.dosage_amount} ${data.dosage_unit} - ${data.frequency_display || ''}</p>
                    </div>

                    <div class="grid grid-cols-2 gap-4 pt-3 border-t">
                        <div>
                            <p class="text-xs text-gray-600">Common Side Effects</p>
                            <p class="font-semibold text-gray-900">${(data.common_side_effects || []).length} listed</p>
                        </div>
                        <div>
                            <p class="text-xs text-gray-600">Serious Warnings</p>
                            <p class="font-semibold text-gray-900">${(data.serious_side_effects || []).length} listed</p>
                        </div>
                    </div>
                </div>

                <!-- Export Format -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-3">
                        Export Format <span class="text-red-500">*</span>
                    </label>
                    <div class="grid grid-cols-3 gap-4">
                        <label class="export-option-card">
                            <input type="radio" name="export_format" value="pdf" checked class="hidden">
                            <div class="border-2 border-gray-200 rounded-lg p-4 cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-all text-center">
                                <i class="fas fa-file-pdf text-3xl text-red-600 mb-2"></i>
                                <h6 class="font-bold">PDF</h6>
                                <p class="text-xs text-gray-600">Print-ready</p>
                            </div>
                        </label>

                        <label class="export-option-card">
                            <input type="radio" name="export_format" value="docx" class="hidden">
                            <div class="border-2 border-gray-200 rounded-lg p-4 cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-all text-center">
                                <i class="fas fa-file-word text-3xl text-blue-600 mb-2"></i>
                                <h6 class="font-bold">Word</h6>
                                <p class="text-xs text-gray-600">Editable</p>
                            </div>
                        </label>

                        <label class="export-option-card">
                            <input type="radio" name="export_format" value="text" class="hidden">
                            <div class="border-2 border-gray-200 rounded-lg p-4 cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-all text-center">
                                <i class="fas fa-file-alt text-3xl text-gray-600 mb-2"></i>
                                <h6 class="font-bold">Text</h6>
                                <p class="text-xs text-gray-600">Simple</p>
                            </div>
                        </label>
                    </div>
                </div>

                <!-- Privacy Notice -->
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p class="text-sm text-blue-800">
                        <i class="fas fa-info-circle mr-2"></i>
                        This medication guide is for patient education. Not medical advice.
                    </p>
                </div>
            </div>
        `;
    }

    getTitle() {
        return 'Medication Guide Wizard';
    }

    getDescription() {
        return 'Create comprehensive patient medication guides with safety information.';
    }

    async complete() {
        this.collectStepData();
        this.showAlert('Generating medication guide...', 'info');

        try {
            const request = {
                medication_name: this.data.medication_display,
                dosage: `${this.data.dosage_amount} ${this.data.dosage_unit}`,
                frequency: this.data.frequency_display,
                route: this.data.route || 'oral',
                special_instructions: this.data.special_instructions || [],
                purpose: this.data.purpose,
                how_it_works: this.data.how_it_works,
                common_side_effects: this.data.common_side_effects || [],
                serious_side_effects: this.data.serious_side_effects || [],
                food_interactions: this.data.food_interactions || [],
                drug_interactions: this.data.drug_interactions || [],
                storage_instructions: this.data.storage_instructions,
                missed_dose_instructions: this.data.missed_dose,
                language: this.data.language,
                reading_level: this.data.reading_level,
                format: this.data.export_format || 'pdf'
            };

            const response = await fetch('/api/v1/patient-documents/medication-guide', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(request)
            });

            if (!response.ok) throw new Error('Failed to generate document');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `medication_guide_${this.data.medication_display}_${Date.now()}.${request.format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();

            this.showAlert('Medication guide generated successfully!', 'success');
            localStorage.removeItem(`wizard_draft_${this.constructor.name}`);

            if (this.onComplete) {
                this.onComplete(this.data);
            }

        } catch (error) {
            console.error('Error:', error);
            this.showAlert('Error generating medication guide. Please try again.', 'error');
        }
    }
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MedicationGuideWizard;
}
