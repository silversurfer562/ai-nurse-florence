/**
 * Shift Handoff Wizard React Component
 * Professional nurse-to-nurse shift handoff documentation with AI assistance
 * Following the pattern from SBAR Wizard
 */

import React, { useEffect, useState } from 'react';
import Joyride, { Step, CallBackProps, STATUS } from 'react-joyride';

// API Configuration
const API_BASE_URL = '/api/v1';

// Shift Handoff Data Interface
interface ShiftHandoffData {
  // Step 1: Patient Identification & Status
  patient_name?: string;
  room_bed?: string;
  age?: string;
  diagnosis?: string;
  admission_date?: string;
  code_status?: string;

  // Step 2: Current Condition & Vital Signs
  current_condition?: string;
  vital_signs?: string;
  pain_level?: string;
  mental_status?: string;

  // Step 3: Treatments & Interventions
  iv_lines?: string;
  medications?: string;
  recent_procedures?: string;
  pending_labs?: string;
  pending_orders?: string;

  // Step 4: Plan & Priorities
  care_priorities?: string;
  scheduled_tasks?: string;
  patient_concerns?: string;
  family_involvement?: string;

  // Step 5: Safety & Special Considerations
  fall_risk?: string;
  isolation_precautions?: string;
  allergies?: string;
  special_equipment?: string;
  other_concerns?: string;
}

// Step configurations matching backend SHIFT_HANDOFF_STEPS
const SHIFT_HANDOFF_STEPS = [
  {
    step: 1,
    title: 'Patient Identification & Status',
    prompt: 'Identify the patient and current clinical status',
    fields: ['patient_name', 'room_bed', 'age', 'diagnosis', 'admission_date', 'code_status'],
    helpText: 'Start with patient basics: name, location, age, diagnosis, and code status',
  },
  {
    step: 2,
    title: 'Current Condition & Vital Signs',
    prompt: 'Describe current condition and most recent vital signs',
    fields: ['current_condition', 'vital_signs', 'pain_level', 'mental_status'],
    helpText: 'Include vital signs, pain level, mental status, and overall condition',
  },
  {
    step: 3,
    title: 'Treatments & Interventions',
    prompt: 'Detail current treatments, medications, and interventions',
    fields: ['iv_lines', 'medications', 'recent_procedures', 'pending_labs', 'pending_orders'],
    helpText: 'IV access, medications given, procedures done, pending orders/labs',
  },
  {
    step: 4,
    title: 'Plan & Priorities',
    prompt: 'Outline the care plan and priorities for the next shift',
    fields: ['care_priorities', 'scheduled_tasks', 'patient_concerns', 'family_involvement'],
    helpText: 'What needs to be done this shift? Patient/family concerns? Priorities?',
  },
  {
    step: 5,
    title: 'Safety & Special Considerations',
    prompt: 'Note any safety concerns or special considerations',
    fields: ['fall_risk', 'isolation_precautions', 'allergies', 'special_equipment', 'other_concerns'],
    helpText: 'Falls risk, isolation, allergies, special equipment, or other safety concerns',
  },
];

// Field labels
const FIELD_LABELS: Record<string, string> = {
  patient_name: 'Patient Name',
  room_bed: 'Room/Bed',
  age: 'Age',
  diagnosis: 'Diagnosis',
  admission_date: 'Admission Date',
  code_status: 'Code Status',
  current_condition: 'Current Condition',
  vital_signs: 'Vital Signs',
  pain_level: 'Pain Level (0-10)',
  mental_status: 'Mental Status',
  iv_lines: 'IV Lines/Access',
  medications: 'Medications Given This Shift',
  recent_procedures: 'Recent Procedures',
  pending_labs: 'Pending Labs',
  pending_orders: 'Pending Orders',
  care_priorities: 'Care Priorities',
  scheduled_tasks: 'Scheduled Tasks',
  patient_concerns: 'Patient/Family Concerns',
  family_involvement: 'Family Involvement',
  fall_risk: 'Fall Risk Assessment',
  isolation_precautions: 'Isolation Precautions',
  allergies: 'Allergies',
  special_equipment: 'Special Equipment',
  other_concerns: 'Other Safety Concerns',
};

// Joyride tour steps
const TOUR_STEPS: Step[] = [
  {
    target: '.shift-handoff-wizard-container',
    content: (
      <div>
        <p className="mb-2">Welcome to the Shift Handoff Wizard! Create professional nurse-to-nurse handoff reports following best practices.</p>
        <p className="text-sm text-gray-600 mt-3 pt-2 border-t border-gray-200">
          💡 <strong>Tip:</strong> Press <kbd className="px-2 py-1 bg-gray-100 rounded border border-gray-300">ESC</kbd> anytime to exit this tour
        </p>
      </div>
    ),
    disableBeacon: true,
  },
  {
    target: '.shift-handoff-step-indicator',
    content: 'Track your progress through 5 handoff sections: Patient ID, Condition, Treatments, Plan, and Safety.',
  },
  {
    target: '.shift-handoff-form',
    content: 'Fill in relevant information for this patient. Not all fields are required - include what\'s clinically relevant.',
  },
  {
    target: '.ai-enhance-btn',
    content: 'Use AI to enhance your notes into professional clinical language. Available on multi-line fields.',
  },
  {
    target: '.shift-handoff-navigation',
    content: 'Navigate through the wizard. Your work is saved automatically in your browser.',
  },
];

export const ShiftHandoffWizard: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [wizardId, setWizardId] = useState<string | null>(null);
  const [formData, setFormData] = useState<ShiftHandoffData>({});
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

  const currentStepConfig = SHIFT_HANDOFF_STEPS[currentStep - 1];

  // Initialize wizard
  useEffect(() => {
    const initializeWizard = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/wizards/shift-handoff/start`, {
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
    const tourSeen = localStorage.getItem('shiftHandoffTourSeen');

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
      localStorage.setItem('shiftHandoffTourSeen', 'true');
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
    const textToEnhance = formData[field as keyof ShiftHandoffData];
    if (!textToEnhance || !wizardId) return;

    setIsEnhancing(true);
    setEnhancingField(field);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/wizards/shift-handoff/${wizardId}/enhance`, {
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
        if (formData[field as keyof ShiftHandoffData]) {
          stepData.data[field] = formData[field as keyof ShiftHandoffData];
        }
      });

      const response = await fetch(`${API_BASE_URL}/wizards/shift-handoff/${wizardId}/step`, {
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
      <div className="shift-handoff-wizard-container max-w-4xl mx-auto p-6">
        <div className="card">
          <h2 className="text-2xl font-bold text-green-600 mb-4 flex items-center">
            <i className="fas fa-check-circle mr-2"></i>
            Shift Handoff Complete
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
                a.download = `Shift_Handoff_${new Date().toISOString().slice(0, 10)}.txt`;
                a.click();
                window.URL.revokeObjectURL(url);
              }}
              className="btn btn-primary"
            >
              <i className="fas fa-download mr-2"></i>
              Download Handoff
            </button>

            <button
              onClick={() => {
                navigator.clipboard.writeText(finalReport.narrative);
                alert('Handoff copied to clipboard!');
              }}
              className="btn bg-secondary-500 text-white hover:bg-secondary-600"
            >
              <i className="fas fa-copy mr-2"></i>
              Copy to Clipboard
            </button>

            <button onClick={handleReset} className="btn bg-secondary-500 text-white hover:bg-secondary-600">
              <i className="fas fa-plus mr-2"></i>
              New Handoff
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

      <div className="shift-handoff-wizard-container max-w-4xl mx-auto p-6">
        <div className="card">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Shift Handoff Wizard</h1>
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
          <div className="shift-handoff-step-indicator mb-8">
            <div className="flex justify-between">
              {SHIFT_HANDOFF_STEPS.map((step, index) => (
                <div
                  key={step.step}
                  className={`flex-1 text-center ${
                    index < SHIFT_HANDOFF_STEPS.length - 1 ? 'border-r border-gray-300' : ''
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
                  <div className="text-xs font-medium">{step.title}</div>
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

            <div className="shift-handoff-form space-y-4">
              {currentStepConfig.fields.map((field) => (
                <div key={field}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {FIELD_LABELS[field]}
                  </label>
                  <div className="flex gap-2">
                    {['current_condition', 'care_priorities', 'scheduled_tasks', 'patient_concerns'].includes(field) ? (
                      <>
                        <textarea
                          className="textarea flex-1 min-h-[100px]"
                          placeholder={`Enter ${FIELD_LABELS[field].toLowerCase()}...`}
                          value={(formData[field as keyof ShiftHandoffData] as string) || ''}
                          onChange={(e) => handleFieldChange(field, e.target.value)}
                          disabled={isLoading}
                        />
                        {formData[field as keyof ShiftHandoffData] && (
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
                        value={(formData[field as keyof ShiftHandoffData] as string) || ''}
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
          <div className="shift-handoff-navigation flex justify-between items-center">
            <button
              onClick={handlePrevious}
              disabled={currentStep === 1 || isLoading}
              className="btn bg-secondary-500 text-white hover:bg-secondary-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <i className="fas fa-arrow-left mr-2"></i>
              Previous
            </button>

            <div className="text-sm text-gray-600">
              Step {currentStep} of {SHIFT_HANDOFF_STEPS.length}
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
              ) : currentStep === SHIFT_HANDOFF_STEPS.length ? (
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
                  {enhancingField && formData[enhancingField as keyof ShiftHandoffData]}
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

export default ShiftHandoffWizard;
