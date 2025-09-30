/**
 * SBAR Wizard Component
 * Structured clinical communication wizard for patient handoffs
 */

class SbarWizard extends BaseWizard {
    constructor(containerId, config = {}) {
        const sbarConfig = {
            steps: [
                {
                    title: 'Situation',
                    description: 'Briefly describe the current situation and reason for communication.',
                    fields: [
                        {
                            id: 'patient_name',
                            type: 'text',
                            label: 'Patient Name/ID',
                            placeholder: 'Patient identifier (use initials or ID for privacy)',
                            required: true,
                            help: 'Use patient initials or ID number for privacy protection'
                        },
                        {
                            id: 'room_unit',
                            type: 'text',
                            label: 'Room/Unit',
                            placeholder: 'e.g., Room 205, ICU Bed 3',
                            required: true
                        },
                        {
                            id: 'situation_description',
                            type: 'textarea',
                            label: 'Current Situation',
                            placeholder: 'Briefly describe why you are calling and the current situation...',
                            required: true,
                            rows: 4,
                            help: 'Include the immediate reason for communication and current patient status'
                        },
                        {
                            id: 'communication_purpose',
                            type: 'select',
                            label: 'Purpose of Communication',
                            required: true,
                            options: [
                                { value: 'shift_handoff', label: 'Shift Handoff' },
                                { value: 'urgent_concern', label: 'Urgent Patient Concern' },
                                { value: 'physician_notification', label: 'Physician Notification' },
                                { value: 'transfer_report', label: 'Transfer Report' },
                                { value: 'discharge_planning', label: 'Discharge Planning' },
                                { value: 'other', label: 'Other' }
                            ]
                        }
                    ]
                },
                {
                    title: 'Background',
                    description: 'Provide relevant clinical background and history.',
                    fields: [
                        {
                            id: 'admission_date',
                            type: 'date',
                            label: 'Admission Date',
                            required: true
                        },
                        {
                            id: 'primary_diagnosis',
                            type: 'text',
                            label: 'Primary Diagnosis',
                            placeholder: 'e.g., Pneumonia, CHF exacerbation',
                            required: true
                        },
                        {
                            id: 'relevant_history',
                            type: 'textarea',
                            label: 'Relevant Medical History',
                            placeholder: 'Include pertinent medical history, allergies, recent procedures...',
                            required: true,
                            rows: 4,
                            help: 'Focus on history relevant to the current situation'
                        },
                        {
                            id: 'current_medications',
                            type: 'textarea',
                            label: 'Current Medications',
                            placeholder: 'List current medications and recent changes...',
                            rows: 3,
                            help: 'Include recent medication changes or concerns'
                        },
                        {
                            id: 'recent_treatments',
                            type: 'textarea',
                            label: 'Recent Treatments/Procedures',
                            placeholder: 'Recent interventions, procedures, or significant events...',
                            rows: 3
                        }
                    ]
                },
                {
                    title: 'Assessment',
                    description: 'Current assessment findings and clinical status.',
                    fields: [
                        {
                            id: 'vital_signs',
                            type: 'textarea',
                            label: 'Current Vital Signs',
                            placeholder: 'BP: ___ HR: ___ RR: ___ Temp: ___ O2 Sat: ___ Pain: ___',
                            required: true,
                            rows: 2,
                            help: 'Include the most recent vital signs and trends'
                        },
                        {
                            id: 'physical_assessment',
                            type: 'textarea',
                            label: 'Key Physical Assessment Findings',
                            placeholder: 'Significant physical assessment findings...',
                            required: true,
                            rows: 4,
                            help: 'Focus on abnormal or significant findings'
                        },
                        {
                            id: 'mental_status',
                            type: 'select',
                            label: 'Mental Status',
                            required: true,
                            options: [
                                { value: 'alert_oriented', label: 'Alert and Oriented x 4' },
                                { value: 'alert_confused', label: 'Alert but Confused' },
                                { value: 'lethargic', label: 'Lethargic' },
                                { value: 'obtunded', label: 'Obtunded' },
                                { value: 'unresponsive', label: 'Unresponsive' },
                                { value: 'sedated', label: 'Sedated' }
                            ]
                        },
                        {
                            id: 'pain_assessment',
                            type: 'text',
                            label: 'Pain Assessment',
                            placeholder: 'Pain scale rating and description',
                            help: 'Include pain scale rating, location, and characteristics'
                        },
                        {
                            id: 'clinical_concerns',
                            type: 'textarea',
                            label: 'Clinical Concerns',
                            placeholder: 'Any concerning changes or clinical issues...',
                            rows: 3,
                            help: 'Highlight any changes from baseline or concerning trends'
                        }
                    ]
                },
                {
                    title: 'Recommendation',
                    description: 'Your recommendations and suggested actions.',
                    fields: [
                        {
                            id: 'immediate_needs',
                            type: 'textarea',
                            label: 'Immediate Needs/Actions',
                            placeholder: 'What needs to be done immediately...',
                            required: true,
                            rows: 3,
                            help: 'Specify urgent actions needed'
                        },
                        {
                            id: 'physician_orders',
                            type: 'textarea',
                            label: 'Physician Orders Needed',
                            placeholder: 'Specific orders you are requesting...',
                            rows: 3,
                            help: 'Be specific about what orders you need'
                        },
                        {
                            id: 'monitoring_requirements',
                            type: 'textarea',
                            label: 'Monitoring Requirements',
                            placeholder: 'How often should patient be assessed...',
                            rows: 3,
                            help: 'Specify frequency and type of monitoring needed'
                        },
                        {
                            id: 'priority_level',
                            type: 'radio',
                            label: 'Priority Level',
                            required: true,
                            options: [
                                { value: 'routine', label: 'Routine - Can wait for next rounds' },
                                { value: 'urgent', label: 'Urgent - Within 1 hour' },
                                { value: 'stat', label: 'STAT - Immediate attention required' }
                            ]
                        },
                        {
                            id: 'follow_up_needed',
                            type: 'select',
                            label: 'Follow-up Needed',
                            options: [
                                { value: 'yes_callback', label: 'Yes - Please call back with orders' },
                                { value: 'yes_visit', label: 'Yes - Please come assess patient' },
                                { value: 'no_followup', label: 'No follow-up needed' }
                            ]
                        }
                    ]
                }
            ],
            onComplete: (data) => this.generateSbarReport(data),
            onStepChange: (step, data) => this.saveProgress(step, data)
        };

        super(containerId, { ...sbarConfig, ...config });
    }

    getTitle() {
        return 'SBAR Communication Tool';
    }

    getDescription() {
        return 'Create structured clinical communication using the SBAR format for safe patient handoffs and physician notifications.';
    }

    generateSbarReport(data) {
        const report = this.formatSbarReport(data);
        this.displayReport(report, data);
    }

    formatSbarReport(data) {
        const timestamp = new Date().toLocaleString();
        
        return `
# SBAR COMMUNICATION REPORT
**Generated:** ${timestamp}
**Purpose:** ${this.formatSelectValue(data.communication_purpose)}

---

## SITUATION
**Patient:** ${data.patient_name || 'N/A'}
**Location:** ${data.room_unit || 'N/A'}
**Priority:** ${this.formatSelectValue(data.priority_level)?.toUpperCase() || 'ROUTINE'}

${data.situation_description || 'No situation description provided.'}

---

## BACKGROUND
**Admission Date:** ${data.admission_date || 'Not specified'}
**Primary Diagnosis:** ${data.primary_diagnosis || 'Not specified'}

**Medical History:**
${data.relevant_history || 'No relevant history documented.'}

**Current Medications:**
${data.current_medications || 'No medications documented.'}

**Recent Treatments/Procedures:**
${data.recent_treatments || 'No recent treatments documented.'}

---

## ASSESSMENT
**Vital Signs:**
${data.vital_signs || 'No vital signs documented.'}

**Mental Status:** ${this.formatSelectValue(data.mental_status) || 'Not assessed'}
**Pain Level:** ${data.pain_assessment || 'Not assessed'}

**Physical Assessment:**
${data.physical_assessment || 'No physical assessment documented.'}

**Clinical Concerns:**
${data.clinical_concerns || 'No specific concerns noted.'}

---

## RECOMMENDATION
**Immediate Actions Needed:**
${data.immediate_needs || 'No immediate actions specified.'}

**Physician Orders Requested:**
${data.physician_orders || 'No specific orders requested.'}

**Monitoring Requirements:**
${data.monitoring_requirements || 'Standard monitoring per unit protocol.'}

**Follow-up Required:** ${this.formatSelectValue(data.follow_up_needed) || 'Not specified'}

---

## CLINICAL SAFETY NOTICE
*This SBAR report is for clinical communication purposes only. All information should be verified and confirmed by the receiving healthcare provider. This tool is for educational and documentation assistance only.*

**Report ID:** SBAR-${Date.now()}
**Generated by:** AI Nurse Florence SBAR Wizard
        `.trim();
    }

    formatSelectValue(value) {
        const optionMap = {
            // Communication purpose
            'shift_handoff': 'Shift Handoff',
            'urgent_concern': 'Urgent Patient Concern',
            'physician_notification': 'Physician Notification',
            'transfer_report': 'Transfer Report',
            'discharge_planning': 'Discharge Planning',
            'other': 'Other',
            
            // Mental status
            'alert_oriented': 'Alert and Oriented x 4',
            'alert_confused': 'Alert but Confused',
            'lethargic': 'Lethargic',
            'obtunded': 'Obtunded',
            'unresponsive': 'Unresponsive',
            'sedated': 'Sedated',
            
            // Priority level
            'routine': 'Routine',
            'urgent': 'Urgent',
            'stat': 'STAT',
            
            // Follow-up
            'yes_callback': 'Yes - Callback requested',
            'yes_visit': 'Yes - Patient assessment needed',
            'no_followup': 'No follow-up needed'
        };
        
        return optionMap[value] || value;
    }

    displayReport(report, data) {
        const reportDiv = document.createElement('div');
        reportDiv.className = 'sbar-report-container fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
        
        reportDiv.innerHTML = `
            <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-full overflow-y-auto">
                <div class="p-6">
                    <div class="flex justify-between items-center mb-6">
                        <h2 class="text-2xl font-bold text-gray-800">SBAR Report Generated</h2>
                        <button id="close-report" class="text-gray-500 hover:text-gray-700">
                            <i class="fas fa-times text-xl"></i>
                        </button>
                    </div>
                    
                    <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
                        <div class="flex">
                            <i class="fas fa-exclamation-triangle text-yellow-400 mr-3 mt-1"></i>
                            <div>
                                <p class="text-sm text-yellow-700">
                                    <strong>Clinical Communication Tool:</strong> This SBAR report is for structured communication purposes only. 
                                    Always verify patient information and follow your institution's communication protocols.
                                </p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="report-content bg-gray-50 p-6 rounded-lg mb-6">
                        <pre class="whitespace-pre-wrap text-sm font-mono">${report}</pre>
                    </div>
                    
                    <div class="flex justify-between">
                        <div class="flex space-x-2">
                            <button id="print-report" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                                <i class="fas fa-print mr-2"></i>Print Report
                            </button>
                            <button id="copy-report" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                                <i class="fas fa-copy mr-2"></i>Copy to Clipboard
                            </button>
                            <button id="save-report" class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
                                <i class="fas fa-download mr-2"></i>Save as Text
                            </button>
                        </div>
                        <button id="new-sbar" class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700">
                            <i class="fas fa-plus mr-2"></i>New SBAR
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(reportDiv);
        
        // Event listeners
        reportDiv.querySelector('#close-report').addEventListener('click', () => {
            document.body.removeChild(reportDiv);
        });
        
        reportDiv.querySelector('#print-report').addEventListener('click', () => {
            window.print();
        });
        
        reportDiv.querySelector('#copy-report').addEventListener('click', () => {
            navigator.clipboard.writeText(report).then(() => {
                this.showAlert('Report copied to clipboard!', 'success');
            });
        });
        
        reportDiv.querySelector('#save-report').addEventListener('click', () => {
            this.downloadReport(report, data);
        });
        
        reportDiv.querySelector('#new-sbar').addEventListener('click', () => {
            document.body.removeChild(reportDiv);
            this.resetWizard();
        });
    }

    downloadReport(report, data) {
        const filename = `SBAR_Report_${data.patient_name || 'Patient'}_${new Date().toISOString().slice(0, 10)}.txt`;
        const blob = new Blob([report], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        this.showAlert('Report downloaded successfully!', 'success');
    }

    resetWizard() {
        this.currentStep = 0;
        this.data = {};
        localStorage.removeItem(`wizard_draft_${this.constructor.name}`);
        this.render();
        this.attachEventListeners();
    }

    saveProgress(step, data) {
        // Auto-save progress
        localStorage.setItem(`wizard_progress_${this.constructor.name}`, JSON.stringify({
            currentStep: step,
            data: data,
            timestamp: new Date().toISOString()
        }));
    }
}

// Auto-initialize if container exists
document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('sbar-wizard-container');
    if (container) {
        new SbarWizard('sbar-wizard-container');
    }
});

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SbarWizard;
}
