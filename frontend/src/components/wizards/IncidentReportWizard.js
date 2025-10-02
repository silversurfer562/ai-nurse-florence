/**
 * Incident Report Wizard
 * Legal documentation for incidents and adverse events
 * Immutable after submission with digital signature
 */

class IncidentReportWizard extends BaseWizard {
    constructor(containerId, config = {}) {
        const defaultSteps = [
            {
                title: 'Incident Details',
                description: 'When, where, and what type of incident',
                render: (data) => this.renderIncidentDetailsStep(data)
            },
            {
                title: 'Factual Description',
                description: 'Objective description of what happened',
                render: (data) => this.renderDescriptionStep(data)
            },
            {
                title: 'Immediate Actions',
                description: 'Actions taken and notifications made',
                render: (data) => this.renderActionsStep(data)
            },
            {
                title: 'Witnesses',
                description: 'Staff witnesses to the incident',
                render: (data) => this.renderWitnessesStep(data)
            },
            {
                title: 'Review & Sign',
                description: 'Review and digitally sign report',
                render: (data) => this.renderReviewStep(data)
            }
        ];

        super(containerId, {
            ...config,
            steps: config.steps || defaultSteps
        });
    }

    renderIncidentDetailsStep(data) {
        return `
            <div class="space-y-4">
                <!-- Legal Notice -->
                <div class="bg-amber-50 border-l-4 border-amber-500 p-4">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <i class="fas fa-exclamation-triangle text-amber-500"></i>
                        </div>
                        <div class="ml-3">
                            <h3 class="text-sm font-medium text-amber-800">Legal Documentation</h3>
                            <div class="mt-2 text-sm text-amber-700">
                                <p>This is a legal document. Be factual and objective. Do NOT include:</p>
                                <ul class="list-disc ml-5 mt-1">
                                    <li>Opinions or blame</li>
                                    <li>Speculation about causes</li>
                                    <li>Patient names (use "the patient" or MRN only)</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Incident Type -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Incident Type <span class="text-red-500">*</span>
                    </label>
                    <select id="incident-type" required class="w-full p-3 border border-gray-300 rounded-lg">
                        <option value="">Select incident type</option>
                        <option value="fall">Patient Fall</option>
                        <option value="medication_error">Medication Error</option>
                        <option value="treatment_injury">Treatment-Related Injury</option>
                        <option value="equipment_failure">Equipment Failure</option>
                        <option value="adverse_reaction">Adverse Drug Reaction</option>
                        <option value="patient_safety">Other Patient Safety Event</option>
                        <option value="staff_injury">Staff Injury</option>
                        <option value="visitor_incident">Visitor Incident</option>
                        <option value="property_damage">Property Damage</option>
                        <option value="security">Security Issue</option>
                        <option value="elopement">Patient Elopement</option>
                        <option value="other">Other</option>
                    </select>
                </div>

                <!-- Date and Time -->
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Incident Date <span class="text-red-500">*</span>
                        </label>
                        <input type="date" id="incident-date" required
                            class="w-full p-3 border border-gray-300 rounded-lg"
                            value="${data.incident_date || new Date().toISOString().split('T')[0]}">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Incident Time <span class="text-red-500">*</span>
                        </label>
                        <input type="time" id="incident-time" required
                            class="w-full p-3 border border-gray-300 rounded-lg"
                            value="${data.incident_time || ''}">
                    </div>
                </div>

                <!-- Location -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Location <span class="text-red-500">*</span>
                    </label>
                    <div class="grid grid-cols-2 gap-4">
                        <select id="location-unit" required class="p-3 border border-gray-300 rounded-lg">
                            <option value="">Select unit/department</option>
                            <option value="emergency_department">Emergency Department</option>
                            <option value="icu">ICU</option>
                            <option value="medical_surgical">Medical-Surgical</option>
                            <option value="pediatrics">Pediatrics</option>
                            <option value="labor_delivery">Labor & Delivery</option>
                            <option value="operating_room">Operating Room</option>
                            <option value="recovery">Post-Anesthesia Recovery</option>
                            <option value="radiology">Radiology</option>
                            <option value="laboratory">Laboratory</option>
                            <option value="pharmacy">Pharmacy</option>
                            <option value="hallway">Hallway/Common Area</option>
                            <option value="other">Other</option>
                        </select>
                        <input type="text" id="location-room" placeholder="Room/Bed number (if applicable)"
                            class="p-3 border border-gray-300 rounded-lg"
                            value="${data.location_room || ''}">
                    </div>
                </div>

                <!-- Patient MRN (NO NAME) -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Patient MRN (Medical Record Number)
                    </label>
                    <input type="text" id="patient-mrn"
                        class="w-full p-3 border border-gray-300 rounded-lg"
                        placeholder="Enter MRN only - DO NOT use patient name"
                        value="${data.patient_mrn || ''}">
                    <p class="text-xs text-red-600 mt-1">
                        <i class="fas fa-exclamation-circle"></i>
                        Use MRN only for legal protection. Never use patient name in incident reports.
                    </p>
                </div>
            </div>
        `;
    }

    renderDescriptionStep(data) {
        return `
            <div class="space-y-4">
                <!-- Writing Guidelines -->
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h4 class="font-semibold text-blue-900 mb-2">
                        <i class="fas fa-lightbulb mr-2"></i>Writing Guidelines
                    </h4>
                    <ul class="text-sm text-blue-800 space-y-1">
                        <li><i class="fas fa-check text-green-600 mr-2"></i>Use objective, factual language</li>
                        <li><i class="fas fa-check text-green-600 mr-2"></i>Write in chronological order</li>
                        <li><i class="fas fa-check text-green-600 mr-2"></i>Include relevant vital signs and assessments</li>
                        <li><i class="fas fa-times text-red-600 mr-2"></i>Don't use words like "appeared," "seemed," or "might have"</li>
                        <li><i class="fas fa-times text-red-600 mr-2"></i>Don't assign blame or speculate about causes</li>
                    </ul>
                </div>

                <!-- Factual Description -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Factual Description of Incident <span class="text-red-500">*</span>
                    </label>
                    <textarea id="factual-description" rows="8" required
                        class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                        placeholder="Example:&#10;&#10;At 14:30, patient (MRN 12345678) was found on floor next to bed in room 302. Patient was alert and oriented x3. No visible injuries noted on initial assessment. Vital signs: BP 130/80, HR 88, RR 16, Temp 98.6°F. Patient stated 'I was trying to reach the bathroom.' Call light was within reach but not activated. Bed was in low position with both side rails up. Non-skid socks were on patient's feet. Patient assisted back to bed...">${data.factual_description || ''}</textarea>
                    <div class="flex justify-between items-center mt-1">
                        <p class="text-xs text-gray-500">Be as detailed and factual as possible</p>
                        <p class="text-xs text-gray-500">${data.factual_description?.length || 0} characters</p>
                    </div>
                </div>

                <!-- Patient Condition Before/After -->
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Patient Condition Before Incident
                        </label>
                        <textarea id="condition-before" rows="3"
                            class="w-full p-3 border border-gray-300 rounded-lg text-sm"
                            placeholder="e.g., Alert, ambulatory with walker, no pain reported">${data.condition_before || ''}</textarea>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Patient Condition After Incident
                        </label>
                        <textarea id="condition-after" rows="3"
                            class="w-full p-3 border border-gray-300 rounded-lg text-sm"
                            placeholder="e.g., Alert, vital signs stable, no visible injuries, c/o right hip pain 4/10">${data.condition_after || ''}</textarea>
                    </div>
                </div>

                <!-- Contributing Factors (Observed) -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Observed Contributing Factors (Optional)
                    </label>
                    <p class="text-xs text-gray-600 mb-2">Only include if directly observed. Do not speculate.</p>
                    <div class="space-y-2">
                        ${['Wet floor', 'Equipment malfunction', 'Inadequate lighting', 'Language barrier',
                            'Patient non-compliance', 'Staffing issue', 'Communication breakdown'].map(factor => `
                            <label class="flex items-center space-x-2">
                                <input type="checkbox" name="contributing_factors" value="${factor}"
                                    class="text-blue-600 rounded"
                                    ${(data.contributing_factors || []).includes(factor) ? 'checked' : ''}>
                                <span class="text-sm text-gray-700">${factor}</span>
                            </label>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    renderActionsStep(data) {
        return `
            <div class="space-y-6">
                <!-- Immediate Actions Taken -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        Immediate Actions Taken <span class="text-red-500">*</span>
                    </label>
                    <div id="actions-list" class="space-y-2 mb-3">
                        ${(data.actions_taken || []).map((action, idx) => `
                            <div class="flex items-center space-x-2 bg-green-50 border border-green-200 p-3 rounded">
                                <i class="fas fa-check-circle text-green-600"></i>
                                <input type="text" value="${action}"
                                    class="flex-1 bg-transparent border-none focus:outline-none"
                                    onchange="updateAction(${idx}, this.value)">
                                <button class="text-red-600 hover:text-red-800" onclick="removeAction(${idx})">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                    <button id="add-action-btn" class="text-blue-600 hover:text-blue-800 text-sm">
                        <i class="fas fa-plus mr-1"></i>Add Action Taken
                    </button>

                    <!-- Quick Add Common Actions -->
                    <div class="mt-3">
                        <label class="text-xs text-gray-600">Quick Add:</label>
                        <div class="flex flex-wrap gap-2 mt-1">
                            ${['Patient assessed for injuries', 'Vital signs obtained', 'Physician notified',
                                'Family notified', 'Incident report initiated', 'Patient repositioned safely',
                                'Safety measures reinforced', 'Equipment removed from service'].map(action => `
                                <button class="px-2 py-1 bg-blue-50 text-xs rounded hover:bg-blue-100"
                                    onclick="addAction('${action.replace(/'/g, "\\'")}')">
                                    + ${action}
                                </button>
                            `).join('')}
                        </div>
                    </div>
                </div>

                <!-- Notifications Made -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-3">
                        Notifications Made <span class="text-red-500">*</span>
                    </label>

                    <!-- Physician -->
                    <div class="border border-gray-200 rounded-lg p-4 mb-3">
                        <label class="flex items-center space-x-2 mb-2">
                            <input type="checkbox" id="physician-notified"
                                class="text-blue-600 rounded"
                                ${data.physician_notified ? 'checked' : ''}>
                            <span class="font-medium text-gray-700">Physician Notified</span>
                        </label>
                        <div id="physician-details" class="grid grid-cols-2 gap-3 mt-2 ${!data.physician_notified ? 'hidden' : ''}">
                            <input type="text" id="physician-name" placeholder="Physician name"
                                class="p-2 border border-gray-300 rounded"
                                value="${data.physician_name || ''}">
                            <input type="time" id="physician-time" placeholder="Time notified"
                                class="p-2 border border-gray-300 rounded"
                                value="${data.physician_time || ''}">
                        </div>
                    </div>

                    <!-- Supervisor -->
                    <div class="border border-gray-200 rounded-lg p-4 mb-3">
                        <label class="flex items-center space-x-2 mb-2">
                            <input type="checkbox" id="supervisor-notified"
                                class="text-blue-600 rounded"
                                ${data.supervisor_notified ? 'checked' : ''}>
                            <span class="font-medium text-gray-700">Supervisor Notified</span>
                        </label>
                        <div id="supervisor-details" class="grid grid-cols-2 gap-3 mt-2 ${!data.supervisor_notified ? 'hidden' : ''}">
                            <input type="text" id="supervisor-name" placeholder="Supervisor name"
                                class="p-2 border border-gray-300 rounded"
                                value="${data.supervisor_name || ''}">
                            <input type="time" id="supervisor-time" placeholder="Time notified"
                                class="p-2 border border-gray-300 rounded"
                                value="${data.supervisor_time || ''}">
                        </div>
                    </div>

                    <!-- Family -->
                    <div class="border border-gray-200 rounded-lg p-4">
                        <label class="flex items-center space-x-2 mb-2">
                            <input type="checkbox" id="family-notified"
                                class="text-blue-600 rounded"
                                ${data.family_notified ? 'checked' : ''}>
                            <span class="font-medium text-gray-700">Family Notified</span>
                        </label>
                        <div id="family-details" class="grid grid-cols-2 gap-3 mt-2 ${!data.family_notified ? 'hidden' : ''}">
                            <input type="text" id="family-contact" placeholder="Contact person relationship"
                                class="p-2 border border-gray-300 rounded"
                                value="${data.family_contact || ''}">
                            <input type="time" id="family-time" placeholder="Time notified"
                                class="p-2 border border-gray-300 rounded"
                                value="${data.family_time || ''}">
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderWitnessesStep(data) {
        return `
            <div class="space-y-4">
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p class="text-sm text-blue-800">
                        <i class="fas fa-info-circle mr-2"></i>
                        List staff members who witnessed the incident. Include name and role only.
                    </p>
                </div>

                <!-- Witnesses List -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-3">
                        Witnesses (Staff Only)
                    </label>
                    <div id="witnesses-list" class="space-y-2 mb-3">
                        ${(data.witnesses || []).map((witness, idx) => `
                            <div class="flex items-center space-x-2 bg-gray-50 p-3 rounded">
                                <i class="fas fa-user text-blue-600"></i>
                                <input type="text" placeholder="Full name"
                                    value="${witness.name || ''}"
                                    class="flex-1 p-2 bg-white border border-gray-300 rounded"
                                    onchange="updateWitnessName(${idx}, this.value)">
                                <input type="text" placeholder="Role (e.g., RN, CNA)"
                                    value="${witness.role || ''}"
                                    class="w-32 p-2 bg-white border border-gray-300 rounded"
                                    onchange="updateWitnessRole(${idx}, this.value)">
                                <button class="text-red-600 hover:text-red-800" onclick="removeWitness(${idx})">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                        `).join('')}
                    </div>
                    <button id="add-witness-btn" class="text-blue-600 hover:text-blue-800 text-sm">
                        <i class="fas fa-plus mr-1"></i>Add Witness
                    </button>
                </div>

                <!-- No Witnesses -->
                <label class="flex items-center space-x-2">
                    <input type="checkbox" id="no-witnesses"
                        class="text-blue-600 rounded"
                        ${data.no_witnesses ? 'checked' : ''}>
                    <span class="text-sm text-gray-700">No witnesses present</span>
                </label>
            </div>
        `;
    }

    renderReviewStep(data) {
        return `
            <div class="space-y-6">
                <!-- Critical Warning -->
                <div class="bg-red-50 border-l-4 border-red-500 p-4">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <i class="fas fa-lock text-red-500"></i>
                        </div>
                        <div class="ml-3">
                            <h3 class="text-sm font-medium text-red-800">Immutable Legal Document</h3>
                            <div class="mt-2 text-sm text-red-700">
                                <p><strong>WARNING:</strong> Once signed and submitted, this report CANNOT be edited or deleted.
                                Review carefully before signing.</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Summary -->
                <div class="bg-white border border-gray-200 rounded-lg p-6">
                    <h4 class="font-bold text-gray-900 mb-4">Incident Report Summary</h4>

                    <div class="space-y-3 text-sm">
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <span class="text-gray-600">Incident Type:</span>
                                <span class="font-semibold text-gray-900 ml-2">${data.incident_type || 'Not specified'}</span>
                            </div>
                            <div>
                                <span class="text-gray-600">Date/Time:</span>
                                <span class="font-semibold text-gray-900 ml-2">${data.incident_date} ${data.incident_time}</span>
                            </div>
                        </div>

                        <div>
                            <span class="text-gray-600">Location:</span>
                            <span class="font-semibold text-gray-900 ml-2">${data.location_unit} ${data.location_room || ''}</span>
                        </div>

                        <div class="pt-2 border-t">
                            <span class="text-gray-600">Description:</span>
                            <p class="text-gray-900 mt-1 italic">"${(data.factual_description || '').substring(0, 150)}${data.factual_description?.length > 150 ? '...' : ''}"</p>
                        </div>

                        <div class="grid grid-cols-3 gap-2 pt-2 border-t">
                            <div class="text-center p-2 bg-gray-50 rounded">
                                <p class="text-xs text-gray-600">Actions Taken</p>
                                <p class="font-semibold text-gray-900">${(data.actions_taken || []).length}</p>
                            </div>
                            <div class="text-center p-2 bg-gray-50 rounded">
                                <p class="text-xs text-gray-600">Notifications</p>
                                <p class="font-semibold text-gray-900">${[data.physician_notified, data.supervisor_notified, data.family_notified].filter(Boolean).length}</p>
                            </div>
                            <div class="text-center p-2 bg-gray-50 rounded">
                                <p class="text-xs text-gray-600">Witnesses</p>
                                <p class="font-semibold text-gray-900">${data.no_witnesses ? 'None' : (data.witnesses || []).length}</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Digital Signature -->
                <div class="bg-white border border-gray-200 rounded-lg p-6">
                    <h4 class="font-bold text-gray-900 mb-4">Digital Signature</h4>

                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">
                                Your Full Name (Typed) <span class="text-red-500">*</span>
                            </label>
                            <input type="text" id="nurse-signature-name" required
                                class="w-full p-3 border border-gray-300 rounded-lg"
                                placeholder="Type your full name as digital signature"
                                value="${data.nurse_signature_name || ''}">
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">
                                Your Credentials <span class="text-red-500">*</span>
                            </label>
                            <input type="text" id="nurse-credentials" required
                                class="w-full p-3 border border-gray-300 rounded-lg"
                                placeholder="e.g., RN, LPN, NP"
                                value="${data.nurse_credentials || ''}">
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">
                                Employee ID <span class="text-red-500">*</span>
                            </label>
                            <input type="text" id="employee-id" required
                                class="w-full p-3 border border-gray-300 rounded-lg"
                                placeholder="Your employee ID number"
                                value="${data.employee_id || ''}">
                        </div>

                        <!-- Acknowledgment -->
                        <div class="bg-gray-50 border border-gray-300 rounded-lg p-4">
                            <label class="flex items-start space-x-3">
                                <input type="checkbox" id="acknowledge-immutable" required
                                    class="mt-1 text-blue-600 rounded">
                                <span class="text-sm text-gray-700">
                                    <strong>I acknowledge that:</strong> This report is factual and accurate to the best of my knowledge.
                                    Once submitted, this report cannot be edited or deleted and becomes part of the permanent legal record.
                                </span>
                            </label>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    getTitle() {
        return 'Incident Report';
    }

    getDescription() {
        return 'Legal documentation of incidents and adverse events. Immutable after submission.';
    }

    async complete() {
        // Verify acknowledgment
        const acknowledged = this.container.querySelector('#acknowledge-immutable')?.checked;
        if (!acknowledged) {
            this.showAlert('You must acknowledge that this report is immutable before submitting.', 'error');
            return;
        }

        this.collectStepData();
        this.showAlert('Submitting incident report...', 'info');

        try {
            const request = {
                incident_type: this.data.incident_type,
                incident_date_time: `${this.data.incident_date}T${this.data.incident_time}`,
                location: `${this.data.location_unit}${this.data.location_room ? ' - ' + this.data.location_room : ''}`,
                patient_mrn: this.data.patient_mrn,
                factual_description: this.data.factual_description,
                condition_before: this.data.condition_before,
                condition_after: this.data.condition_after,
                contributing_factors: this.data.contributing_factors || [],
                immediate_actions_taken: this.data.actions_taken || [],
                notifications_made: {
                    physician: this.data.physician_notified ? {
                        name: this.data.physician_name,
                        time: this.data.physician_time
                    } : null,
                    supervisor: this.data.supervisor_notified ? {
                        name: this.data.supervisor_name,
                        time: this.data.supervisor_time
                    } : null,
                    family: this.data.family_notified ? {
                        contact: this.data.family_contact,
                        time: this.data.family_time
                    } : null
                },
                witnesses: this.data.no_witnesses ? [] : (this.data.witnesses || []),
                nurse_signature: {
                    name: this.data.nurse_signature_name,
                    credentials: this.data.nurse_credentials,
                    employee_id: this.data.employee_id,
                    timestamp: new Date().toISOString()
                }
            };

            // API call would go here
            // const response = await fetch('/api/v1/incident-reports', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify(request)
            // });

            // For now, simulate success
            await new Promise(resolve => setTimeout(resolve, 1500));

            this.showAlert('Incident report submitted successfully. Report is now immutable.', 'success');

            // Clear draft
            localStorage.removeItem(`wizard_draft_${this.constructor.name}`);

            if (this.onComplete) {
                this.onComplete(this.data);
            }

        } catch (error) {
            console.error('Error:', error);
            this.showAlert('Error submitting incident report. Please try again.', 'error');
        }
    }
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IncidentReportWizard;
}
