/**
 * SBAR Report Wizard Component
 * Implements the SBAR (Situation, Background, Assessment, Recommendation) clinical communication tool
 */

import BaseWizard from './BaseWizard.js';

class SbarWizard extends BaseWizard {
    constructor(containerId) {
        super('sbar-report', containerId);
        this.steps = ['situation', 'background', 'assessment', 'recommendation', 'review'];
    }

    getTitle() {
        return 'SBAR Report Generator';
    }

    renderStep(stepName) {
        const content = document.getElementById('wizard-content');

        switch(stepName) {
            case 'situation':
                this.renderSituationStep(content);
                break;
            case 'background':
                this.renderBackgroundStep(content);
                break;
            case 'assessment':
                this.renderAssessmentStep(content);
                break;
            case 'recommendation':
                this.renderRecommendationStep(content);
                break;
            case 'review':
                this.renderReviewStep(content);
                break;
            default:
                this.showError(`Unknown step: ${stepName}`);
        }

        this.currentStep = this.steps.indexOf(stepName) + 1;
        this.updateProgress();
    }

    renderSituationStep(container) {
        container.innerHTML = `
            <div class="step-content">
                <div class="step-header">
                    <h3><i class="fas fa-info-circle text-blue-600"></i> Situation</h3>
                    <p class="text-gray-600">Describe the current patient situation clearly and concisely.</p>
                </div>

                <div class="form-group">
                    <label for="patient-name">Patient Identifier:</label>
                    <input type="text" id="patient-name" class="form-input"
                           placeholder="Room 302A, Initial J.D." />
                </div>

                <div class="form-group">
                    <label for="situation-text">Current Situation:</label>
                    <textarea id="situation-text" class="form-textarea" rows="4"
                              placeholder="Patient presenting with... Current vital signs... Immediate concerns..."></textarea>
                </div>

                <div class="clinical-prompts">
                    <h4>Consider including:</h4>
                    <ul class="prompt-list">
                        <li>• Patient age, gender, diagnosis</li>
                        <li>• Current symptoms or changes in condition</li>
                        <li>• Vital signs if relevant</li>
                        <li>• Time-sensitive information</li>
                    </ul>
                </div>
            </div>
        `;
    }

    renderBackgroundStep(container) {
        container.innerHTML = `
            <div class="step-content">
                <div class="step-header">
                    <h3><i class="fas fa-history text-green-600"></i> Background</h3>
                    <p class="text-gray-600">Provide relevant medical history and context.</p>
                </div>

                <div class="form-group">
                    <label for="medical-history">Relevant Medical History:</label>
                    <textarea id="medical-history" class="form-textarea" rows="3"
                              placeholder="Pertinent diagnoses, allergies, medications..."></textarea>
                </div>

                <div class="form-group">
                    <label for="recent-events">Recent Events:</label>
                    <textarea id="recent-events" class="form-textarea" rows="3"
                              placeholder="Recent procedures, treatments, changes in condition..."></textarea>
                </div>

                <div class="clinical-prompts">
                    <h4>Consider including:</h4>
                    <ul class="prompt-list">
                        <li>• Admission diagnosis and date</li>
                        <li>• Relevant comorbidities</li>
                        <li>• Current medications</li>
                        <li>• Recent lab results or procedures</li>
                    </ul>
                </div>
            </div>
        `;
    }

    renderAssessmentStep(container) {
        container.innerHTML = `
            <div class="step-content">
                <div class="step-header">
                    <h3><i class="fas fa-stethoscope text-purple-600"></i> Assessment</h3>
                    <p class="text-gray-600">Your professional nursing assessment of the situation.</p>
                </div>

                <div class="form-group">
                    <label for="clinical-assessment">Clinical Assessment:</label>
                    <textarea id="clinical-assessment" class="form-textarea" rows="4"
                              placeholder="Your professional assessment of the patient's condition..."></textarea>
                </div>

                <div class="form-group">
                    <label for="concerns">Specific Concerns:</label>
                    <textarea id="concerns" class="form-textarea" rows="3"
                              placeholder="What are you most concerned about? What has changed?"></textarea>
                </div>

                <div class="clinical-prompts">
                    <h4>Assessment should include:</h4>
                    <ul class="prompt-list">
                        <li>• Your interpretation of the data</li>
                        <li>• What you think is happening</li>
                        <li>• Level of urgency or stability</li>
                        <li>• Specific nursing concerns</li>
                    </ul>
                </div>
            </div>
        `;
    }

    renderRecommendationStep(container) {
        container.innerHTML = `
            <div class="step-content">
                <div class="step-header">
                    <h3><i class="fas fa-lightbulb text-orange-600"></i> Recommendation</h3>
                    <p class="text-gray-600">What specific actions do you recommend?</p>
                </div>

                <div class="form-group">
                    <label for="recommendations">Recommendations:</label>
                    <textarea id="recommendations" class="form-textarea" rows="4"
                              placeholder="Specific actions you recommend..."></textarea>
                </div>

                <div class="form-group">
                    <label for="urgency">Urgency Level:</label>
                    <select id="urgency" class="form-select">
                        <option value="routine">Routine - Within normal timeframe</option>
                        <option value="soon">Soon - Within next hour</option>
                        <option value="urgent">Urgent - Within 30 minutes</option>
                        <option value="immediate">Immediate - Right now</option>
                    </select>
                </div>

                <div class="clinical-prompts">
                    <h4>Recommendations might include:</h4>
                    <ul class="prompt-list">
                        <li>• Orders you think are needed</li>
                        <li>• When you need provider to see patient</li>
                        <li>• Specific interventions to consider</li>
                        <li>• Monitoring requirements</li>
                    </ul>
                </div>
            </div>
        `;
    }

    async nextStep() {
        const currentStepName = this.steps[this.currentStep - 1];
        const stepData = this.collectStepData(currentStepName);

        if (stepData) {
            const result = await this.submitStep(stepData);
            if (result && result.success) {
                if (result.data.next_step) {
                    this.renderStep(result.data.next_step);
                } else {
                    await this.generateReport();
                }
            }
        }
    }

    collectStepData(stepName) {
        switch(stepName) {
            case 'situation':
                return {
                    patient_name: document.getElementById('patient-name').value,
                    situation: document.getElementById('situation-text').value
                };
            case 'background':
                return {
                    medical_history: document.getElementById('medical-history').value,
                    recent_events: document.getElementById('recent-events').value
                };
            case 'assessment':
                return {
                    clinical_assessment: document.getElementById('clinical-assessment').value,
                    concerns: document.getElementById('concerns').value
                };
            case 'recommendation':
                return {
                    recommendations: document.getElementById('recommendations').value,
                    urgency: document.getElementById('urgency').value
                };
            default:
                return null;
        }
    }

    async generateReport() {
        try {
            const response = await fetch(`${this.apiBase}/${this.wizardType}/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ wizard_id: this.wizardId })
            });

            const result = await response.json();
            if (result.success) {
                this.displayGeneratedReport(result.data.sbar_report);
            }
        } catch (error) {
            this.showError('Failed to generate SBAR report');
        }
    }

    displayGeneratedReport(report) {
        const content = document.getElementById('wizard-content');
        content.innerHTML = `
            <div class="report-generated">
                <h3><i class="fas fa-check-circle text-green-600"></i> SBAR Report Generated</h3>
                <div class="report-content">
                    <pre class="formatted-report">${report}</pre>
                </div>
                <div class="report-actions">
                    <button class="btn btn-primary" onclick="this.copyReport()">
                        <i class="fas fa-copy"></i> Copy Report
                    </button>
                    <button class="btn btn-secondary" onclick="this.downloadReport()">
                        <i class="fas fa-download"></i> Download
                    </button>
                </div>
            </div>
        `;

        // Hide navigation buttons
        document.getElementById('prev-btn').style.display = 'none';
        document.getElementById('next-btn').innerHTML = '<i class="fas fa-redo"></i> New Report';
        document.getElementById('next-btn').onclick = () => window.location.reload();
    }
}

export default SbarWizard;
