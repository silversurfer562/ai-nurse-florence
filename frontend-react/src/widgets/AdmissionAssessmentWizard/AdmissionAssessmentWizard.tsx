/**
 * Admission Assessment Wizard React Component
 * Comprehensive initial patient assessment documentation with AI assistance
 * Following the WIZARD_TOUR_PATTERN.md standard
 */

import React, { useEffect, useState } from 'react';
import Joyride, { Step, CallBackProps, STATUS } from 'react-joyride';

const API_BASE_URL = '/api/v1';

interface AdmissionAssessmentData {
  // Step 1: Patient Demographics & Chief Complaint
  patient_name?: string;
  date_of_birth?: string;
  gender?: string;
  admission_date?: string;
  chief_complaint?: string;
  referring_provider?: string;
  // Step 2: Medical History & Medications
  past_medical_history?: string;
  past_surgical_history?: string;
  current_medications?: string;
  allergies?: string;
  immunization_status?: string;
  family_history?: string;
  // Step 3: Review of Systems
  cardiovascular?: string;
  respiratory?: string;
  gastrointestinal?: string;
  genitourinary?: string;
  neurological?: string;
  musculoskeletal?: string;
  integumentary?: string;
  psychosocial?: string;
  // Step 4: Physical Assessment & Vital Signs
  vital_signs?: string;
  height_weight?: string;
  general_appearance?: string;
  physical_exam_findings?: string;
  pain_assessment?: string;
  fall_risk_score?: string;
  // Step 5: Psychosocial & Discharge Planning
  living_situation?: string;
  support_system?: string;
  advance_directives?: string;
  code_status?: string;
  barriers_to_care?: string;
  discharge_planning_needs?: string;
  // Step 6: Initial Care Plan & Orders
  nursing_diagnoses?: string;
  care_priorities?: string;
  patient_goals?: string;
  pending_orders?: string;
  patient_education_needs?: string;
  follow_up_required?: string;
}

const ADMISSION_ASSESSMENT_STEPS = [
  {
    step: 1,
    title: 'Patient Demographics & Chief Complaint',
    fields: ['patient_name', 'date_of_birth', 'gender', 'admission_date', 'chief_complaint', 'referring_provider'],
    helpText: 'Start with basic patient information and primary reason for admission',
  },
  {
    step: 2,
    title: 'Medical History & Medications',
    fields: ['past_medical_history', 'past_surgical_history', 'current_medications', 'allergies', 'immunization_status', 'family_history'],
    helpText: 'Include chronic conditions, previous surgeries, all medications, allergies, and relevant family history',
  },
  {
    step: 3,
    title: 'Review of Systems',
    fields: ['cardiovascular', 'respiratory', 'gastrointestinal', 'genitourinary', 'neurological', 'musculoskeletal', 'integumentary', 'psychosocial'],
    helpText: 'Document findings for each body system. Note any abnormalities or patient concerns.',
  },
  {
    step: 4,
    title: 'Physical Assessment & Vital Signs',
    fields: ['vital_signs', 'height_weight', 'general_appearance', 'physical_exam_findings', 'pain_assessment', 'fall_risk_score'],
    helpText: 'Include complete vital signs, measurements, general appearance, and initial physical findings',
  },
  {
    step: 5,
    title: 'Psychosocial & Discharge Planning',
    fields: ['living_situation', 'support_system', 'advance_directives', 'code_status', 'barriers_to_care', 'discharge_planning_needs'],
    helpText: 'Document living situation, support systems, advance care planning, and anticipated discharge needs',
  },
  {
    step: 6,
    title: 'Initial Care Plan & Orders',
    fields: ['nursing_diagnoses', 'care_priorities', 'patient_goals', 'pending_orders', 'patient_education_needs', 'follow_up_required'],
    helpText: 'Identify nursing diagnoses, set priorities, establish patient-centered goals, and note education needs',
  },
];

const FIELD_LABELS: Record<string, string> = {
  patient_name: 'Patient Name', date_of_birth: 'Date of Birth', gender: 'Gender', admission_date: 'Admission Date',
  chief_complaint: 'Chief Complaint', referring_provider: 'Referring Provider',
  past_medical_history: 'Past Medical History', past_surgical_history: 'Past Surgical History',
  current_medications: 'Current Medications', allergies: 'Allergies', immunization_status: 'Immunization Status',
  family_history: 'Family History', cardiovascular: 'Cardiovascular', respiratory: 'Respiratory',
  gastrointestinal: 'Gastrointestinal', genitourinary: 'Genitourinary', neurological: 'Neurological',
  musculoskeletal: 'Musculoskeletal', integumentary: 'Integumentary', psychosocial: 'Psychosocial',
  vital_signs: 'Vital Signs', height_weight: 'Height/Weight', general_appearance: 'General Appearance',
  physical_exam_findings: 'Physical Exam Findings', pain_assessment: 'Pain Assessment (0-10)',
  fall_risk_score: 'Fall Risk Score', living_situation: 'Living Situation', support_system: 'Support System',
  advance_directives: 'Advance Directives', code_status: 'Code Status', barriers_to_care: 'Barriers to Care',
  discharge_planning_needs: 'Discharge Planning Needs', nursing_diagnoses: 'Nursing Diagnoses',
  care_priorities: 'Care Priorities', patient_goals: 'Patient Goals', pending_orders: 'Pending Orders',
  patient_education_needs: 'Patient Education Needs', follow_up_required: 'Follow-up Required',
};

const TOUR_STEPS: Step[] = [
  {
    target: '.admission-assessment-wizard-container',
    content: (
      <div>
        <p className="mb-2">Welcome to the Admission Assessment Wizard! Create comprehensive initial patient assessments following evidence-based nursing standards.</p>
        <p className="text-sm text-gray-600 mt-3 pt-2 border-t border-gray-200">
          💡 <strong>Tip:</strong> Press <kbd className="px-2 py-1 bg-gray-100 rounded border border-gray-300">ESC</kbd> anytime to exit this tour
        </p>
      </div>
    ),
    disableBeacon: true,
  },
  {
    target: '.admission-assessment-step-indicator',
    content: 'Track your progress through the 6 comprehensive assessment sections.',
  },
  {
    target: '.admission-assessment-form',
    content: 'Document relevant clinical information. Not all fields are required - include what\'s clinically significant.',
  },
  {
    target: '.ai-enhance-btn',
    content: 'Use AI to enhance your notes into professional clinical language. Available on narrative fields.',
  },
  {
    target: '.admission-assessment-navigation',
    content: 'Navigate through the wizard. Your work is saved automatically in your browser.',
  },
];

export const AdmissionAssessmentWizard: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [wizardId, setWizardId] = useState<string | null>(null);
  const [formData, setFormData] = useState<AdmissionAssessmentData>({});
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

  const currentStepConfig = ADMISSION_ASSESSMENT_STEPS[currentStep - 1];

  useEffect(() => {
    const initializeWizard = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/wizards/admission-assessment/start`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });
        if (!response.ok) throw new Error('Failed to start wizard');
        const data = await response.json();
        setWizardId(data.data.wizard_session.wizard_id);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to initialize wizard');
      }
    };
    if (!wizardId) initializeWizard();
  }, [wizardId]);

  useEffect(() => {
    const tourSeen = localStorage.getItem('admissionAssessmentTourSeen');
    if (!tourSeen) {
      const timer = setTimeout(() => {
        setRunTour(true);
        setShowPulse(false);
      }, 2500);
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
      localStorage.setItem('admissionAssessmentTourSeen', 'true');
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
    const textToEnhance = formData[field as keyof AdmissionAssessmentData];
    if (!textToEnhance || !wizardId) return;
    setIsEnhancing(true);
    setEnhancingField(field);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/wizards/admission-assessment/${wizardId}/enhance`, {
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
      const stepData: any = { step: currentStep, data: {} };
      currentStepConfig.fields.forEach((field) => {
        if (formData[field as keyof AdmissionAssessmentData]) {
          stepData.data[field] = formData[field as keyof AdmissionAssessmentData];
        }
      });
      const response = await fetch(`${API_BASE_URL}/wizards/admission-assessment/${wizardId}/step`, {
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
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const handleReset = () => {
    setCurrentStep(1);
    setWizardId(null);
    setFormData({});
    setIsCompleted(false);
    setFinalReport(null);
    setError(null);
  };

  if (isCompleted && finalReport) {
    return (
      <div className="admission-assessment-wizard-container max-w-4xl mx-auto p-6">
        <div className="card">
          <h2 className="text-2xl font-bold text-green-600 mb-4 flex items-center">
            <i className="fas fa-check-circle mr-2"></i>
            Admission Assessment Complete
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
                a.download = `Admission_Assessment_${new Date().toISOString().slice(0, 10)}.txt`;
                a.click();
                window.URL.revokeObjectURL(url);
              }}
              className="btn btn-primary"
            >
              <i className="fas fa-download mr-2"></i>
              Download Assessment
            </button>
            <button
              onClick={() => {
                navigator.clipboard.writeText(finalReport.narrative);
                alert('Assessment copied to clipboard!');
              }}
              className="btn bg-accent-500 text-white hover:bg-accent-600"
            >
              <i className="fas fa-copy mr-2"></i>
              Copy to Clipboard
            </button>
            <button onClick={handleReset} className="btn bg-secondary-500 text-white hover:bg-secondary-600">
              <i className="fas fa-plus mr-2"></i>
              New Assessment
            </button>
          </div>
        </div>
      </div>
    );
  }

  const narrativeFields = ['past_medical_history', 'past_surgical_history', 'current_medications', 'family_history',
    'cardiovascular', 'respiratory', 'gastrointestinal', 'genitourinary', 'neurological', 'musculoskeletal',
    'integumentary', 'psychosocial', 'physical_exam_findings', 'discharge_planning_needs', 'nursing_diagnoses',
    'care_priorities', 'patient_goals', 'patient_education_needs'];

  return (
    <>
      <Joyride steps={TOUR_STEPS} run={runTour} continuous showProgress showSkipButton callback={handleJoyrideCallback}
        styles={{ options: { primaryColor: '#d4af37', zIndex: 10000 } }} />
      <div className="admission-assessment-wizard-container max-w-4xl mx-auto p-6">
        <div className="card">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Admission Assessment Wizard</h1>
            <button onClick={() => setRunTour(true)}
              className={`btn bg-accent-500 text-white hover:bg-accent-600 text-sm ${showPulse ? 'animate-pulse' : ''}`}
              title="Quick tour - Press ESC anytime to exit">
              <i className="fas fa-question-circle mr-2"></i>
              {!hasSeenTour && showPulse ? 'New? Take Quick Tour!' : 'Help'}
            </button>
          </div>
          <div className="admission-assessment-step-indicator mb-8">
            <div className="flex justify-between">
              {ADMISSION_ASSESSMENT_STEPS.map((step, index) => (
                <div key={step.step} className={`flex-1 text-center ${index < ADMISSION_ASSESSMENT_STEPS.length - 1 ? 'border-r border-gray-300' : ''}`}>
                  <div className={`inline-flex items-center justify-center w-10 h-10 rounded-full mb-2 ${
                    currentStep > step.step ? 'bg-green-500 text-white' : currentStep === step.step ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
                  }`}>
                    {currentStep > step.step ? <i className="fas fa-check"></i> : step.step}
                  </div>
                  <div className="text-xs font-medium">{step.title.split(' & ')[0]}</div>
                </div>
              ))}
            </div>
          </div>
          {error && (
            <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
              <p className="text-red-700">{error}</p>
            </div>
          )}
          <div className="mb-6">
            <h2 className="text-2xl font-bold mb-2">{currentStepConfig.title}</h2>
            <p className="text-sm text-gray-500 mb-4">
              <i className="fas fa-info-circle mr-2"></i>
              {currentStepConfig.helpText}
            </p>
            <div className="admission-assessment-form space-y-4">
              {currentStepConfig.fields.map((field) => (
                <div key={field}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{FIELD_LABELS[field]}</label>
                  <div className="flex gap-2">
                    {narrativeFields.includes(field) ? (
                      <>
                        <textarea className="textarea flex-1 min-h-[100px]" placeholder={`Enter ${FIELD_LABELS[field].toLowerCase()}...`}
                          value={(formData[field as keyof AdmissionAssessmentData] as string) || ''}
                          onChange={(e) => handleFieldChange(field, e.target.value)} disabled={isLoading} />
                        {formData[field as keyof AdmissionAssessmentData] && (
                          <button onClick={() => handleEnhance(field)} disabled={isEnhancing}
                            className="ai-enhance-btn btn bg-purple-600 text-white hover:bg-purple-700 disabled:opacity-50 self-start" title="Enhance with AI">
                            {isEnhancing && enhancingField === field ? <i className="fas fa-spinner fa-spin"></i> : <i className="fas fa-magic"></i>}
                          </button>
                        )}
                      </>
                    ) : (
                      <input type="text" className="input flex-1" placeholder={`Enter ${FIELD_LABELS[field].toLowerCase()}...`}
                        value={(formData[field as keyof AdmissionAssessmentData] as string) || ''}
                        onChange={(e) => handleFieldChange(field, e.target.value)} disabled={isLoading} />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="admission-assessment-navigation flex justify-between items-center">
            <button onClick={handlePrevious} disabled={currentStep === 1 || isLoading}
              className="btn bg-secondary-500 text-white hover:bg-secondary-600 disabled:opacity-50 disabled:cursor-not-allowed">
              <i className="fas fa-arrow-left mr-2"></i>Previous
            </button>
            <div className="text-sm text-gray-600">Step {currentStep} of {ADMISSION_ASSESSMENT_STEPS.length}</div>
            <button onClick={handleNext} disabled={isLoading}
              className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed">
              {isLoading ? <><i className="fas fa-spinner fa-spin mr-2"></i>Processing...</> :
               currentStep === ADMISSION_ASSESSMENT_STEPS.length ? <><i className="fas fa-check mr-2"></i>Complete</> :
               <>Next<i className="fas fa-arrow-right ml-2"></i></>}
            </button>
          </div>
        </div>
      </div>
      {showEnhancementModal && enhancementResult && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <h3 className="text-xl font-bold mb-4">AI Enhanced Text</h3>
            <div className="space-y-4">
              <div>
                <h4 className="font-semibold text-sm text-gray-600 mb-2">Original:</h4>
                <p className="bg-gray-50 p-3 rounded whitespace-pre-wrap">
                  {enhancingField && formData[enhancingField as keyof AdmissionAssessmentData]}
                </p>
              </div>
              <div>
                <h4 className="font-semibold text-sm text-gray-600 mb-2">Enhanced:</h4>
                <p className="bg-purple-50 p-3 rounded whitespace-pre-wrap">{enhancementResult}</p>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button onClick={applyEnhancement} className="btn btn-primary">
                <i className="fas fa-check mr-2"></i>Use Enhanced Version
              </button>
              <button onClick={() => setShowEnhancementModal(false)} className="btn bg-secondary-500 text-white hover:bg-secondary-600">
                Keep Original
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default AdmissionAssessmentWizard;
