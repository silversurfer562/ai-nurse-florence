/**
 * Documentation Module for Clinical Wizards
 * Handles SBAR preview, edit, and export for legal documentation compliance
 *
 * Philosophy: "Assessment Without Documentation Is Incomplete"
 * See: docs/WIZARD_DOCUMENTATION_PHILOSOPHY.md
 */

const DocumentationModule = {
    /**
     * Generate SBAR documentation from wizard data
     * @param {Object} wizardData - Complete wizard assessment data
     * @param {String} wizardType - Type of wizard (sepsis, stroke, cardiac, etc.)
     * @returns {Object} SBAR formatted documentation
     */
    generateSBAR(wizardData, wizardType) {
        const templates = {
            'sepsis': this.generateSepsisSBAR,
            'stroke': this.generateStrokeSBAR,
            'cardiac': this.generateCardiacSBAR,
            'code-blue': this.generateCodeBlueSBAR,
            'blood-transfusion': this.generateBloodTransfusionSBAR,
            'restraint': this.generateRestraintSBAR,
            'fall-risk': this.generateFallRiskSBAR,
            // Add more templates as needed
        };

        const generator = templates[wizardType] || this.generateGenericSBAR;
        const sbarData = generator.call(this, wizardData);

        // Add metadata
        sbarData.metadata = {
            timestamp: new Date().toISOString(),
            timestampFormatted: new Date().toLocaleString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
            }),
            nurse: this.getCurrentNurse(),
            wizardType: wizardType,
            version: '1.0',
            documentId: this.generateDocumentId()
        };

        return sbarData;
    },

    /**
     * Generate SBAR for Sepsis Screening
     */
    generateSepsisSBAR(data) {
        return {
            situation: this.formatSituation({
                age: data.patientAge || 'Unknown',
                gender: data.patientGender || 'Unknown',
                chiefComplaint: data.chiefComplaint || 'Not documented',
                infectionSource: data.infectionSource || 'Unknown source'
            }),

            background: this.formatBackground({
                medicalHistory: data.medicalHistory || [],
                medications: data.medications || [],
                allergies: data.allergies || [],
                riskFactors: data.riskFactors || []
            }),

            assessment: this.formatSepsisAssessment({
                qsofaScore: data.qsofaScore || 0,
                qsofaComponents: data.qsofaComponents || {},
                sirsCount: data.sirsCount || 0,
                sirsComponents: data.sirsComponents || {},
                vitalSigns: data.vitalSigns || {},
                labs: data.labs || {}
            }),

            recommendation: this.formatSepsisRecommendation({
                interventions: data.interventions || [],
                providerNotified: data.providerNotified || false,
                providerName: data.providerName || '',
                notificationTime: data.notificationTime || ''
            })
        };
    },

    /**
     * Format Situation section
     */
    formatSituation(data) {
        return `${data.age} year old ${data.gender} presenting with ${data.chiefComplaint}. Suspected ${data.infectionSource} infection.`;
    },

    /**
     * Format Background section
     */
    formatBackground(data) {
        let background = '';

        if (data.medicalHistory && data.medicalHistory.length > 0) {
            background += `Past Medical History: ${data.medicalHistory.join(', ')}. `;
        }

        if (data.medications && data.medications.length > 0) {
            background += `Current Medications: ${data.medications.join(', ')}. `;
        }

        if (data.allergies && data.allergies.length > 0) {
            background += `Allergies: ${data.allergies.join(', ')}. `;
        } else {
            background += `Allergies: NKDA. `;
        }

        if (data.riskFactors && data.riskFactors.length > 0) {
            background += `Risk Factors: ${data.riskFactors.join(', ')}.`;
        }

        return background || 'No significant medical history documented.';
    },

    /**
     * Format Assessment section for Sepsis
     */
    formatSepsisAssessment(data) {
        let assessment = '';

        // qSOFA Score
        const qsofaRisk = data.qsofaScore >= 2 ? 'HIGH RISK' : 'Low Risk';
        assessment += `qSOFA Score: ${data.qsofaScore}/3 (${qsofaRisk})\n`;

        if (data.qsofaComponents) {
            assessment += `  - Respiratory Rate: ${data.qsofaComponents.respiratoryRate || 'Not documented'}\n`;
            assessment += `  - Mental Status: ${data.qsofaComponents.mentalStatus || 'Not documented'}\n`;
            assessment += `  - Systolic BP: ${data.qsofaComponents.systolicBP || 'Not documented'}\n`;
        }

        // SIRS Criteria
        const sirsStatus = data.sirsCount >= 2 ? 'POSITIVE - SEPSIS SUSPECTED' : 'Negative';
        assessment += `\nSIRS Criteria: ${data.sirsCount}/4 (${sirsStatus})\n`;

        if (data.sirsComponents) {
            assessment += `  - Temperature: ${data.sirsComponents.temperature || 'Not documented'}\n`;
            assessment += `  - Heart Rate: ${data.sirsComponents.heartRate || 'Not documented'}\n`;
            assessment += `  - Respiratory Rate: ${data.sirsComponents.respiratoryRate || 'Not documented'}\n`;
            assessment += `  - WBC Count: ${data.sirsComponents.wbc || 'Not documented'}\n`;
        }

        // Current Vitals
        if (data.vitalSigns && Object.keys(data.vitalSigns).length > 0) {
            assessment += `\nCurrent Vital Signs:\n`;
            assessment += `  - Temp: ${data.vitalSigns.temp || 'N/A'}\n`;
            assessment += `  - HR: ${data.vitalSigns.hr || 'N/A'} bpm\n`;
            assessment += `  - RR: ${data.vitalSigns.rr || 'N/A'}/min\n`;
            assessment += `  - BP: ${data.vitalSigns.bp || 'N/A'}\n`;
            assessment += `  - SpO2: ${data.vitalSigns.spo2 || 'N/A'}%\n`;
        }

        // Labs
        if (data.labs && Object.keys(data.labs).length > 0) {
            assessment += `\nLaboratory Values:\n`;
            if (data.labs.wbc) assessment += `  - WBC: ${data.labs.wbc}\n`;
            if (data.labs.lactate) assessment += `  - Lactate: ${data.labs.lactate} mmol/L\n`;
            if (data.labs.creatinine) assessment += `  - Creatinine: ${data.labs.creatinine} mg/dL\n`;
        }

        return assessment;
    },

    /**
     * Format Recommendation section for Sepsis
     */
    formatSepsisRecommendation(data) {
        let recommendation = '';

        if (data.interventions && data.interventions.length > 0) {
            recommendation += 'Sepsis Bundle Initiated (within 1 hour):\n';
            data.interventions.forEach(intervention => {
                recommendation += `  ☑ ${intervention}\n`;
            });
        }

        if (data.providerNotified) {
            recommendation += `\nProvider Notified: ${data.providerName || 'Attending physician'} at ${data.notificationTime || 'time not documented'}`;
        }

        recommendation += `\n\nContinue monitoring and reassess vitals every 15 minutes.`;

        return recommendation;
    },

    /**
     * Show preview modal with edit capability
     * @param {Object} sbarData - SBAR formatted data
     * @param {Object} options - Configuration options
     */
    showPreviewModal(sbarData, options = {}) {
        const {
            editable = true,
            onSave = null,
            onPrint = null,
            onPDF = null,
            onCancel = null
        } = options;

        // Remove existing modal if present
        const existing = document.getElementById('documentationModal');
        if (existing) existing.remove();

        // Create modal
        const modal = document.createElement('div');
        modal.id = 'documentationModal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            animation: fadeIn 0.3s ease;
        `;

        // Create modal content
        const modalContent = `
            <div style="background: white; border-radius: 12px; max-width: 900px; width: 90%; max-height: 90vh; display: flex; flex-direction: column; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);">
                <!-- Header -->
                <div style="padding: 20px 24px; border-bottom: 2px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 12px 12px 0 0;">
                    <div>
                        <h2 style="margin: 0; color: white; font-size: 20px; font-weight: 700;">
                            <i class="fas fa-file-medical"></i> Clinical Documentation
                        </h2>
                        <p style="margin: 4px 0 0 0; color: #e0e7ff; font-size: 13px;">Review and edit before submission</p>
                    </div>
                    <div style="display: flex; gap: 12px; align-items: center;">
                        <button id="toggleEditMode" style="background: white; color: #6366f1; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 14px;">
                            <i class="fas fa-edit"></i> ${editable ? 'Edit Mode' : 'View Mode'}
                        </button>
                    </div>
                </div>

                <!-- SBAR Content -->
                <div style="flex: 1; overflow-y: auto; padding: 24px;">
                    <div id="sbarContent" style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.6; white-space: pre-wrap;">
                        ${this.formatSBARForDisplay(sbarData)}
                    </div>
                </div>

                <!-- Footer Actions -->
                <div style="padding: 16px 24px; border-top: 2px solid #e5e7eb; display: flex; justify-content: space-between; background: #f9fafb; border-radius: 0 0 12px 12px;">
                    <div style="display: flex; gap: 8px;">
                        <button id="printBtn" style="background: #10b981; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: 600; display: flex; align-items: center; gap: 6px;">
                            <i class="fas fa-print"></i> Print
                        </button>
                        <button id="pdfBtn" style="background: #3b82f6; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: 600; display: flex; align-items: center; gap: 6px;">
                            <i class="fas fa-file-pdf"></i> PDF
                        </button>
                        <button id="copyBtn" style="background: #8b5cf6; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: 600; display: flex; align-items: center; gap: 6px;">
                            <i class="fas fa-copy"></i> Copy
                        </button>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button id="cancelBtn" style="background: #6b7280; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: 600;">
                            Cancel
                        </button>
                        <button id="saveBtn" style="background: #ef4444; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: 600; display: flex; align-items: center; gap: 6px;">
                            <i class="fas fa-save"></i> Save to EHR
                        </button>
                    </div>
                </div>
            </div>

            <style>
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
            </style>
        `;

        modal.innerHTML = modalContent;
        document.body.appendChild(modal);

        // Wire up event handlers
        this.setupModalEventHandlers(modal, sbarData, {
            onSave,
            onPrint,
            onPDF,
            onCancel,
            editable
        });
    },

    /**
     * Setup event handlers for modal
     */
    setupModalEventHandlers(modal, sbarData, options) {
        const contentDiv = modal.querySelector('#sbarContent');
        let isEditMode = false;

        // Edit mode toggle
        modal.querySelector('#toggleEditMode').addEventListener('click', () => {
            isEditMode = !isEditMode;
            contentDiv.contentEditable = isEditMode;
            contentDiv.style.background = isEditMode ? '#fffbeb' : '#f9fafb';
            contentDiv.style.border = isEditMode ? '2px solid #f59e0b' : '1px solid #e5e7eb';
            modal.querySelector('#toggleEditMode').innerHTML = isEditMode
                ? '<i class="fas fa-eye"></i> View Mode'
                : '<i class="fas fa-edit"></i> Edit Mode';
        });

        // Print button
        modal.querySelector('#printBtn').addEventListener('click', () => {
            if (options.onPrint) {
                options.onPrint(contentDiv.textContent);
            } else {
                this.printChartCopy(contentDiv.textContent);
            }
        });

        // PDF button
        modal.querySelector('#pdfBtn').addEventListener('click', () => {
            if (options.onPDF) {
                options.onPDF(contentDiv.textContent);
            } else {
                this.exportToPDF(contentDiv.textContent, sbarData.metadata);
            }
        });

        // Copy button
        modal.querySelector('#copyBtn').addEventListener('click', () => {
            this.copyToClipboard(contentDiv.textContent);
        });

        // Cancel button
        modal.querySelector('#cancelBtn').addEventListener('click', () => {
            modal.remove();
            if (options.onCancel) options.onCancel();
        });

        // Save button
        modal.querySelector('#saveBtn').addEventListener('click', () => {
            const finalText = contentDiv.textContent;
            modal.remove();
            if (options.onSave) options.onSave(finalText, sbarData);
        });

        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
                if (options.onCancel) options.onCancel();
            }
        });
    },

    /**
     * Format SBAR for display
     */
    formatSBARForDisplay(sbarData) {
        return `╔════════════════════════════════════════════════════════════════╗
║  CLINICAL DOCUMENTATION - SBAR FORMAT                         ║
╠════════════════════════════════════════════════════════════════╣
║  Date/Time: ${sbarData.metadata.timestampFormatted}
║  Nurse: ${sbarData.metadata.nurse}
║  Document ID: ${sbarData.metadata.documentId}
╚════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 SITUATION:

${sbarData.situation}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 BACKGROUND:

${sbarData.background}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 ASSESSMENT:

${sbarData.assessment}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 RECOMMENDATION:

${sbarData.recommendation}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Electronically documented by: ${sbarData.metadata.nurse}
Time: ${sbarData.metadata.timestampFormatted}

This documentation was generated using AI Nurse Florence Clinical Wizard.
Review for accuracy and completeness before submission.`;
    },

    /**
     * Print chart copy
     */
    printChartCopy(sbarText) {
        const printWindow = window.open('', '', 'width=800,height=600');
        printWindow.document.write(`
            <html>
            <head>
                <title>Clinical Documentation - Chart Copy</title>
                <style>
                    body { font-family: 'Courier New', monospace; font-size: 12px; margin: 20px; }
                    pre { white-space: pre-wrap; }
                </style>
            </head>
            <body>
                <pre>${sbarText}</pre>
            </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    },

    /**
     * Export to PDF
     */
    exportToPDF(sbarText, metadata) {
        // Create a blob with the content
        const blob = new Blob([sbarText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);

        // Create download link
        const a = document.createElement('a');
        a.href = url;
        a.download = `clinical-documentation-${metadata.documentId}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        alert('Documentation downloaded. You can convert to PDF using your preferred tool.');
    },

    /**
     * Copy to clipboard
     */
    copyToClipboard(sbarText) {
        navigator.clipboard.writeText(sbarText).then(() => {
            alert('Documentation copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy:', err);
            alert('Failed to copy to clipboard. Please select and copy manually.');
        });
    },

    /**
     * Get current nurse (from session or prompt)
     */
    getCurrentNurse() {
        // In production, this would come from authentication/session
        return prompt('Enter your name and credentials (e.g., Jane Smith, RN):', 'Jane Smith, RN') || 'Not provided';
    },

    /**
     * Generate unique document ID
     */
    generateDocumentId() {
        return 'DOC-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9).toUpperCase();
    },

    /**
     * Validate documentation completeness
     */
    validateDocumentation(sbarData) {
        const required = ['situation', 'background', 'assessment', 'recommendation'];
        const missing = required.filter(field =>
            !sbarData[field] || sbarData[field].trim() === ''
        );

        if (missing.length > 0) {
            return {
                valid: false,
                errors: missing.map(f => `${f.toUpperCase()} section is required`)
            };
        }

        return { valid: true, errors: [] };
    },

    // Placeholder templates for other wizards (to be implemented)
    generateStrokeSBAR(data) {
        return { situation: 'Stroke SBAR - To be implemented', background: '', assessment: '', recommendation: '' };
    },

    generateCardiacSBAR(data) {
        return { situation: 'Cardiac SBAR - To be implemented', background: '', assessment: '', recommendation: '' };
    },

    generateCodeBlueSBAR(data) {
        return { situation: 'Code Blue SBAR - To be implemented', background: '', assessment: '', recommendation: '' };
    },

    generateBloodTransfusionSBAR(data) {
        return { situation: 'Blood Transfusion SBAR - To be implemented', background: '', assessment: '', recommendation: '' };
    },

    generateRestraintSBAR(data) {
        return { situation: 'Restraint SBAR - To be implemented', background: '', assessment: '', recommendation: '' };
    },

    generateFallRiskSBAR(data) {
        return { situation: 'Fall Risk SBAR - To be implemented', background: '', assessment: '', recommendation: '' };
    },

    generateGenericSBAR(data) {
        return {
            situation: data.situation || 'Clinical situation to be documented',
            background: data.background || 'Patient background information',
            assessment: data.assessment || 'Clinical assessment findings',
            recommendation: data.recommendation || 'Recommended actions'
        };
    }
};

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DocumentationModule;
}
