/**
 * SBAR Wizard React Component
 * Professional clinical documentation with AI assistance and interactive tour
 */

import React, { useEffect, useState } from 'react';
import Joyride, { Step, CallBackProps, STATUS } from 'react-joyride';
import { useSbarWizardStore } from '@/lib/store';
import type { SbarData } from '@/types';

// Step configurations
const SBAR_STEPS: Array<{
  section: keyof SbarData;
  title: string;
  prompt: string;
  placeholder: string;
  helpText: string;
}> = [
  {
    section: 'situation',
    title: 'Situation',
    prompt: 'Describe the current patient situation and reason for communication',
    placeholder: 'e.g., "Experiencing acute chest pain for past 30 minutes, rating 8/10. Patient appears diaphoretic and anxious..."',
    helpText: 'Describe the immediate concern and reason for this communication',
  },
  {
    section: 'background',
    title: 'Background',
    prompt: 'Provide relevant patient background and medical history',
    placeholder: 'e.g., "68 y/o male, admitted 3 days ago for COPD exacerbation. History of HTN, DM2..."',
    helpText: 'Include admission date, diagnosis, allergies, current medications',
  },
  {
    section: 'assessment',
    title: 'Assessment',
    prompt: 'Share your clinical assessment and current findings',
    placeholder: 'e.g., "Patient appears anxious and in moderate distress. Skin cool and clammy. Lungs with crackles bilaterally..."',
    helpText: 'Describe physical findings, mental status, and your clinical judgment',
  },
  {
    section: 'recommendation',
    title: 'Recommendation',
    prompt: 'State your recommendations and what you need',
    placeholder: 'e.g., "Request immediate physician evaluation. Consider transfer to higher level of care..."',
    helpText: 'Be specific about actions needed and priority level',
  },
];

// Joyride tour steps - only showing elements that are always visible
const TOUR_STEPS: Step[] = [
  {
    target: '.sbar-wizard-container',
    content: (
      <div>
        <p className="mb-2">Welcome to the SBAR Wizard! This tool helps you create professional clinical handoff reports with AI assistance.</p>
        <p className="text-sm text-gray-600 mt-3 pt-2 border-t border-gray-200">
          💡 <strong>Tip:</strong> Press <kbd className="px-2 py-1 bg-gray-100 rounded border border-gray-300">ESC</kbd> anytime to exit this tour
        </p>
      </div>
    ),
    disableBeacon: true,
  },
  {
    target: '.sbar-step-indicator',
    content: 'Track your progress through the 4 SBAR sections: Situation, Background, Assessment, and Recommendation.',
  },
  {
    target: '.sbar-textarea',
    content: 'Enter your clinical notes here. You can use informal language - AI will help professionalize it.',
  },
  {
    target: '.ai-enhance-btn',
    content: 'Click "Enhance with AI" to convert your notes into professional clinical language following SBAR best practices. This button appears on all steps.',
  },
  {
    target: '.sbar-navigation',
    content: 'Navigate through the wizard using these buttons. Your work is saved automatically in your browser. Additional AI features (Priority Suggestion, Medication Checks) appear on relevant steps.',
  },
];

export const SbarWizard: React.FC = () => {
  const {
    currentStep,
    formData,
    formErrors,
    isLoading,
    error,
    isEnhancing,
    enhancementResult,
    isPriorityChecking,
    suggestedPriority,
    priorityReasoning,
    isMedicationChecking,
    medicationResults,
    isCompleted,
    finalReport,
    startWizard,
    nextStep,
    previousStep,
    updateFormData,
    enhanceText,
    checkPriority,
    checkMedications,
    reset,
  } = useSbarWizardStore();

  const [runTour, setRunTour] = useState(false);
  const [showEnhancementModal, setShowEnhancementModal] = useState(false);
  const [hasSeenTour, setHasSeenTour] = useState(false);
  const [showPulse, setShowPulse] = useState(false);

  // Vital signs state (for Assessment step)
  const [vitalSigns, setVitalSigns] = useState({
    temperature: '',
    bloodPressure: '',
    heartRate: '',
    respiratoryRate: '',
    oxygenSaturation: '',
    painLevel: '',
  });

  // Patient info state (for Situation step)
  const [patientInfo, setPatientInfo] = useState({
    patientId: '',
    location: '',
  });

  const currentStepConfig = SBAR_STEPS[currentStep - 1];

  useEffect(() => {
    const state = useSbarWizardStore.getState();
    // Only start wizard if we don't have an ID OR if there's an error suggesting session is invalid
    if (!state.wizardId || (state.error && state.error.includes('session'))) {
      startWizard().catch((err) => {
        console.error('Failed to start wizard:', err);
        // Clear potentially corrupted state and retry once
        useSbarWizardStore.persist.clearStorage();
        setTimeout(() => startWizard(), 100);
      });
    }
  }, [startWizard]);

  // Auto-launch tour on first visit (after page load)
  useEffect(() => {
    // Check if user has seen the tour before
    const tourSeen = localStorage.getItem('sbarTourSeen');

    if (!tourSeen) {
      // Wait for page to fully load, then start tour
      const timer = setTimeout(() => {
        setRunTour(true);
        setShowPulse(false); // Stop pulse when tour starts
      }, 2500); // 2.5 second delay after page load

      // Show pulse on Help button while waiting
      setShowPulse(true);

      return () => clearTimeout(timer);
    } else {
      setHasSeenTour(true);
    }
  }, []);

  const handleJoyrideCallback = (data: CallBackProps) => {
    const { status } = data;
    if ([STATUS.FINISHED, STATUS.SKIPPED].includes(status)) {
      setRunTour(false);
      setHasSeenTour(true);
      // Mark tour as seen in localStorage
      localStorage.setItem('sbarTourSeen', 'true');
      // Keep pulse for 30 seconds after skipping, then stop
      if (status === STATUS.SKIPPED) {
        setShowPulse(true);
        setTimeout(() => setShowPulse(false), 30000);
      }
    }
  };

  const handleEnhance = async () => {
    // Automatically prepend structured data before enhancing
    let textToEnhance = formData[currentStepConfig.section] || '';

    // For Situation step: prepend patient info if provided
    if (currentStepConfig.section === 'situation' && (patientInfo.patientId || patientInfo.location)) {
      const patientText = `Patient: ${patientInfo.patientId || '[Not specified]'}\nLocation: ${patientInfo.location || '[Not specified]'}\n\n`;
      // Only prepend if not already included
      if (!textToEnhance.includes(patientText)) {
        textToEnhance = patientText + textToEnhance;
        updateFormData('situation', textToEnhance);
      }
    }

    // For Assessment step: prepend vital signs if provided
    if (currentStepConfig.section === 'assessment') {
      const hasVitals = vitalSigns.temperature || vitalSigns.bloodPressure ||
                        vitalSigns.heartRate || vitalSigns.respiratoryRate ||
                        vitalSigns.oxygenSaturation;
      if (hasVitals) {
        const vs = `Vital Signs: Temp ${vitalSigns.temperature || '?'}°F, BP ${vitalSigns.bloodPressure || '?'}, HR ${vitalSigns.heartRate || '?'} bpm, RR ${vitalSigns.respiratoryRate || '?'}, O₂ Sat ${vitalSigns.oxygenSaturation || '?'}%${vitalSigns.painLevel ? `, Pain ${vitalSigns.painLevel}/10` : ''}.\n\n`;
        // Only prepend if not already included
        if (!textToEnhance.includes('Vital Signs:')) {
          textToEnhance = vs + textToEnhance;
          updateFormData('assessment', textToEnhance);
        }
      }
    }

    await enhanceText(currentStepConfig.section);
    setShowEnhancementModal(true);
  };

  const applyEnhancement = () => {
    if (enhancementResult) {
      updateFormData(currentStepConfig.section, enhancementResult);
      setShowEnhancementModal(false);
    }
  };

  const handleCheckMedications = async () => {
    if (currentStepConfig.section === 'background') {
      await checkMedications();
    }
  };

  const handleCheckPriority = async () => {
    if (currentStepConfig.section === 'assessment') {
      await checkPriority();
    }
  };

  if (isCompleted && finalReport) {
    return (
      <div className="sbar-wizard-container max-w-4xl mx-auto p-6">
        <div className="card">
          <h2 className="text-2xl font-bold text-green-600 mb-4 flex items-center">
            <i className="fas fa-check-circle mr-2"></i>
            SBAR Report Complete
          </h2>

          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-bold text-lg mb-2">Situation</h3>
              <p className="whitespace-pre-wrap">{finalReport.situation}</p>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-bold text-lg mb-2">Background</h3>
              <p className="whitespace-pre-wrap">{finalReport.background}</p>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-bold text-lg mb-2">Assessment</h3>
              <p className="whitespace-pre-wrap">{finalReport.assessment}</p>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-bold text-lg mb-2">Recommendation</h3>
              <p className="whitespace-pre-wrap">{finalReport.recommendation}</p>
            </div>
          </div>

          <div className="mt-6 flex gap-3">
            <button
              onClick={() => {
                const reportText = `SBAR REPORT\n\nSITUATION:\n${finalReport.situation}\n\nBACKGROUND:\n${finalReport.background}\n\nASSESSMENT:\n${finalReport.assessment}\n\nRECOMMENDATION:\n${finalReport.recommendation}`;

                const blob = new Blob([reportText], { type: 'text/plain' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `SBAR_Report_${new Date().toISOString().slice(0, 10)}.txt`;
                a.click();
                window.URL.revokeObjectURL(url);
              }}
              className="btn btn-primary"
            >
              <i className="fas fa-download mr-2"></i>
              Download Report
            </button>

            <button
              onClick={() => {
                const reportText = `SBAR REPORT\n\nSITUATION:\n${finalReport.situation}\n\nBACKGROUND:\n${finalReport.background}\n\nASSESSMENT:\n${finalReport.assessment}\n\nRECOMMENDATION:\n${finalReport.recommendation}`;
                navigator.clipboard.writeText(reportText);
                alert('Report copied to clipboard!');
              }}
              className="btn btn-secondary"
            >
              <i className="fas fa-copy mr-2"></i>
              Copy to Clipboard
            </button>

            <button onClick={reset} className="btn btn-secondary">
              <i className="fas fa-plus mr-2"></i>
              New Report
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <Joyride
        steps={TOUR_STEPS}
        run={runTour}
        continuous
        showProgress
        showSkipButton
        callback={handleJoyrideCallback}
        styles={{
          options: {
            primaryColor: '#d4af37', // Gold accent color
            zIndex: 10000,
          },
        }}
      />

      <div className="sbar-wizard-container max-w-4xl mx-auto p-6">
        <div className="card">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">SBAR Wizard</h1>
            <button
              onClick={() => setRunTour(true)}
              className={`btn bg-accent-500 text-white hover:bg-accent-600 text-sm ${
                showPulse ? 'animate-pulse' : ''
              }`}
              title="Quick tour - Press ESC anytime to exit"
            >
              <i className="fas fa-question-circle mr-2"></i>
              {!hasSeenTour && showPulse ? 'New? Take Quick Tour!' : 'Help'}
            </button>
          </div>

          {/* Step Indicator */}
          <div className="sbar-step-indicator mb-8">
            <div className="flex justify-between">
              {SBAR_STEPS.map((step, index) => (
                <div
                  key={step.section}
                  className={`flex-1 text-center ${
                    index < SBAR_STEPS.length - 1 ? 'border-r border-gray-300' : ''
                  }`}
                >
                  <div
                    className={`inline-flex items-center justify-center w-10 h-10 rounded-full mb-2 ${
                      currentStep > index + 1
                        ? 'bg-green-500 text-white'
                        : currentStep === index + 1
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-600'
                    }`}
                  >
                    {currentStep > index + 1 ? (
                      <i className="fas fa-check"></i>
                    ) : (
                      index + 1
                    )}
                  </div>
                  <div className="text-sm font-medium">{step.title}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {/* Current Step */}
          <div className="mb-6">
            <h2 className="text-2xl font-bold mb-2">{currentStepConfig.title}</h2>
            <p className="text-gray-600 mb-4">{currentStepConfig.prompt}</p>
            <p className="text-sm text-gray-500 mb-4">
              <i className="fas fa-info-circle mr-2"></i>
              {currentStepConfig.helpText}
            </p>

            {/* Patient Info (Situation step only) */}
            {currentStepConfig.section === 'situation' && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                <h3 className="font-semibold text-green-900 mb-3 flex items-center">
                  <i className="fas fa-id-card mr-2"></i>
                  Patient Information
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Patient ID / Name
                    </label>
                    <input
                      type="text"
                      placeholder="e.g., John Doe, MRN: 123456"
                      className="input text-sm"
                      value={patientInfo.patientId}
                      onChange={(e) => setPatientInfo({...patientInfo, patientId: e.target.value})}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Location / Room
                    </label>
                    <input
                      type="text"
                      placeholder="e.g., Room 302, ICU Bed 4"
                      className="input text-sm"
                      value={patientInfo.location}
                      onChange={(e) => setPatientInfo({...patientInfo, location: e.target.value})}
                    />
                  </div>
                </div>

                <p className="mt-3 text-xs text-green-800 flex items-center">
                  <i className="fas fa-info-circle mr-2"></i>
                  This information will be automatically included when you click "Enhance with AI"
                </p>
              </div>
            )}

            {/* Vital Signs (Assessment step only) */}
            {currentStepConfig.section === 'assessment' && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <h3 className="font-semibold text-blue-900 mb-3 flex items-center">
                  <i className="fas fa-heartbeat mr-2"></i>
                  Vital Signs
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Temperature (°F)
                    </label>
                    <input
                      type="text"
                      placeholder="98.6"
                      className="input text-sm"
                      value={vitalSigns.temperature}
                      onChange={(e) => setVitalSigns({...vitalSigns, temperature: e.target.value})}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Blood Pressure
                    </label>
                    <input
                      type="text"
                      placeholder="120/80"
                      className="input text-sm"
                      value={vitalSigns.bloodPressure}
                      onChange={(e) => setVitalSigns({...vitalSigns, bloodPressure: e.target.value})}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Heart Rate (bpm)
                    </label>
                    <input
                      type="text"
                      placeholder="72"
                      className="input text-sm"
                      value={vitalSigns.heartRate}
                      onChange={(e) => setVitalSigns({...vitalSigns, heartRate: e.target.value})}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Respiratory Rate
                    </label>
                    <input
                      type="text"
                      placeholder="16"
                      className="input text-sm"
                      value={vitalSigns.respiratoryRate}
                      onChange={(e) => setVitalSigns({...vitalSigns, respiratoryRate: e.target.value})}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      O₂ Saturation (%)
                    </label>
                    <input
                      type="text"
                      placeholder="98"
                      className="input text-sm"
                      value={vitalSigns.oxygenSaturation}
                      onChange={(e) => setVitalSigns({...vitalSigns, oxygenSaturation: e.target.value})}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Pain Level (0-10)
                    </label>
                    <input
                      type="text"
                      placeholder="0"
                      className="input text-sm"
                      value={vitalSigns.painLevel}
                      onChange={(e) => setVitalSigns({...vitalSigns, painLevel: e.target.value})}
                    />
                  </div>
                </div>

                <p className="mt-3 text-xs text-blue-800 flex items-center">
                  <i className="fas fa-info-circle mr-2"></i>
                  These vital signs will be automatically included when you click "Enhance with AI"
                </p>
              </div>
            )}

            <textarea
              className="sbar-textarea textarea min-h-[200px]"
              placeholder={currentStepConfig.placeholder}
              value={formData[currentStepConfig.section] || ''}
              onChange={(e) =>
                updateFormData(currentStepConfig.section, e.target.value)
              }
              disabled={isLoading}
            />

            {formErrors[currentStepConfig.section] && (
              <p className="text-red-600 text-sm mt-2">
                {formErrors[currentStepConfig.section]}
              </p>
            )}
          </div>

          {/* AI Features */}
          <div className="flex flex-wrap gap-3 mb-6">
            <button
              onClick={handleEnhance}
              disabled={isEnhancing || !formData[currentStepConfig.section]}
              className="ai-enhance-btn btn bg-purple-600 text-white hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isEnhancing ? (
                <>
                  <i className="fas fa-spinner fa-spin mr-2"></i>
                  Enhancing...
                </>
              ) : (
                <>
                  <i className="fas fa-magic mr-2"></i>
                  Enhance with AI
                </>
              )}
            </button>

            {currentStepConfig.section === 'assessment' && (
              <button
                onClick={handleCheckPriority}
                disabled={isPriorityChecking || !formData.assessment}
                className="ai-priority-btn btn bg-orange-600 text-white hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isPriorityChecking ? (
                  <>
                    <i className="fas fa-spinner fa-spin mr-2"></i>
                    Checking...
                  </>
                ) : (
                  <>
                    <i className="fas fa-exclamation-circle mr-2"></i>
                    Suggest Priority
                  </>
                )}
              </button>
            )}

            {currentStepConfig.section === 'background' && (
              <button
                onClick={handleCheckMedications}
                disabled={isMedicationChecking || !formData.background}
                className="ai-medications-btn btn bg-red-600 text-white hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isMedicationChecking ? (
                  <>
                    <i className="fas fa-spinner fa-spin mr-2"></i>
                    Checking...
                  </>
                ) : (
                  <>
                    <i className="fas fa-pills mr-2"></i>
                    Check Interactions
                  </>
                )}
              </button>
            )}
          </div>

          {/* Priority Results */}
          {suggestedPriority && priorityReasoning && (
            <div className="bg-orange-50 border-l-4 border-orange-400 p-4 mb-6">
              <h4 className="font-bold mb-2">
                Suggested Priority: {suggestedPriority.toUpperCase()}
              </h4>
              <p className="text-sm">{priorityReasoning}</p>
            </div>
          )}

          {/* Medication Results */}
          {medicationResults && (
            <div
              className={`border-l-4 p-4 mb-6 ${
                medicationResults.has_major_interactions
                  ? 'bg-red-50 border-red-400'
                  : medicationResults.has_interactions
                  ? 'bg-yellow-50 border-yellow-400'
                  : 'bg-green-50 border-green-400'
              }`}
            >
              <h4 className="font-bold mb-2">
                {medicationResults.has_interactions
                  ? `⚠️ ${medicationResults.total_interactions} Interaction(s) Found`
                  : '✓ No Major Interactions Detected'}
              </h4>
              {medicationResults.interactions.length > 0 && (
                <ul className="text-sm space-y-2">
                  {medicationResults.interactions.map((interaction, idx) => (
                    <li key={idx}>
                      <strong>
                        {interaction.drug1} ↔ {interaction.drug2}
                      </strong>{' '}
                      ({interaction.severity}): {interaction.description}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {/* Navigation */}
          <div className="sbar-navigation flex justify-between items-center">
            <button
              onClick={previousStep}
              disabled={currentStep === 1}
              className="btn btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <i className="fas fa-arrow-left mr-2"></i>
              Previous
            </button>

            <div className="text-sm text-gray-600">
              Step {currentStep} of {SBAR_STEPS.length}
            </div>

            <button
              onClick={nextStep}
              disabled={isLoading}
              className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {currentStep === SBAR_STEPS.length ? (
                <>
                  <i className="fas fa-check mr-2"></i>
                  Complete
                </>
              ) : (
                <>
                  Next
                  <i className="fas fa-arrow-right ml-2"></i>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Enhancement Modal */}
      {showEnhancementModal && enhancementResult && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <h3 className="text-xl font-bold mb-4">AI Enhanced Text</h3>

            <div className="space-y-4">
              <div>
                <h4 className="font-semibold text-sm text-gray-600 mb-2">
                  Original:
                </h4>
                <p className="bg-gray-50 p-3 rounded whitespace-pre-wrap">
                  {formData[currentStepConfig.section]}
                </p>
              </div>

              <div>
                <h4 className="font-semibold text-sm text-gray-600 mb-2">
                  Enhanced:
                </h4>
                <p className="bg-purple-50 p-3 rounded whitespace-pre-wrap">
                  {enhancementResult}
                </p>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button onClick={applyEnhancement} className="btn btn-primary">
                <i className="fas fa-check mr-2"></i>
                Use Enhanced Version
              </button>
              <button
                onClick={() => setShowEnhancementModal(false)}
                className="btn btn-secondary"
              >
                Keep Original
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default SbarWizard;
