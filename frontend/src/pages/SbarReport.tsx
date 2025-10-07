import { useState, useEffect } from 'react';
import Joyride, { Step, CallBackProps, STATUS } from 'react-joyride';
import { useCareSettings, useCareSettingTemplates } from '../hooks/useCareSettings';
import CareSettingContextBanner from '../components/CareSettingContextBanner';
import VoiceDictation from '../components/VoiceDictation';
import { tourConfig, getQuickStartButtonProps } from '../utils/tourConfig';

interface WizardData {
  [key: string]: string;
}

interface WizardStep {
  title: string;
  description?: string;
  field: {
    id: string;
    label: string;
    placeholder: string;
    help: string;
    rows: number;
  };
}

export default function SbarReport() {
  const [currentStep, setCurrentStep] = useState(0);
  const [data, setData] = useState<WizardData>({
    patient_id: '',
    situation: '',
    background: '',
    assessment: '',
    recommendation: ''
  });
  const [generatedReport, setGeneratedReport] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  // Tour state
  const [runTour, setRunTour] = useState(false);
  const [showPulse, setShowPulse] = useState(false);

  // Care setting integration
  const { careSetting } = useCareSettings();
  const { getTemplateDefaults } = useCareSettingTemplates();

  // Tour steps
  const tourSteps: Step[] = [
    {
      target: '.wizard-container',
      content: (
        <div>
          <p className="mb-2">Welcome to the SBAR Report Wizard! This tool helps you create structured clinical communications following the SBAR format.</p>
          <p className="text-sm text-orange-800 bg-orange-50 p-2 rounded mt-2">
            <strong>⚠️ Important:</strong> This wizard moves forward only. Review each step carefully before clicking Next.
          </p>
          <p className="text-sm text-gray-600 mt-3 pt-2 border-t border-gray-200">
            💡 <strong>Tip:</strong> Press <kbd className="px-2 py-1 bg-gray-100 rounded border border-gray-300">ESC</kbd> anytime to exit this tour
          </p>
        </div>
      ),
      disableBeacon: true,
    },
    {
      target: '.wizard-progress',
      content: 'Track your progress through all five steps. Green = completed, Blue with ring = current, Gray = upcoming. Steps cannot be clicked to go back.',
    },
    {
      target: '.wizard-content',
      content: 'Complete each section carefully. You cannot return to edit previous steps, so review your entries before advancing.',
    },
    {
      target: '.wizard-navigation',
      content: 'Use "Next" to advance and "Start Over" to restart if needed. The wizard will confirm before moving to the next step.',
    },
  ];

  // Auto-launch tour on first visit
  useEffect(() => {
    const tourSeen = localStorage.getItem('sbarTourSeen');
    if (!tourSeen) {
      const timer = setTimeout(() => {
        setRunTour(true);
        setShowPulse(false);
      }, 2500);
      setShowPulse(true);
      return () => clearTimeout(timer);
    }
  }, []);

  // Tour callback handler
  const handleTourCallback = (data: CallBackProps) => {
    const { status } = data;
    if (status === STATUS.FINISHED || status === STATUS.SKIPPED) {
      setRunTour(false);
      localStorage.setItem('sbarTourSeen', 'true');
    }
  };

  // Load care setting template defaults
  useEffect(() => {
    if (careSetting) {
      const defaults = getTemplateDefaults('sbar');
      // Templates can guide placeholder text and focus areas
      console.log('SBAR defaults for', careSetting, ':', defaults);
    }
  }, [careSetting, getTemplateDefaults]);

  const steps: WizardStep[] = [
    {
      title: 'Patient Information',
      description: 'Identify the patient (use initials or ID for privacy)',
      field: {
        id: 'patient_id',
        label: 'Patient ID/Initials',
        placeholder: 'e.g., J.D., Room 412, MRN 123456',
        help: 'Use patient initials or ID number for privacy protection',
        rows: 2
      }
    },
    {
      title: 'Situation',
      description: 'Briefly describe the current situation and reason for communication',
      field: {
        id: 'situation',
        label: 'Situation',
        placeholder: careSetting === 'icu'
          ? 'Describe patient status, critical changes, immediate concerns...'
          : careSetting === 'emergency'
          ? 'Chief complaint, vital signs, time-critical concerns...'
          : careSetting === 'home-health'
          ? 'Current home situation, patient/caregiver concerns...'
          : 'Why are you calling? What is happening right now?',
        help: 'Focus on the immediate issue requiring communication',
        rows: 4
      }
    },
    {
      title: 'Background',
      description: 'Provide relevant clinical context and patient history',
      field: {
        id: 'background',
        label: 'Background',
        placeholder: careSetting === 'icu'
          ? 'Diagnosis, procedures, medications, recent labs, code status...'
          : careSetting === 'emergency'
          ? 'Medical history, current medications, allergies, recent events...'
          : careSetting === 'home-health'
          ? 'Diagnosis, home medications, support system, baseline status...'
          : 'What is the clinical context? Diagnosis, medications, recent changes...',
        help: 'Include pertinent medical history and current treatment',
        rows: 5
      }
    },
    {
      title: 'Assessment',
      description: 'State your clinical assessment of the situation',
      field: {
        id: 'assessment',
        label: 'Assessment',
        placeholder: careSetting === 'icu'
          ? 'Clinical interpretation, severity assessment, trend analysis...'
          : careSetting === 'emergency'
          ? 'Working diagnosis, acuity level, critical findings...'
          : careSetting === 'home-health'
          ? 'Patient progress, safety concerns, functional status...'
          : 'What do you think is happening? Your clinical judgment...',
        help: 'Your professional assessment of the patient\'s condition',
        rows: 5
      }
    },
    {
      title: 'Recommendation',
      description: 'Suggest specific actions or decisions needed',
      field: {
        id: 'recommendation',
        label: 'Recommendation',
        placeholder: careSetting === 'icu'
          ? 'Specific interventions needed, consultations, orders, transfer...'
          : careSetting === 'emergency'
          ? 'Immediate actions, diagnostic workup, admission vs discharge...'
          : careSetting === 'home-health'
          ? 'Care plan changes, referrals, education needs, follow-up...'
          : 'What do you need? Orders, interventions, consultation...',
        help: 'Be specific about what you need from the receiving provider',
        rows: 5
      }
    }
  ];

  const updateData = (field: string, value: string) => {
    setData({ ...data, [field]: value });
  };

  const validateStep = (): boolean => {
    const step = steps[currentStep];
    if (!data[step.field.id] || data[step.field.id].trim() === '') {
      alert(`Please complete: ${step.title}`);
      return false;
    }
    return true;
  };

  const nextStep = () => {
    if (!validateStep()) return;

    // Show confirmation dialog before advancing (except on first step)
    if (currentStep > 0 && currentStep < steps.length - 1) {
      const confirmed = window.confirm(
        "Please review your entries. You won't be able to go back to edit this step. Continue?"
      );
      if (!confirmed) return;
    }

    if (currentStep === steps.length - 1) {
      handleGenerate();
    } else {
      setCurrentStep(currentStep + 1);
    }
  };

  const startOver = () => {
    const confirmed = window.confirm(
      "Are you sure you want to start over? All entered data will be lost."
    );
    if (confirmed) {
      setData({
        patient_id: '',
        situation: '',
        background: '',
        assessment: '',
        recommendation: ''
      });
      setGeneratedReport(null);
      setCurrentStep(0);
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch('/api/v1/wizards/sbar-report/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_id: data.patient_id,
          situation: data.situation,
          background: data.background,
          assessment: data.assessment,
          recommendation: data.recommendation,
          care_setting: careSetting || 'med-surg'
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setGeneratedReport(result.sbar_report || result.report);
      } else {
        alert('Failed to generate SBAR report. Please try again.');
      }
    } catch (error) {
      console.error('Error generating SBAR report:', error);
      alert('An error occurred. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = () => {
    if (generatedReport) {
      navigator.clipboard.writeText(generatedReport);
      alert('SBAR report copied to clipboard!');
    }
  };

  const downloadReport = () => {
    if (generatedReport) {
      const blob = new Blob([generatedReport], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `sbar-report-${data.patient_id || 'patient'}.txt`;
      a.click();
      window.URL.revokeObjectURL(url);
    }
  };

  const startNew = () => {
    setData({
      patient_id: '',
      situation: '',
      background: '',
      assessment: '',
      recommendation: ''
    });
    setGeneratedReport(null);
    setCurrentStep(0);
  };

  if (generatedReport) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-purple-50">
        <div className="container mx-auto px-4 py-8 max-w-4xl">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-800 mb-2">SBAR Report Generated</h1>
            <p className="text-sm sm:text-base text-gray-600">Structured clinical communication ready to use</p>
          </div>

          {/* Care Setting Banner */}
          {careSetting && <CareSettingContextBanner className="mb-6" message={`SBAR report optimized for ${careSetting} setting`} />}

          {/* Generated Report */}
          <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
            <div className="mb-4 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">
              <h2 className="text-xl sm:text-2xl font-bold text-gray-800">Your SBAR Report</h2>
              <div className="flex flex-col sm:flex-row gap-2">
                <button
                  onClick={copyToClipboard}
                  className="min-h-[44px] px-4 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                >
                  <i className="fas fa-copy mr-2"></i>Copy
                </button>
                <button
                  onClick={downloadReport}
                  className="min-h-[44px] px-4 py-3 bg-success-600 text-white rounded-lg hover:bg-success-700 transition-colors"
                >
                  <i className="fas fa-download mr-2"></i>Download
                </button>
              </div>
            </div>
            <pre className="whitespace-pre-wrap bg-gray-50 p-6 rounded-lg border border-gray-200 text-gray-800 font-mono text-sm leading-relaxed">
              {generatedReport}
            </pre>
          </div>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row justify-center gap-3">
            <button
              onClick={startNew}
              className="min-h-[44px] px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              <i className="fas fa-plus mr-2"></i>Create New SBAR
            </button>
            <a
              href="/app"
              className="min-h-[44px] px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center justify-center"
            >
              <i className="fas fa-table-columns mr-2"></i>Back to Dashboard
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-purple-50">
      <Joyride
        steps={tourSteps}
        run={runTour}
        callback={handleTourCallback}
        {...tourConfig}
      />
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex flex-col sm:flex-row justify-center items-center gap-4 mb-2">
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-800">SBAR Report Wizard</h1>
            <button
              onClick={() => setRunTour(true)}
              {...getQuickStartButtonProps('SBAR Report', showPulse)}
            >
              <i className="fas fa-question-circle mr-2" aria-hidden="true"></i>
              Quick Start
            </button>
          </div>
          <p className="text-sm sm:text-base text-gray-600">Structured clinical communication for patient handoffs</p>
        </div>

        {/* Care Setting Context Banner */}
        {careSetting && <CareSettingContextBanner className="mb-6" />}

        {/* Wizard Container */}
        <div className="wizard-container bg-white rounded-lg shadow-lg overflow-visible">
          {/* Wizard Header */}
          <div className="wizard-header bg-primary-600 text-white p-6 rounded-t-lg">
            <h2 className="text-2xl font-bold">SBAR Communication Tool</h2>
            <p className="text-primary-100 mt-2">Complete each section for effective clinical handoff</p>
          </div>

          {/* Progress Bar */}
          <div className="wizard-progress bg-gray-50 p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Progress</span>
              <span className="text-sm text-gray-500">
                {currentStep + 1} of {steps.length}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
              ></div>
            </div>
            <div className="flex justify-between mt-2 gap-1 sm:gap-2">
              {steps.map((step, index) => {
                const isCompleted = index < currentStep;
                const isCurrent = index === currentStep;

                return (
                  <div key={index} className="flex flex-col items-center flex-1">
                    <div
                      className={`min-w-[44px] min-h-[44px] w-10 h-10 sm:w-12 sm:h-12 rounded-full flex items-center justify-center text-xs sm:text-sm font-bold transition-all ${
                        isCurrent
                          ? 'bg-primary-600 text-white ring-2 ring-primary-400 ring-offset-2'
                          : isCompleted
                          ? 'bg-success-500 text-white'
                          : 'bg-gray-200 text-gray-400'
                      }`}
                      title={step.title}
                    >
                      {index + 1}
                    </div>
                    <span className="text-[10px] sm:text-xs text-gray-600 mt-1 text-center hidden sm:block">{step.title}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Step Content */}
          <div className="wizard-content p-6">
            <div className="step-content">
              <h3 className="text-xl font-bold text-gray-800 mb-4">{steps[currentStep].title}</h3>
              {steps[currentStep].description && (
                <p className="text-gray-600 mb-6">{steps[currentStep].description}</p>
              )}

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {steps[currentStep].field.label} <span className="text-red-500">*</span>
                </label>
                <div>
                  <textarea
                    value={data[steps[currentStep].field.id] || ''}
                    onChange={(e) => updateData(steps[currentStep].field.id, e.target.value)}
                    placeholder={steps[currentStep].field.placeholder}
                    rows={steps[currentStep].field.rows}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                  <VoiceDictation
                    onTranscript={(text) => updateData(steps[currentStep].field.id, (data[steps[currentStep].field.id] || '') + ' ' + text)}
                    placeholder="Use voice to dictate"
                  />
                </div>
                <p className="text-sm text-gray-500 mt-2">
                  <i className="fas fa-info-circle mr-1"></i>
                  {steps[currentStep].field.help}
                </p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <div className="wizard-navigation bg-gray-50 p-4 rounded-b-lg flex flex-col sm:flex-row gap-3 sm:justify-between">
            <button
              onClick={startOver}
              className="min-h-[44px] px-6 py-3 text-gray-700 bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200 transition-colors"
            >
              <i className="fas fa-redo mr-2"></i>Start Over
            </button>

            <button
              onClick={nextStep}
              disabled={isGenerating}
              className="min-h-[44px] px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Advance to next step (you cannot go back to edit this step)"
            >
              {currentStep === steps.length - 1 ? (
                isGenerating ? (
                  <>
                    <i className="fas fa-spinner fa-spin mr-2"></i>Generating...
                  </>
                ) : (
                  <>
                    <i className="fas fa-check mr-2"></i>Generate Report
                  </>
                )
              ) : (
                <>
                  Next<i className="fas fa-arrow-right ml-2"></i>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-gray-600 text-sm">
          <p>&copy; 2025 AI Nurse Florence</p>
        </div>
      </div>
    </div>
  );
}
