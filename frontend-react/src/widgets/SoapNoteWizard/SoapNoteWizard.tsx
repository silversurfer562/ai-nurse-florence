/**
 * SOAP Note Wizard React Component
 * Professional clinical progress note documentation with AI assistance
 * Following the pattern from SBAR and Shift Handoff wizards
 */

import React, { useEffect, useState } from 'react';
import Joyride, { Step, CallBackProps, STATUS } from 'react-joyride';

// API Configuration
const API_BASE_URL = '/api/v1';

// SOAP Note Data Interface
interface SoapNoteData {
  // Subjective
  chief_complaint?: string;
  history_present_illness?: string;
  patient_reported_symptoms?: string;
  pain_description?: string;
  functional_status?: string;
  patient_concerns?: string;

  // Objective
  vital_signs?: string;
  physical_exam_findings?: string;
  lab_results?: string;
  imaging_results?: string;
  medication_administration?: string;
  procedures_performed?: string;

  // Assessment
  primary_diagnosis?: string;
  differential_diagnoses?: string;
  problem_list?: string;
  progress_evaluation?: string;
  response_to_treatment?: string;
  complications_concerns?: string;

  // Plan
  diagnostic_plan?: string;
  therapeutic_plan?: string;
  patient_education?: string;
  monitoring_plan?: string;
  follow_up?: string;
  consultations_needed?: string;

  // Metadata
  note_date?: string;
}

// Step configurations matching backend SOAP_NOTE_STEPS
const SOAP_NOTE_STEPS = [
  {
    step: 1,
    title: 'Subjective - Patient\'s Experience',
    prompt: 'Document the patient\'s subjective experience and reported symptoms',
    fields: ['chief_complaint', 'history_present_illness', 'patient_reported_symptoms', 'pain_description', 'functional_status', 'patient_concerns'],
    helpText: 'Record what the patient tells you in their own words. Include chief complaint, symptoms, pain, and any concerns they express.',
  },
  {
    step: 2,
    title: 'Objective - Clinical Observations',
    prompt: 'Record objective clinical findings and measurements',
    fields: ['vital_signs', 'physical_exam_findings', 'lab_results', 'imaging_results', 'medication_administration', 'procedures_performed'],
    helpText: 'Document measurable data: vital signs, physical exam findings, lab/imaging results, medications given, procedures done.',
  },
  {
    step: 3,
    title: 'Assessment - Clinical Analysis',
    prompt: 'Provide your clinical assessment and interpretation',
    fields: ['primary_diagnosis', 'differential_diagnoses', 'problem_list', 'progress_evaluation', 'response_to_treatment', 'complications_concerns'],
    helpText: 'Analyze the data: primary diagnosis, other possibilities, current problems, patient\'s progress, treatment response, any concerns.',
  },
  {
    step: 4,
    title: 'Plan - Care Plan and Next Steps',
    prompt: 'Outline the care plan and next steps',
    fields: ['diagnostic_plan', 'therapeutic_plan', 'patient_education', 'monitoring_plan', 'follow_up', 'consultations_needed'],
    helpText: 'Detail the plan: further diagnostics needed, treatment changes, patient education, monitoring requirements, follow-up, consultations.',
  },
];

// Field labels
const FIELD_LABELS: Record<string, string> = {
  chief_complaint: 'Chief Complaint',
  history_present_illness: 'History of Present Illness (HPI)',
  patient_reported_symptoms: 'Patient-Reported Symptoms',
  pain_description: 'Pain Description',
  functional_status: 'Functional Status',
  patient_concerns: 'Patient Concerns',
  vital_signs: 'Vital Signs',
  physical_exam_findings: 'Physical Examination Findings',
  lab_results: 'Laboratory Results',
  imaging_results: 'Imaging Results',
  medication_administration: 'Medications Administered',
  procedures_performed: 'Procedures Performed',
  primary_diagnosis: 'Primary Diagnosis',
  differential_diagnoses: 'Differential Diagnoses',
  problem_list: 'Problem List',
  progress_evaluation: 'Progress Evaluation',
  response_to_treatment: 'Response to Treatment',
  complications_concerns: 'Complications/Concerns',
  diagnostic_plan: 'Diagnostic Plan',
  therapeutic_plan: 'Therapeutic Plan',
  patient_education: 'Patient Education',
  monitoring_plan: 'Monitoring Plan',
  follow_up: 'Follow-up',
  consultations_needed: 'Consultations Needed',
};

// Joyride tour steps
const TOUR_STEPS: Step[] = [
  {
    target: '.soap-note-wizard-container',
    content: (
      <div>
        <p className="mb-2">Welcome to the SOAP Note Wizard! Create professional clinical progress notes following the evidence-based SOAP format.</p>
        <p className="text-sm text-gray-600 mt-3 pt-2 border-t border-gray-200">
          💡 <strong>Tip:</strong> Press <kbd className="px-2 py-1 bg-gray-100 rounded border border-gray-300">ESC</kbd> anytime to exit this tour
        </p>
      </div>
    ),
    disableBeacon: true,
  },
  {
    target: '.soap-note-step-indicator',
    content: 'Track your progress through the 4 SOAP sections: Subjective, Objective, Assessment, and Plan.',
  },
  {
    target: '.soap-note-form',
    content: 'Fill in relevant clinical information. Not all fields are required - document what\'s clinically significant.',
  },
  {
    target: '.ai-enhance-btn',
    content: 'Use AI to enhance your notes into professional clinical language. Available on narrative fields.',
  },
  {
    target: '.soap-note-navigation',
    content: 'Navigate through the wizard. Your work is saved automatically in your browser.',
  },
];

export const SoapNoteWizard: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [wizardId, setWizardId] = useState<string | null>(null);
  const [formData, setFormData] = useState<SoapNoteData>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [enhancementResult, setEnhancementResult] = useState<string | null>(null);
  const [enhancingField, setEnhancingField] = useState<string | null>(null);
  const [showEnhancementModal, setShowEnhancementModal] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [finalReport, setFinalReport] = useState<any>(null);
  const [runTour, setRunTour] = useState(false);
  const [hasSeenTour, setHasSeenTour] = useState(false);
  const [showPulse, setShowPulse] = useState(false);

  const currentStepConfig = SOAP_NOTE_STEPS[currentStep - 1];

  // Initialize wizard
  useEffect(() => {
    const initializeWizard = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/wizards/soap-note/start`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) throw new Error('Failed to start wizard');

        const data = await response.json();
        setWizardId(data.data.wizard_session.wizard_id);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to initialize wizard');
        console.error('Wizard initialization error:', err);
      }
    };

    if (!wizardId) {
      initializeWizard();
    }
  }, [wizardId]);

  // Auto-launch tour on first visit (after page load)
  useEffect(() => {
    // Check if user has seen the tour before
    const tourSeen = localStorage.getItem('soapNoteTourSeen');

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
      localStorage.setItem('soapNoteTourSeen', 'true');
      // Keep pulse for 30 seconds after skipping, then stop
      if (status === STATUS.SKIPPED) {
        setShowPulse(true);
        setTimeout(() => setShowPulse(false), 30000);
      }
    }
  };

  const handleFieldChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleEnhance = async (field: string) => {
    const textToEnhance = formData[field as keyof SoapNoteData];
    if (!textToEnhance || !wizardId) return;

    setIsEnhancing(true);
    setEnhancingField(field);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/wizards/soap-note/${wizardId}/enhance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textToEnhance, field }),
      });

      if (!response.ok) throw new Error('Failed to enhance text');

      const data = await response.json();
      setEnhancementResult(data.data.enhanced_text);
      setShowEnhancementModal(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to enhance text');
    } finally {
      setIsEnhancing(false);
    }
  };

  const applyEnhancement = () => {
    if (enhancementResult && enhancingField) {
      setFormData((prev) => ({ ...prev, [enhancingField]: enhancementResult }));
      setShowEnhancementModal(false);
      setEnhancementResult(null);
      setEnhancingField(null);
    }
  };

  const handleNext = async () => {
    if (!wizardId) return;

    setIsLoading(true);
    setError(null);

    try {
      // Prepare step data
      const stepData: any = { step: currentStep, data: {} };
      currentStepConfig.fields.forEach((field) => {
        if (formData[field as keyof SoapNoteData]) {
          stepData.data[field] = formData[field as keyof SoapNoteData];
        }
      });

      // Add note date if not set
      if (currentStep === 1 && !formData.note_date) {
        stepData.data.note_date = new Date().toISOString();
      }

      const response = await fetch(`${API_BASE_URL}/wizards/soap-note/${wizardId}/step`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(stepData),
      });

      if (!response.ok) throw new Error('Failed to submit step');

      const data = await response.json();

      if (data.data.completed) {
        setIsCompleted(true);
        setFinalReport(data.data.report);
      } else {
        setCurrentStep(currentStep + 1);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit step');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleReset = () => {
    setCurrentStep(1);
    setWizardId(null);
    setFormData({});
    setIsCompleted(false);
    setFinalReport(null);
    setError(null);
  };

  // Completed view
  if (isCompleted && finalReport) {
    return (
      <div className="soap-note-wizard-container max-w-4xl mx-auto p-6">
        <div className="card">
          <h2 className="text-2xl font-bold text-green-600 mb-4 flex items-center">
            <i className="fas fa-check-circle mr-2"></i>
            SOAP Note Complete
          </h2>

          <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
            <p className="text-sm text-blue-800">{finalReport.banner}</p>
          </div>

          <div className="space-y-4">
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <pre className="whitespace-pre-wrap font-sans text-sm">{finalReport.narrative}</pre>
            </div>
          </div>

          <div className="mt-6 flex gap-3">
            <button
              onClick={() => {
                const blob = new Blob([finalReport.narrative], { type: 'text/plain' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `SOAP_Note_${new Date().toISOString().slice(0, 10)}.txt`;
                a.click();
                window.URL.revokeObjectURL(url);
              }}
              className="btn btn-primary"
            >
              <i className="fas fa-download mr-2"></i>
              Download SOAP Note
            </button>

            <button
              onClick={() => {
                navigator.clipboard.writeText(finalReport.narrative);
                alert('SOAP note copied to clipboard!');
              }}
              className="btn bg-accent-500 text-white hover:bg-accent-600"
            >
              <i className="fas fa-copy mr-2"></i>
              Copy to Clipboard
            </button>

            <button onClick={handleReset} className="btn bg-secondary-500 text-white hover:bg-secondary-600">
              <i className="fas fa-plus mr-2"></i>
              New SOAP Note
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

      <div className="soap-note-wizard-container max-w-4xl mx-auto p-6">
        <div className="card">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">SOAP Note Wizard</h1>
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
          <div className="soap-note-step-indicator mb-8">
            <div className="flex justify-between">
              {SOAP_NOTE_STEPS.map((step, index) => (
                <div
                  key={step.step}
                  className={`flex-1 text-center ${
                    index < SOAP_NOTE_STEPS.length - 1 ? 'border-r border-gray-300' : ''
                  }`}
                >
                  <div
                    className={`inline-flex items-center justify-center w-10 h-10 rounded-full mb-2 ${
                      currentStep > step.step
                        ? 'bg-green-500 text-white'
                        : currentStep === step.step
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-600'
                    }`}
                  >
                    {currentStep > step.step ? <i className="fas fa-check"></i> : step.step}
                  </div>
                  <div className="text-xs font-medium">{step.title.split(' - ')[0]}</div>
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

            <div className="soap-note-form space-y-4">
              {currentStepConfig.fields.map((field) => (
                <div key={field}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {FIELD_LABELS[field]}
                  </label>
                  <div className="flex gap-2">
                    {['history_present_illness', 'patient_reported_symptoms', 'physical_exam_findings', 'problem_list', 'progress_evaluation', 'diagnostic_plan', 'therapeutic_plan', 'patient_education'].includes(field) ? (
                      <>
                        <textarea
                          className="textarea flex-1 min-h-[100px]"
                          placeholder={`Enter ${FIELD_LABELS[field].toLowerCase()}...`}
                          value={(formData[field as keyof SoapNoteData] as string) || ''}
                          onChange={(e) => handleFieldChange(field, e.target.value)}
                          disabled={isLoading}
                        />
                        {formData[field as keyof SoapNoteData] && (
                          <button
                            onClick={() => handleEnhance(field)}
                            disabled={isEnhancing}
                            className="ai-enhance-btn btn bg-purple-600 text-white hover:bg-purple-700 disabled:opacity-50 self-start"
                            title="Enhance with AI"
                          >
                            {isEnhancing && enhancingField === field ? (
                              <i className="fas fa-spinner fa-spin"></i>
                            ) : (
                              <i className="fas fa-magic"></i>
                            )}
                          </button>
                        )}
                      </>
                    ) : (
                      <input
                        type="text"
                        className="input flex-1"
                        placeholder={`Enter ${FIELD_LABELS[field].toLowerCase()}...`}
                        value={(formData[field as keyof SoapNoteData] as string) || ''}
                        onChange={(e) => handleFieldChange(field, e.target.value)}
                        disabled={isLoading}
                      />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Navigation */}
          <div className="soap-note-navigation flex justify-between items-center">
            <button
              onClick={handlePrevious}
              disabled={currentStep === 1 || isLoading}
              className="btn bg-secondary-500 text-white hover:bg-secondary-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <i className="fas fa-arrow-left mr-2"></i>
              Previous
            </button>

            <div className="text-sm text-gray-600">
              Step {currentStep} of {SOAP_NOTE_STEPS.length}
            </div>

            <button
              onClick={handleNext}
              disabled={isLoading}
              className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <i className="fas fa-spinner fa-spin mr-2"></i>
                  Processing...
                </>
              ) : currentStep === SOAP_NOTE_STEPS.length ? (
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
                <h4 className="font-semibold text-sm text-gray-600 mb-2">Original:</h4>
                <p className="bg-gray-50 p-3 rounded whitespace-pre-wrap">
                  {enhancingField && formData[enhancingField as keyof SoapNoteData]}
                </p>
              </div>

              <div>
                <h4 className="font-semibold text-sm text-gray-600 mb-2">Enhanced:</h4>
                <p className="bg-purple-50 p-3 rounded whitespace-pre-wrap">{enhancementResult}</p>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button onClick={applyEnhancement} className="btn btn-primary">
                <i className="fas fa-check mr-2"></i>
                Use Enhanced Version
              </button>
              <button
                onClick={() => setShowEnhancementModal(false)}
                className="btn bg-secondary-500 text-white hover:bg-secondary-600"
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

export default SoapNoteWizard;
