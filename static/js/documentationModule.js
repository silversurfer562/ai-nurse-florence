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

    /**
     * Generate SBAR for Stroke Assessment
     */
    generateStrokeSBAR(data) {
        return {
            situation: this.formatStrokeSituation({
                lastKnownWell: data.lastKnownWell || 'Unknown',
                nihssScore: data.nihssScore || 0,
                cincinnatiDroop: data.cincinnatiDroop,
                cincinnatiDrift: data.cincinnatiDrift,
                cincinnatiSpeech: data.cincinnatiSpeech
            }),

            background: this.formatStrokeBackground({
                medicalHistory: data.medicalHistory || [],
                medications: data.medications || [],
                allergies: data.allergies || [],
                riskFactors: this.extractStrokeRiskFactors(data)
            }),

            assessment: this.formatStrokeAssessment({
                nihssScore: data.nihssScore || 0,
                nihssComponents: this.getNIHSSComponents(data),
                cincinnatiPositive: this.isCincinnatiPositive(data),
                tpaWindow: this.calculateTPAWindow(data.lastKnownWell)
            }),

            recommendation: this.formatStrokeRecommendation({
                nihssScore: data.nihssScore || 0,
                tpaEligible: this.isTPAEligible(data),
                contraindications: data.contraindications || [],
                interventions: data.interventions || []
            })
        };
    },

    /**
     * Format Situation section for Stroke
     */
    formatStrokeSituation(data) {
        const timeFromOnset = this.calculateTimeFromOnset(data.lastKnownWell);
        const cincinnatiFindings = [];

        if (data.cincinnatiDroop === 'positive') cincinnatiFindings.push('facial droop');
        if (data.cincinnatiDrift === 'positive') cincinnatiFindings.push('arm drift');
        if (data.cincinnatiSpeech === 'abnormal') cincinnatiFindings.push('speech abnormality');

        const cincinnatiText = cincinnatiFindings.length > 0
            ? `Positive Cincinnati Stroke Scale findings: ${cincinnatiFindings.join(', ')}.`
            : 'Cincinnati Stroke Scale completed.';

        return `Patient presenting with acute neurological symptoms. Last known well: ${data.lastKnownWell} (${timeFromOnset}). ${cincinnatiText} NIHSS score: ${data.nihssScore}/42.`;
    },

    /**
     * Format Background section for Stroke
     */
    formatStrokeBackground(data) {
        let background = '';

        // Risk factors specific to stroke
        if (data.riskFactors && data.riskFactors.length > 0) {
            background += `Stroke Risk Factors: ${data.riskFactors.join(', ')}. `;
        }

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

        return background || 'No significant medical history documented.';
    },

    /**
     * Format Assessment section for Stroke
     */
    formatStrokeAssessment(data) {
        let assessment = '';

        // NIHSS Score
        const severity = data.nihssScore <= 4 ? 'Minor' :
                        data.nihssScore <= 15 ? 'Moderate' :
                        data.nihssScore <= 20 ? 'Moderate to Severe' :
                        'Severe';

        assessment += `NIHSS Score: ${data.nihssScore}/42 (${severity} Stroke)\n`;

        // NIHSS Component Breakdown
        if (data.nihssComponents) {
            assessment += `\nNIHSS Component Breakdown:\n`;
            assessment += `  - Level of Consciousness: ${data.nihssComponents.consciousness || 'Not documented'}\n`;
            assessment += `  - Best Gaze: ${data.nihssComponents.gaze || 'Not documented'}\n`;
            assessment += `  - Visual Fields: ${data.nihssComponents.visual || 'Not documented'}\n`;
            assessment += `  - Facial Palsy: ${data.nihssComponents.facialPalsy || 'Not documented'}\n`;
            assessment += `  - Motor Arm: ${data.nihssComponents.motorArm || 'Not documented'}\n`;
            assessment += `  - Motor Leg: ${data.nihssComponents.motorLeg || 'Not documented'}\n`;
            assessment += `  - Limb Ataxia: ${data.nihssComponents.ataxia || 'Not documented'}\n`;
            assessment += `  - Sensory: ${data.nihssComponents.sensory || 'Not documented'}\n`;
            assessment += `  - Language: ${data.nihssComponents.language || 'Not documented'}\n`;
            assessment += `  - Dysarthria: ${data.nihssComponents.dysarthria || 'Not documented'}\n`;
            assessment += `  - Extinction/Inattention: ${data.nihssComponents.extinction || 'Not documented'}\n`;
        }

        // Cincinnati Stroke Scale
        if (data.cincinnatiPositive) {
            assessment += `\nCincinnati Stroke Scale: POSITIVE - Suggests acute stroke\n`;
        }

        // tPA Window
        assessment += `\ntPA Eligibility Window: ${data.tpaWindow}\n`;

        return assessment;
    },

    /**
     * Format Recommendation section for Stroke
     */
    formatStrokeRecommendation(data) {
        let recommendation = '';

        // tPA Eligibility
        if (data.tpaEligible) {
            recommendation += `PATIENT IS CANDIDATE FOR tPA (Alteplase)\n`;
            recommendation += `Recommendation: Administer tPA per protocol if no contraindications develop.\n\n`;
        } else {
            recommendation += `Patient NOT candidate for tPA.\n`;
            if (data.contraindications && data.contraindications.length > 0) {
                recommendation += `Contraindications: ${data.contraindications.join(', ')}\n\n`;
            }
        }

        // Interventions
        if (data.interventions && data.interventions.length > 0) {
            recommendation += 'Stroke Interventions Completed:\n';
            data.interventions.forEach(intervention => {
                recommendation += `  ☑ ${intervention}\n`;
            });
        }

        // Standard recommendations based on severity
        recommendation += `\nRecommended Actions:\n`;
        recommendation += `  - Activate stroke team/neurology consult immediately\n`;
        recommendation += `  - Stat CT head (non-contrast) to rule out hemorrhage\n`;
        recommendation += `  - Blood pressure management (target < 185/110 if tPA candidate)\n`;
        recommendation += `  - Establish 2 large bore IVs\n`;
        recommendation += `  - Labs: CBC, BMP, coags (PT/INR, PTT), troponin, lipid panel\n`;
        recommendation += `  - Continuous cardiac and neuro monitoring\n`;

        if (data.nihssScore > 10) {
            recommendation += `  - Consider ICU admission due to severe stroke (NIHSS > 10)\n`;
        }

        recommendation += `\nReassess NIHSS and vital signs every 15 minutes.`;

        return recommendation;
    },

    /**
     * Helper: Extract stroke risk factors from data
     */
    extractStrokeRiskFactors(data) {
        const riskFactors = [];
        const history = data.medicalHistory || [];

        if (history.includes('Hypertension') || history.includes('HTN')) riskFactors.push('Hypertension');
        if (history.includes('Atrial Fibrillation') || history.includes('AFib')) riskFactors.push('Atrial Fibrillation');
        if (history.includes('Diabetes')) riskFactors.push('Diabetes');
        if (history.includes('Hyperlipidemia')) riskFactors.push('Hyperlipidemia');
        if (history.includes('Previous Stroke') || history.includes('CVA')) riskFactors.push('Previous Stroke');
        if (history.includes('TIA')) riskFactors.push('TIA');
        if (history.includes('Smoking')) riskFactors.push('Tobacco use');

        // Check medications for anticoagulants
        const medications = data.medications || [];
        if (medications.some(med => med.toLowerCase().includes('warfarin') || med.toLowerCase().includes('coumadin'))) {
            riskFactors.push('Anticoagulation therapy');
        }

        return riskFactors;
    },

    /**
     * Helper: Get NIHSS component descriptions
     */
    getNIHSSComponents(data) {
        return {
            consciousness: this.describeNIHSSComponent('1a-1c', [data.nihss1a, data.nihss1b, data.nihss1c]),
            gaze: this.describeNIHSSComponent('2', data.nihss2),
            visual: this.describeNIHSSComponent('3', data.nihss3),
            facialPalsy: this.describeNIHSSComponent('4', data.nihss4),
            motorArm: this.describeNIHSSComponent('5', [data.nihss5a, data.nihss5b]),
            motorLeg: this.describeNIHSSComponent('6', [data.nihss6a, data.nihss6b]),
            ataxia: this.describeNIHSSComponent('7', data.nihss7),
            sensory: this.describeNIHSSComponent('8', data.nihss8),
            language: this.describeNIHSSComponent('9', data.nihss9),
            dysarthria: this.describeNIHSSComponent('10', data.nihss10),
            extinction: this.describeNIHSSComponent('11', data.nihss11)
        };
    },

    /**
     * Helper: Describe NIHSS component score
     */
    describeNIHSSComponent(component, score) {
        if (Array.isArray(score)) {
            const total = score.reduce((sum, s) => sum + (s || 0), 0);
            return `${total} points`;
        }
        return score !== null && score !== undefined ? `${score} points` : 'Not assessed';
    },

    /**
     * Helper: Check if Cincinnati is positive
     */
    isCincinnatiPositive(data) {
        return data.cincinnatiDroop === 'positive' ||
               data.cincinnatiDrift === 'positive' ||
               data.cincinnatiSpeech === 'abnormal';
    },

    /**
     * Helper: Calculate time from onset
     */
    calculateTimeFromOnset(lastKnownWell) {
        if (!lastKnownWell) return 'Unknown';

        const onsetTime = new Date(lastKnownWell);
        const now = new Date();
        const diffMs = now - onsetTime;
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

        return `${diffHours}h ${diffMinutes}m ago`;
    },

    /**
     * Helper: Calculate tPA eligibility window
     */
    calculateTPAWindow(lastKnownWell) {
        if (!lastKnownWell) return 'Unable to determine - onset time unknown';

        const onsetTime = new Date(lastKnownWell);
        const now = new Date();
        const diffHours = (now - onsetTime) / (1000 * 60 * 60);

        if (diffHours < 3) {
            const remaining = 3 - diffHours;
            return `Within 3-hour window (${remaining.toFixed(1)} hours remaining)`;
        } else if (diffHours < 4.5) {
            const remaining = 4.5 - diffHours;
            return `Within extended 4.5-hour window (${remaining.toFixed(1)} hours remaining)`;
        } else {
            return `Outside tPA window (${diffHours.toFixed(1)} hours from onset)`;
        }
    },

    /**
     * Helper: Determine tPA eligibility
     */
    isTPAEligible(data) {
        if (!data.lastKnownWell) return false;

        const onsetTime = new Date(data.lastKnownWell);
        const now = new Date();
        const diffHours = (now - onsetTime) / (1000 * 60 * 60);

        const withinWindow = diffHours < 4.5;
        const hasContraindications = data.contraindications && data.contraindications.length > 0;

        return withinWindow && !hasContraindications;
    },

    /**
     * Generate SBAR for Cardiac Assessment
     */
    generateCardiacSBAR(data) {
        return {
            situation: this.formatCardiacSituation({
                age: data.patientAge || 'Unknown',
                gender: data.patientGender || 'Unknown',
                chiefComplaint: data.chiefComplaint || 'Not documented',
                painLocation: data.painLocation || 'Not specified',
                painQualities: data.painQualities || [],
                painDuration: data.painDuration || 'Unknown',
                heartScore: data.heartScore || 0,
                stemiCriteria: data.stemiCriteria || 'no'
            }),

            background: this.formatCardiacBackground({
                riskFactors: data.riskFactors || [],
                medicalHistory: data.medicalHistory || [],
                medications: data.medications || [],
                allergies: data.allergies || [],
                associatedSymptoms: data.associatedSymptoms || []
            }),

            assessment: this.formatCardiacAssessment({
                heartScore: data.heartScore || 0,
                heartRiskLevel: data.heartRiskLevel || 'Unknown',
                historyScore: data.historyScore || 0,
                ekgScore: data.ekgScore || 0,
                ageScore: data.ageScore || 0,
                riskFactors: data.riskFactors || [],
                troponinScore: data.troponinScore || 0,
                vitalSigns: data.vitalSigns || {},
                ecgRhythm: data.ecgRhythm || 'Not documented',
                stChanges: data.stChanges || {},
                stemiCriteria: data.stemiCriteria || 'no',
                labs: data.labs || {}
            }),

            recommendation: this.formatCardiacRecommendation({
                heartScore: data.heartScore || 0,
                stemiCriteria: data.stemiCriteria || 'no',
                disposition: data.disposition || 'Pending',
                medicationsGiven: data.medicationsGiven || [],
                cathLabTime: data.cathLabTime || '',
                dispositionInstructions: data.dispositionInstructions || '',
                additionalNotes: data.additionalNotes || ''
            })
        };
    },

    /**
     * Format Situation section for Cardiac
     */
    formatCardiacSituation(data) {
        let situation = `${data.age} year old ${data.gender} presenting with ${data.chiefComplaint}`;

        if (data.painLocation !== 'Not specified') {
            situation += ` located in ${data.painLocation}`;
        }

        if (data.painQualities && data.painQualities.length > 0) {
            situation += `, described as ${data.painQualities.join(', ')}`;
        }

        if (data.painDuration !== 'Unknown') {
            situation += `, duration: ${data.painDuration} minutes`;
        }

        situation += `. HEART score: ${data.heartScore}/10`;

        if (data.stemiCriteria === 'yes') {
            situation += '. **STEMI CRITERIA MET - CATH LAB ACTIVATED**';
        }

        return situation + '.';
    },

    /**
     * Format Background section for Cardiac
     */
    formatCardiacBackground(data) {
        let background = '';

        // Cardiac risk factors
        if (data.riskFactors && data.riskFactors.length > 0) {
            background += `Cardiac Risk Factors: ${data.riskFactors.join(', ')}. `;
        }

        // Medical history
        if (data.medicalHistory && data.medicalHistory.length > 0) {
            background += `Past Medical History: ${data.medicalHistory.join(', ')}. `;
        }

        // Medications
        if (data.medications && data.medications.length > 0) {
            background += `Current Medications: ${data.medications.join(', ')}. `;
        }

        // Allergies
        if (data.allergies && data.allergies.length > 0) {
            background += `Allergies: ${data.allergies.join(', ')}. `;
        } else {
            background += `Allergies: NKDA. `;
        }

        // Associated symptoms
        if (data.associatedSymptoms && data.associatedSymptoms.length > 0) {
            background += `Associated Symptoms: ${data.associatedSymptoms.join(', ')}.`;
        }

        return background || 'No significant cardiac history documented.';
    },

    /**
     * Format Assessment section for Cardiac
     */
    formatCardiacAssessment(data) {
        let assessment = '';

        // HEART Score
        const maceRisk = data.heartScore <= 3 ? '1.7%' :
                        data.heartScore <= 6 ? '16.6%' :
                        '50-65%';

        assessment += `HEART Score: ${data.heartScore}/10 (${data.heartRiskLevel} - ${maceRisk} 6-week MACE risk)\n`;
        assessment += `  - History (clinical suspicion): ${data.historyScore}/2\n`;
        assessment += `  - EKG findings: ${data.ekgScore}/2\n`;
        assessment += `  - Age: ${data.ageScore}/2\n`;
        assessment += `  - Risk factors: ${data.riskFactors.length > 0 ? data.riskFactors.join(', ') : 'None documented'}\n`;
        assessment += `  - Troponin: ${data.troponinScore}/2\n`;

        // Vital Signs
        if (data.vitalSigns && Object.keys(data.vitalSigns).length > 0) {
            assessment += `\nCurrent Vital Signs:\n`;
            assessment += `  - Heart Rate: ${data.vitalSigns.heartRate} bpm\n`;
            assessment += `  - Blood Pressure: ${data.vitalSigns.bloodPressure} mmHg\n`;
            assessment += `  - Respiratory Rate: ${data.vitalSigns.respiratoryRate}/min\n`;
            assessment += `  - SpO2: ${data.vitalSigns.o2Saturation}%\n`;
        }

        // ECG Findings
        assessment += `\n12-Lead ECG:\n`;
        assessment += `  - Rhythm: ${data.ecgRhythm}\n`;

        if (data.stChanges) {
            if (data.stChanges.stElevation) {
                assessment += `  - ST Elevation: ${data.stChanges.stElevationLeads || 'Yes'}\n`;
            }
            if (data.stChanges.stDepression) {
                assessment += `  - ST Depression: ${data.stChanges.stDepressionLeads || 'Yes'}\n`;
            }
            if (data.stChanges.tWaveInversion) {
                assessment += `  - T-wave Inversions: ${data.stChanges.tWaveLeads || 'Yes'}\n`;
            }
            if (data.stChanges.qWaves) {
                assessment += `  - Pathological Q Waves: ${data.stChanges.qWaveLeads || 'Yes'}\n`;
            }
        }

        if (data.stemiCriteria === 'yes') {
            assessment += `  - **STEMI CRITERIA: POSITIVE**\n`;
        }

        // Labs
        if (data.labs && Object.keys(data.labs).length > 0) {
            assessment += `\nLaboratory Values:\n`;
            if (data.labs.troponinValue) assessment += `  - Troponin: ${data.labs.troponinValue} ng/mL (drawn at ${data.labs.troponinTime || 'time not documented'})\n`;
            if (data.labs.bnpValue) assessment += `  - BNP: ${data.labs.bnpValue}\n`;
            if (data.labs.bmpResults) assessment += `  - BMP: ${data.labs.bmpResults}\n`;
            if (data.labs.cbcResults) assessment += `  - CBC: ${data.labs.cbcResults}\n`;
        }

        return assessment;
    },

    /**
     * Format Recommendation section for Cardiac
     */
    formatCardiacRecommendation(data) {
        let recommendation = '';

        // STEMI pathway
        if (data.stemiCriteria === 'yes') {
            recommendation += '**STEMI PATHWAY ACTIVATED**\n';
            recommendation += 'Immediate Actions Required:\n';
            recommendation += '  ☑ Activate cath lab (door-to-balloon time <90 minutes)\n';
            recommendation += '  ☑ Cardiology consult STAT\n';
            recommendation += '  ☑ Aspirin 324mg PO (if not already given)\n';
            recommendation += '  ☑ Dual antiplatelet therapy (Clopidogrel/Ticagrelor)\n';
            recommendation += '  ☑ Anticoagulation (Heparin bolus + infusion)\n';
            recommendation += '  ☑ Continuous cardiac monitoring\n';
            recommendation += '  ☑ Admission to CCU\n\n';
        } else {
            // Risk-based recommendations
            if (data.heartScore <= 3) {
                recommendation += 'Low HEART Score (0-3): Low risk for MACE\n';
                recommendation += 'Recommendation: Consider discharge home with cardiology follow-up in 72 hours\n';
                recommendation += '  - Stress test within 72 hours (outpatient)\n';
                recommendation += '  - Return precautions provided\n';
                recommendation += '  - Follow-up with primary care or cardiologist\n\n';
            } else if (data.heartScore <= 6) {
                recommendation += 'Moderate HEART Score (4-6): Moderate risk for MACE\n';
                recommendation += 'Recommendation: Observation unit for serial troponins and monitoring\n';
                recommendation += '  - Serial troponins (0, 3, 6 hours)\n';
                recommendation += '  - Continuous telemetry monitoring\n';
                recommendation += '  - Consider stress test or CT coronary angiography\n';
                recommendation += '  - Cardiology consultation\n\n';
            } else {
                recommendation += 'High HEART Score (7-10): High risk for MACE\n';
                recommendation += 'Recommendation: Admit to telemetry or CCU\n';
                recommendation += '  - Cardiology consult\n';
                recommendation += '  - Serial troponins and ECGs\n';
                recommendation += '  - Consider early invasive strategy (cardiac catheterization)\n';
                recommendation += '  - Optimal medical therapy (antiplatelet, statin, beta-blocker)\n\n';
            }
        }

        // Medications administered
        if (data.medicationsGiven && data.medicationsGiven.length > 0) {
            recommendation += 'Medications Administered:\n';
            data.medicationsGiven.forEach(med => {
                recommendation += `  ☑ ${med}\n`;
            });
            recommendation += '\n';
        }

        // Cath lab activation
        if (data.cathLabTime) {
            recommendation += `Cath Lab/Cardiology: Scheduled for ${data.cathLabTime}\n\n`;
        }

        // Disposition
        recommendation += `Disposition: ${data.disposition}\n`;

        if (data.dispositionInstructions) {
            recommendation += `\nDisposition Instructions:\n${data.dispositionInstructions}\n`;
        }

        if (data.additionalNotes) {
            recommendation += `\nAdditional Notes:\n${data.additionalNotes}\n`;
        }

        recommendation += '\nContinue cardiac monitoring and reassess per protocol.';

        return recommendation;
    },

    /**
     * Generate SBAR for Code Blue Assessment
     */
    generateCodeBlueSBAR(data) {
        return {
            situation: this.formatCodeBlueSituation({
                codeCalledTime: data.codeCalledTime || 'Not documented',
                location: data.location || 'Not specified',
                initialRhythm: data.initialRhythm || 'Not documented',
                witnessed: data.witnessed || 'Unknown',
                patientAge: data.patientAge || 'Unknown',
                patientGender: data.patientGender || 'Unknown'
            }),

            background: this.formatCodeBlueBackground({
                medicalHistory: data.medicalHistory || [],
                medications: data.medications || [],
                allergies: data.allergies || [],
                reasonForAdmission: data.reasonForAdmission || 'Not documented',
                codeStatus: data.codeStatus || 'Full code'
            }),

            assessment: this.formatCodeBlueAssessment({
                cprStartTime: data.cprStartTime || '',
                teamRoles: data.teamRoles || {},
                interventions: data.interventions || [],
                medications: data.medications || [],
                defibrillations: data.defibrillations || [],
                roscTime: data.roscTime || '',
                codeDuration: data.codeDuration || 'Unknown'
            }),

            recommendation: this.formatCodeBlueRecommendation({
                outcome: data.outcome || 'Pending',
                roscTime: data.roscTime || '',
                codeEndTime: data.codeEndTime || '',
                familyNotified: data.familyNotified || 'Not documented',
                familyNotifiedBy: data.familyNotifiedBy || '',
                debriefingCompleted: data.debriefingCompleted || false,
                debriefingNotes: data.debriefingNotes || '',
                additionalNotes: data.additionalNotes || ''
            })
        };
    },

    /**
     * Format Situation section for Code Blue
     */
    formatCodeBlueSituation(data) {
        let situation = `Code Blue called at ${data.codeCalledTime} in ${data.location}. `;
        situation += `${data.patientAge} year old ${data.patientGender} patient. `;
        situation += `Initial rhythm: ${data.initialRhythm}. `;
        situation += `Event was ${data.witnessed.toLowerCase()}.`;

        return situation;
    },

    /**
     * Format Background section for Code Blue
     */
    formatCodeBlueBackground(data) {
        let background = '';

        background += `Reason for admission/visit: ${data.reasonForAdmission}. `;

        if (data.medicalHistory && data.medicalHistory.length > 0) {
            background += `Relevant medical history: ${data.medicalHistory.join(', ')}. `;
        }

        if (data.medications && data.medications.length > 0) {
            background += `Home medications: ${data.medications.join(', ')}. `;
        }

        if (data.allergies && data.allergies.length > 0) {
            background += `Allergies: ${data.allergies.join(', ')}. `;
        } else {
            background += `Allergies: NKDA. `;
        }

        background += `Code status: ${data.codeStatus}.`;

        return background || 'No significant background information documented.';
    },

    /**
     * Format Assessment section for Code Blue
     */
    formatCodeBlueAssessment(data) {
        let assessment = '';

        // Timeline of events
        assessment += 'Timeline of Events:\n';
        if (data.cprStartTime) {
            assessment += `  - CPR initiated: ${data.cprStartTime}\n`;
        }

        // Team roles
        if (data.teamRoles && Object.keys(data.teamRoles).length > 0) {
            assessment += '\nCode Blue Team:\n';
            if (data.teamRoles.codeLeader) assessment += `  - Code Leader: ${data.teamRoles.codeLeader}\n`;
            if (data.teamRoles.compressor1) assessment += `  - Compressor: ${data.teamRoles.compressor1}\n`;
            if (data.teamRoles.airway) assessment += `  - Airway Manager: ${data.teamRoles.airway}\n`;
            if (data.teamRoles.medRN) assessment += `  - Medication RN: ${data.teamRoles.medRN}\n`;
            if (data.teamRoles.recorder) assessment += `  - Recorder: ${data.teamRoles.recorder}\n`;
        }

        // Interventions performed
        if (data.interventions && data.interventions.length > 0) {
            assessment += '\nInterventions Performed:\n';
            data.interventions.forEach(intervention => {
                assessment += `  - ${intervention.time}: ${intervention.description}\n`;
            });
        }

        // Defibrillation attempts
        if (data.defibrillations && data.defibrillations.length > 0) {
            assessment += '\nDefibrillation Attempts:\n';
            data.defibrillations.forEach((defib, index) => {
                assessment += `  - Shock ${index + 1} at ${defib.time}: ${defib.joules}J - Result: ${defib.result}\n`;
            });
        }

        // Medications administered
        if (data.medications && data.medications.length > 0) {
            assessment += '\nMedications Administered:\n';
            data.medications.forEach(med => {
                assessment += `  - ${med.time}: ${med.medication} ${med.dose} ${med.route}\n`;
            });
        }

        // ROSC status
        if (data.roscTime) {
            assessment += `\nROSC (Return of Spontaneous Circulation): ACHIEVED at ${data.roscTime}\n`;
        } else {
            assessment += `\nROSC: NOT achieved\n`;
        }

        // Code duration
        assessment += `\nTotal code duration: ${data.codeDuration}`;

        return assessment;
    },

    /**
     * Format Recommendation section for Code Blue
     */
    formatCodeBlueRecommendation(data) {
        let recommendation = '';

        // Outcome-based recommendations
        if (data.outcome.includes('Survived') || data.outcome.includes('ROSC')) {
            recommendation += '**POST-ROSC CARE INITIATED**\n';
            recommendation += 'Immediate Actions Required:\n';
            recommendation += '  ☑ Transfer to ICU for post-cardiac arrest care\n';
            recommendation += '  ☑ Initiate targeted temperature management (TTM) protocol\n';
            recommendation += '  ☑ Continuous cardiac monitoring and frequent neuro checks\n';
            recommendation += '  ☑ Obtain 12-lead ECG - consider cardiac catheterization if STEMI\n';
            recommendation += '  ☑ Optimize hemodynamics (MAP >65 mmHg)\n';
            recommendation += '  ☑ Mechanical ventilation with lung-protective strategy\n';
            recommendation += '  ☑ Avoid hypoxia and hyperoxia (SpO2 94-98%)\n';
            recommendation += '  ☑ Stat labs: ABG, lactate, troponin, BMP, CBC, coags\n';
            recommendation += '  ☑ Cardiology consultation\n\n';
        } else if (data.outcome.includes('Expired')) {
            recommendation += '**RESUSCITATION CEASED**\n';
            const timeOfDeath = data.codeEndTime || 'Time not documented';
            recommendation += `Time of death declared: ${timeOfDeath}\n\n`;
            recommendation += 'Post-Event Actions:\n';
            recommendation += '  ☑ Physician certified death\n';
            recommendation += '  ☑ Family notification completed\n';
            recommendation += '  ☑ Organ donation/procurement contacted (if applicable)\n';
            recommendation += '  ☑ Medical examiner/coroner notification (if required)\n';
            recommendation += '  ☑ Post-code team debriefing scheduled\n\n';
        }

        // Family notification
        recommendation += `Family Notification: ${data.familyNotified}`;
        if (data.familyNotifiedBy) {
            recommendation += ` by ${data.familyNotifiedBy}`;
        }
        recommendation += '\n\n';

        // Debriefing
        if (data.debriefingCompleted) {
            recommendation += 'Team Debriefing: Completed\n';
            if (data.debriefingNotes) {
                recommendation += `Notes: ${data.debriefingNotes}\n`;
            }
        } else {
            recommendation += 'Team Debriefing: Recommend scheduling within 24 hours for all team members\n';
        }

        // Additional notes
        if (data.additionalNotes) {
            recommendation += `\nAdditional Notes:\n${data.additionalNotes}\n`;
        }

        recommendation += '\nComplete Code Blue documentation submitted to medical record per hospital policy.';

        return recommendation;
    },

    /**
     * Generate SBAR for Blood Transfusion
     */
    generateBloodTransfusionSBAR(data) {
        return {
            situation: this.formatBloodTransfusionSituation({
                patientName: data.patientName || 'Patient',
                patientMrn: data.patientMrn || 'Not documented',
                productType: data.productType || 'Not specified',
                unitNumber: data.unitNumber || 'Not documented',
                indication: data.indication || 'Blood transfusion administration',
                patientBloodType: data.patientBloodType || 'Type & Screen on file'
            }),

            background: this.formatBloodTransfusionBackground({
                transfusionHistory: data.transfusionHistory || 'No prior transfusion reactions',
                allergies: data.allergies || [],
                currentHemoglobin: data.currentHemoglobin || 'Not documented',
                indication: data.indication || 'Blood transfusion administration'
            }),

            assessment: this.formatBloodTransfusionAssessment({
                nurse1Name: data.nurse1Name || 'Nurse 1',
                nurse2Name: data.nurse2Name || 'Nurse 2',
                verificationCompleted: data.verificationCompleted || false,
                verificationTime: data.verificationTime || 'Not documented',
                unitNumber: data.unitNumber || 'Not documented',
                unitExpiration: data.unitExpiration || 'Verified within date',
                bloodTypeVerification: data.bloodTypeVerification || 'Verified compatible',
                baselineVitals: data.baselineVitals || {},
                monitoringVitals: data.monitoringVitals || {},
                postVitals: data.postVitals || {},
                transfusionStartTime: data.transfusionStartTime || 'Not documented',
                volumeTransfused: data.volumeTransfused || 'Not documented',
                transfusionRate: data.transfusionRate || 'Not documented',
                reactionsObserved: data.reactionsObserved || false,
                reactionDetails: data.reactionDetails || 'No adverse reactions observed',
                reactionType: data.reactionType || 'None',
                patientTolerance: data.patientTolerance || 'Not assessed',
                ivGauge: data.ivGauge || 'Not documented',
                consentVerified: data.consentVerified || false
            }),

            recommendation: this.formatBloodTransfusionRecommendation({
                postTransfusionLabs: data.postTransfusionLabs || 'Ordered per protocol',
                reactionsObserved: data.reactionsObserved || false,
                patientTolerance: data.patientTolerance || 'Not assessed',
                outcomeSummary: data.outcomeSummary || 'Transfusion completed per protocol'
            })
        };
    },

    /**
     * Format Situation section for Blood Transfusion
     */
    formatBloodTransfusionSituation(data) {
        return `Patient ${data.patientName} (MRN: ${data.patientMrn}) receiving ${data.productType}, Unit #${data.unitNumber}. Indication: ${data.indication}. Patient blood type: ${data.patientBloodType}.`;
    },

    /**
     * Format Background section for Blood Transfusion
     */
    formatBloodTransfusionBackground(data) {
        let background = '';

        background += `Transfusion History: ${data.transfusionHistory}. `;

        if (data.allergies && data.allergies.length > 0) {
            background += `Allergies: ${data.allergies.join(', ')}. `;
        } else {
            background += `Allergies: NKDA. `;
        }

        if (data.currentHemoglobin && data.currentHemoglobin !== 'Not documented') {
            background += `Current Hemoglobin: ${data.currentHemoglobin} g/dL. `;
        }

        background += `Indication for transfusion: ${data.indication}.`;

        return background;
    },

    /**
     * Format Assessment section for Blood Transfusion
     */
    formatBloodTransfusionAssessment(data) {
        let assessment = '';

        // Product Verification
        assessment += `Product Verification (Two-Person Check):\n`;
        assessment += `  - Verified by: ${data.nurse1Name} and ${data.nurse2Name}\n`;
        assessment += `  - Verification time: ${data.verificationTime}\n`;
        assessment += `  - Unit number: ${data.unitNumber}\n`;
        assessment += `  - Expiration date: ${data.unitExpiration}\n`;
        assessment += `  - Blood type compatibility: ${data.bloodTypeVerification}\n`;
        assessment += `  - Verification status: ${data.verificationCompleted ? 'COMPLETED ✓' : 'INCOMPLETE'}\n`;

        // Pre-transfusion details
        assessment += `\nPre-Transfusion:\n`;
        assessment += `  - Informed consent: ${data.consentVerified ? 'Verified ✓' : 'Not verified'}\n`;
        assessment += `  - IV access: ${data.ivGauge} gauge\n`;

        // Baseline Vitals
        assessment += `\nBaseline Vital Signs:\n`;
        assessment += `  - Blood Pressure: ${data.baselineVitals.bloodPressure || 'Not documented'}\n`;
        assessment += `  - Heart Rate: ${data.baselineVitals.heartRate || 'Not documented'} bpm\n`;
        assessment += `  - Temperature: ${data.baselineVitals.temperature || 'Not documented'}°F\n`;

        // Transfusion details
        assessment += `\nTransfusion Administration:\n`;
        assessment += `  - Start time: ${data.transfusionStartTime}\n`;
        assessment += `  - Volume transfused: ${data.volumeTransfused} mL\n`;
        assessment += `  - Transfusion rate: ${data.transfusionRate} mL/hr\n`;

        // Monitoring vitals
        if (data.monitoringVitals) {
            assessment += `\nVital Signs Monitoring (Every 15 minutes):\n`;
            if (data.monitoringVitals.baseline) {
                assessment += `  - Baseline: BP ${data.monitoringVitals.baseline.bp || 'N/A'}, HR ${data.monitoringVitals.baseline.hr || 'N/A'}, Temp ${data.monitoringVitals.baseline.temp || 'N/A'}°F\n`;
            }
            if (data.monitoringVitals.min15) {
                assessment += `  - 15 min: BP ${data.monitoringVitals.min15.bp || 'N/A'}, HR ${data.monitoringVitals.min15.hr || 'N/A'}, Temp ${data.monitoringVitals.min15.temp || 'N/A'}°F\n`;
            }
            if (data.monitoringVitals.min30) {
                assessment += `  - 30 min: BP ${data.monitoringVitals.min30.bp || 'N/A'}, HR ${data.monitoringVitals.min30.hr || 'N/A'}, Temp ${data.monitoringVitals.min30.temp || 'N/A'}°F\n`;
            }
            if (data.monitoringVitals.min60) {
                assessment += `  - 60 min: BP ${data.monitoringVitals.min60.bp || 'N/A'}, HR ${data.monitoringVitals.min60.hr || 'N/A'}, Temp ${data.monitoringVitals.min60.temp || 'N/A'}°F\n`;
            }
        }

        // Post-transfusion vitals
        assessment += `\nPost-Transfusion Vital Signs:\n`;
        assessment += `  - Blood Pressure: ${data.postVitals.bloodPressure || 'Not documented'}\n`;
        assessment += `  - Heart Rate: ${data.postVitals.heartRate || 'Not documented'} bpm\n`;
        assessment += `  - Temperature: ${data.postVitals.temperature || 'Not documented'}°F\n`;

        // Adverse reactions
        assessment += `\nAdverse Reactions:\n`;
        if (data.reactionsObserved) {
            assessment += `  - Reaction observed: YES\n`;
            assessment += `  - Reaction type: ${data.reactionType}\n`;
            assessment += `  - Details: ${data.reactionDetails}\n`;
        } else {
            assessment += `  - No adverse reactions observed ✓\n`;
        }

        // Patient tolerance
        assessment += `\nPatient Tolerance: ${this.formatToleranceLevel(data.patientTolerance)}\n`;

        return assessment;
    },

    /**
     * Format tolerance level for display
     */
    formatToleranceLevel(tolerance) {
        const toleranceLevels = {
            'excellent': 'Excellent - No adverse reactions',
            'good': 'Good - Mild symptoms, resolved',
            'fair': 'Fair - Moderate symptoms, monitored',
            'poor': 'Poor - Significant adverse reaction'
        };
        return toleranceLevels[tolerance] || tolerance || 'Not assessed';
    },

    /**
     * Format Recommendation section for Blood Transfusion
     */
    formatBloodTransfusionRecommendation(data) {
        let recommendation = '';

        if (data.reactionsObserved) {
            recommendation += `ADVERSE REACTION DOCUMENTED\n`;
            recommendation += `Continue to monitor patient closely for delayed reactions.\n`;
            recommendation += `Physician notified of reaction.\n`;
            recommendation += `Consider pre-medication for future transfusions.\n\n`;
        } else {
            recommendation += `Transfusion completed without adverse reactions.\n\n`;
        }

        // Post-transfusion care
        recommendation += `Post-Transfusion Care:\n`;
        recommendation += `  - Post-transfusion labs: ${data.postTransfusionLabs}\n`;
        recommendation += `  - Continue monitoring for delayed reactions (24-48 hours)\n`;
        recommendation += `  - Patient/family educated on signs of delayed reactions\n`;

        if (data.patientTolerance === 'poor' || data.patientTolerance === 'fair') {
            recommendation += `  - Enhanced monitoring recommended due to tolerance level\n`;
        }

        // Repeat transfusions
        recommendation += `\nFor Future Transfusions:\n`;
        if (data.reactionsObserved) {
            recommendation += `  - Pre-medication recommended (diphenhydramine, acetaminophen)\n`;
            recommendation += `  - Slower transfusion rate may be indicated\n`;
            recommendation += `  - Consider washed/leukoreduced products\n`;
        } else {
            recommendation += `  - Standard transfusion protocol may continue\n`;
            recommendation += `  - Repeat type & screen if needed\n`;
        }

        recommendation += `\n${data.outcomeSummary}`;

        return recommendation;
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
