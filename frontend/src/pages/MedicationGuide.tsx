import { useState, useEffect } from 'react';
import Joyride, { Step, CallBackProps, STATUS } from 'react-joyride';
import { useCareSettings, useCareSettingTemplates } from '../hooks/useCareSettings';
import CareSettingContextBanner from '../components/CareSettingContextBanner';
import { tourConfig, getQuickStartButtonProps } from '../utils/tourConfig';

interface WizardData {
  medication_name: string;
  dosage: string;
  frequency: string;
  route: string;
  special_instructions: string[];
  purpose?: string;
  how_it_works?: string;
  common_side_effects: string[];
  serious_side_effects: string[];
  interactions: string[];
  storage_instructions?: string;
}

export default function MedicationGuide() {
  const [currentStep, setCurrentStep] = useState(0);
  const [data, setData] = useState<WizardData>({
    medication_name: '',
    dosage: '',
    frequency: '',
    route: 'oral',
    special_instructions: [],
    common_side_effects: [],
    serious_side_effects: [],
    interactions: []
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [newItem, setNewItem] = useState('');

  // Tour state
  const [runTour, setRunTour] = useState(false);
  const [showPulse, setShowPulse] = useState(false);

  const { careSetting } = useCareSettings();
  const { getTemplateDefaults } = useCareSettingTemplates();

  // Tour steps
  const tourSteps: Step[] = [
    {
      target: '.wizard-container',
      content: (
        <div>
          <p className="mb-2">Welcome to the Medication Guide Wizard! Create patient-friendly medication education materials.</p>
          <p className="text-sm text-gray-600 mt-3 pt-2 border-t border-gray-200">
            💡 <strong>Tip:</strong> Press <kbd className="px-2 py-1 bg-gray-100 rounded border border-gray-300">ESC</kbd> anytime to exit this tour
          </p>
        </div>
      ),
      disableBeacon: true,
    },
    {
      target: '.wizard-progress',
      content: 'Track your progress through all six steps: Medication Info, Instructions, Purpose, Side Effects, Safety, and Review.',
    },
    {
      target: '.wizard-content',
      content: 'Complete each section with medication details. The wizard helps create comprehensive patient education materials.',
    },
    {
      target: '.help-button',
      content: 'Need help anytime? Click this button to restart the tour.',
    },
  ];

  // Auto-launch tour on first visit
  useEffect(() => {
    const tourSeen = localStorage.getItem('medicationGuideTourSeen');
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
      localStorage.setItem('medicationGuideTourSeen', 'true');
    }
  };

  useEffect(() => {
    if (careSetting) {
      const defaults = getTemplateDefaults('medication-guide');
      console.log('Medication guide defaults for', careSetting, ':', defaults);
    }
  }, [careSetting, getTemplateDefaults]);

  const steps = [
    { title: 'Medication Info', description: 'Basic medication information' },
    { title: 'Instructions', description: 'How to take this medication' },
    { title: 'Purpose', description: 'Why you are taking this medication' },
    { title: 'Side Effects', description: 'What to watch for' },
    { title: 'Safety', description: 'Important precautions' },
    { title: 'Review', description: 'Confirm and generate' }
  ];

  const updateData = (field: keyof WizardData, value: any) => {
    setData({ ...data, [field]: value });
  };

  const addArrayItem = (field: keyof WizardData, value: string) => {
    if (!value.trim()) return;
    const currentArray = (data[field] as string[]) || [];
    updateData(field, [...currentArray, value]);
    setNewItem('');
  };

  const removeArrayItem = (field: keyof WizardData, index: number) => {
    const currentArray = (data[field] as string[]) || [];
    updateData(field, currentArray.filter((_, i) => i !== index));
  };

  const validateStep = (): boolean => {
    if (currentStep === 0 && (!data.medication_name.trim() || !data.dosage.trim() || !data.frequency.trim())) {
      alert('Please complete all required medication information');
      return false;
    }
    return true;
  };

  const nextStep = () => {
    if (!validateStep()) return;
    if (currentStep === steps.length - 1) {
      handleGenerate();
    } else {
      setCurrentStep(currentStep + 1);
    }
  };

  const previousStep = () => {
    if (currentStep > 0) setCurrentStep(currentStep - 1);
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch('/api/v1/patient-documents/medication-guide', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...data, care_setting: careSetting || 'med-surg', format: 'pdf' }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `medication-guide-${data.medication_name}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
        alert('Medication guide generated successfully!');
      } else {
        alert('Failed to generate medication guide. Please try again.');
      }
    } catch (error) {
      console.error('Error generating medication guide:', error);
      alert('An error occurred. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Medication Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={data.medication_name}
                onChange={(e) => updateData('medication_name', e.target.value)}
                placeholder="e.g., Metformin, Lisinopril, Atorvastatin"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Dosage <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={data.dosage}
                  onChange={(e) => updateData('dosage', e.target.value)}
                  placeholder="e.g., 500 mg, 10 mg"
                  className="w-full p-3 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Frequency <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={data.frequency}
                  onChange={(e) => updateData('frequency', e.target.value)}
                  placeholder="e.g., twice daily, every 8 hours"
                  className="w-full p-3 border border-gray-300 rounded-lg"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Route</label>
              <select
                value={data.route}
                onChange={(e) => updateData('route', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg"
              >
                <option value="oral">Oral (by mouth)</option>
                <option value="topical">Topical (on skin)</option>
                <option value="inhalation">Inhalation</option>
                <option value="injection">Injection</option>
                <option value="sublingual">Sublingual (under tongue)</option>
              </select>
            </div>
          </div>
        );

      case 1:
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Special Instructions
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={newItem}
                  onChange={(e) => setNewItem(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addArrayItem('special_instructions', newItem)}
                  placeholder="e.g., Take with food, Avoid alcohol"
                  className="flex-1 p-2 border border-gray-300 rounded"
                />
                <button
                  onClick={() => addArrayItem('special_instructions', newItem)}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Add
                </button>
              </div>
              <ul className="space-y-2">
                {data.special_instructions.map((item, index) => (
                  <li key={index} className="flex justify-between items-center bg-blue-50 p-2 rounded">
                    <span>{item}</span>
                    <button
                      onClick={() => removeArrayItem('special_instructions', index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <i className="fas fa-times"></i>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Storage Instructions (Optional)
              </label>
              <textarea
                value={data.storage_instructions || ''}
                onChange={(e) => updateData('storage_instructions', e.target.value)}
                placeholder="e.g., Store at room temperature, Keep in refrigerator"
                rows={2}
                className="w-full p-3 border border-gray-300 rounded-lg"
              />
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Purpose (Why you are taking this medication)
              </label>
              <textarea
                value={data.purpose || ''}
                onChange={(e) => updateData('purpose', e.target.value)}
                placeholder="e.g., To lower your blood sugar, To control high blood pressure"
                rows={3}
                className="w-full p-3 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                How It Works (Simple explanation)
              </label>
              <textarea
                value={data.how_it_works || ''}
                onChange={(e) => updateData('how_it_works', e.target.value)}
                placeholder="e.g., Helps your body use insulin better, Relaxes blood vessels"
                rows={3}
                className="w-full p-3 border border-gray-300 rounded-lg"
              />
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Common Side Effects
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={newItem}
                  onChange={(e) => setNewItem(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addArrayItem('common_side_effects', newItem)}
                  placeholder="e.g., Nausea, Headache, Dizziness"
                  className="flex-1 p-2 border border-gray-300 rounded"
                />
                <button
                  onClick={() => addArrayItem('common_side_effects', newItem)}
                  className="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700"
                >
                  Add
                </button>
              </div>
              <ul className="space-y-2">
                {data.common_side_effects.map((item, index) => (
                  <li key={index} className="flex justify-between items-center bg-yellow-50 p-2 rounded">
                    <span>{item}</span>
                    <button
                      onClick={() => removeArrayItem('common_side_effects', index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <i className="fas fa-times"></i>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Serious Side Effects (Call your doctor if you experience these)
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={newItem}
                  onChange={(e) => setNewItem(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addArrayItem('serious_side_effects', newItem)}
                  placeholder="e.g., Severe allergic reaction, Difficulty breathing"
                  className="flex-1 p-2 border border-gray-300 rounded"
                />
                <button
                  onClick={() => addArrayItem('serious_side_effects', newItem)}
                  className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                >
                  Add
                </button>
              </div>
              <ul className="space-y-2">
                {data.serious_side_effects.map((item, index) => (
                  <li key={index} className="flex justify-between items-center bg-red-50 p-2 rounded border-l-4 border-red-500">
                    <span>{item}</span>
                    <button
                      onClick={() => removeArrayItem('serious_side_effects', index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <i className="fas fa-times"></i>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Drug Interactions / Things to Avoid
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={newItem}
                  onChange={(e) => setNewItem(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addArrayItem('interactions', newItem)}
                  placeholder="e.g., Grapefruit juice, Alcohol, NSAIDs"
                  className="flex-1 p-2 border border-gray-300 rounded"
                />
                <button
                  onClick={() => addArrayItem('interactions', newItem)}
                  className="px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700"
                >
                  Add
                </button>
              </div>
              <ul className="space-y-2">
                {data.interactions.map((item, index) => (
                  <li key={index} className="flex justify-between items-center bg-orange-50 p-2 rounded">
                    <span>{item}</span>
                    <button
                      onClick={() => removeArrayItem('interactions', index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <i className="fas fa-times"></i>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
              <p className="text-sm text-blue-900">
                <i className="fas fa-info-circle mr-2"></i>
                Always tell your doctor about all medications you are taking, including over-the-counter drugs and supplements
              </p>
            </div>
          </div>
        );

      case 5:
        return (
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">Medication</h4>
              <p className="text-gray-700">{data.medication_name} {data.dosage}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">How to Take</h4>
              <p className="text-gray-700">{data.frequency} - {data.route}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">Instructions</h4>
              <p className="text-gray-700">{data.special_instructions.length} instruction(s)</p>
            </div>
            <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
              <p className="text-sm text-blue-900">
                <i className="fas fa-info-circle mr-2"></i>
                Click "Generate" to create your medication guide PDF
              </p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <Joyride
        steps={tourSteps}
        run={runTour}
        callback={handleTourCallback}
        {...tourConfig}
      />
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="text-center mb-8">
          <div className="flex justify-center items-center gap-4 mb-2">
            <h1 className="text-4xl font-bold text-gray-800">Medication Guide Wizard</h1>
            <button
              onClick={() => setRunTour(true)}
              {...getQuickStartButtonProps('Medication Guide', showPulse)}
            >
              <i className="fas fa-question-circle mr-2"></i>
              Quick Start
            </button>
          </div>
          <p className="text-gray-600">Comprehensive medication information for patients</p>
        </div>

        {careSetting && <CareSettingContextBanner className="mb-6" />}

        <div className="wizard-container bg-white rounded-lg shadow-lg">
          <div className="wizard-header bg-blue-600 text-white p-6 rounded-t-lg">
            <h2 className="text-2xl font-bold">Medication Guide</h2>
            <p className="text-blue-100 mt-2">Patient-friendly medication information</p>
          </div>

          <div className="wizard-progress bg-gray-50 p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Progress</span>
              <span className="text-sm text-gray-500">{currentStep + 1} of {steps.length}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
              ></div>
            </div>
          </div>

          <div className="wizard-content p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">{steps[currentStep].title}</h3>
            <p className="text-gray-600 mb-6">{steps[currentStep].description}</p>
            {renderStepContent()}
          </div>

          <div className="wizard-navigation bg-gray-50 p-4 rounded-b-lg flex justify-between">
            <button
              onClick={previousStep}
              disabled={currentStep === 0}
              className={`px-4 py-2 text-gray-600 bg-gray-200 rounded-lg hover:bg-gray-300 ${
                currentStep === 0 ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              <i className="fas fa-arrow-left mr-2"></i>Previous
            </button>
            <button
              onClick={nextStep}
              disabled={isGenerating}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {currentStep === steps.length - 1 ? (
                isGenerating ? (
                  <>
                    <i className="fas fa-spinner fa-spin mr-2"></i>Generating...
                  </>
                ) : (
                  <>
                    <i className="fas fa-file-pdf mr-2"></i>Generate PDF
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

        <div className="mt-12 text-center text-gray-600 text-sm">
          <p>&copy; 2025 AI Nurse Florence</p>
        </div>
      </div>
    </div>
  );
}
