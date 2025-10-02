import { useState, useEffect } from 'react';
import { HelpSystem } from '../components/Help/HelpSystem';
import { useCareSettings, useCareSettingTemplates } from '../hooks/useCareSettings';
import CareSettingContextBanner from '../components/CareSettingContextBanner';
import DiseaseAutocomplete from '../components/DiseaseAutocomplete';

interface Medication {
  name: string;
  dosage: string;
  frequency: string;
  instructions: string;
}

interface WizardData {
  patient_name?: string;
  primary_diagnosis: string;
  medications: Medication[];
  follow_up_appointments: string[];
  activity_restrictions: string[];
  diet_instructions?: string;
  warning_signs: string[];
  emergency_criteria: string[];
  wound_care?: string;
  equipment_needs: string[];
  home_care_services?: string;
}

export default function DischargeInstructions() {
  const [currentStep, setCurrentStep] = useState(0);
  const [data, setData] = useState<WizardData>({
    primary_diagnosis: '',
    medications: [],
    follow_up_appointments: [],
    activity_restrictions: [],
    warning_signs: [],
    emergency_criteria: [],
    equipment_needs: []
  });
  const [isGenerating, setIsGenerating] = useState(false);

  // Care setting integration
  const { careSetting } = useCareSettings();
  const { getTemplateDefaults } = useCareSettingTemplates();

  // Load care setting template defaults
  useEffect(() => {
    if (careSetting) {
      const defaults = getTemplateDefaults('discharge');
      console.log('Discharge defaults for', careSetting, ':', defaults);
    }
  }, [careSetting, getTemplateDefaults]);

  const steps = [
    { id: 0, title: 'Patient Info', icon: 'fa-user' },
    { id: 1, title: 'Diagnosis', icon: 'fa-stethoscope' },
    { id: 2, title: 'Medications', icon: 'fa-pills' },
    { id: 3, title: 'Follow-up', icon: 'fa-calendar-check' },
    { id: 4, title: 'Instructions', icon: 'fa-clipboard-list' },
    { id: 5, title: 'Safety', icon: 'fa-exclamation-triangle' },
    { id: 6, title: 'Review', icon: 'fa-eye' }
  ];

  const updateData = (field: keyof WizardData, value: any) => {
    setData({ ...data, [field]: value });
  };

  const addMedication = () => {
    setData({
      ...data,
      medications: [...data.medications, { name: '', dosage: '', frequency: '', instructions: '' }]
    });
  };

  const updateMedication = (index: number, field: keyof Medication, value: string) => {
    const updatedMeds = [...data.medications];
    updatedMeds[index] = { ...updatedMeds[index], [field]: value };
    setData({ ...data, medications: updatedMeds });
  };

  const removeMedication = (index: number) => {
    setData({ ...data, medications: data.medications.filter((_, i) => i !== index) });
  };

  const addArrayItem = (field: keyof WizardData, value: string) => {
    if (!value.trim()) return;
    const currentArray = (data[field] as string[]) || [];
    updateData(field, [...currentArray, value]);
  };

  const removeArrayItem = (field: keyof WizardData, index: number) => {
    const currentArray = (data[field] as string[]) || [];
    updateData(field, currentArray.filter((_, i) => i !== index));
  };

  const validateStep = (): boolean => {
    switch (currentStep) {
      case 1:
        if (!data.primary_diagnosis.trim()) {
          alert('Please enter the primary diagnosis');
          return false;
        }
        break;
      case 5:
        if (data.warning_signs.length === 0 || data.emergency_criteria.length === 0) {
          alert('Please add warning signs and emergency criteria for patient safety');
          return false;
        }
        break;
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
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleGenerate = async (format: 'pdf' | 'docx' | 'txt' = 'pdf') => {
    setIsGenerating(true);
    try {
      const response = await fetch('/api/v1/patient-documents/discharge-instructions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...data,
          care_setting: careSetting || 'med-surg',
          format: format
        }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const fileExtension = format === 'docx' ? 'docx' : format === 'txt' ? 'txt' : 'pdf';
        a.download = `discharge-instructions-${data.patient_name || 'patient'}.${fileExtension}`;
        a.click();
        window.URL.revokeObjectURL(url);
        alert(`Discharge instructions exported as ${format.toUpperCase()} successfully!`);
      } else {
        alert('Failed to generate discharge instructions. Please try again.');
      }
    } catch (error) {
      console.error('Error generating discharge instructions:', error);
      alert('An error occurred. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const [newItem, setNewItem] = useState('');

  const renderStepContent = () => {

    switch (currentStep) {
      case 0: // Patient Info
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Patient Name (Optional - for privacy)
              </label>
              <input
                type="text"
                value={data.patient_name || ''}
                onChange={(e) => updateData('patient_name', e.target.value)}
                placeholder="Patient initials or ID (e.g., J.D., Room 412)"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-sm text-gray-500 mt-1">
                <i className="fas fa-info-circle mr-1"></i>
                Use initials or room number for patient privacy
              </p>
            </div>
          </div>
        );

      case 1: // Diagnosis
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Primary Diagnosis <span className="text-red-500">*</span>
              </label>
              <p className="text-sm text-gray-500 mb-2">
                Start typing to search for a disease or condition. Autocomplete suggestions will appear instantly.
              </p>
              <DiseaseAutocomplete
                value={data.primary_diagnosis}
                onChange={(value) => updateData('primary_diagnosis', value)}
                onSelect={(disease) => updateData('primary_diagnosis', disease)}
                placeholder={
                  careSetting === 'icu'
                    ? 'e.g., Acute respiratory failure, septic shock...'
                    : careSetting === 'emergency'
                    ? 'e.g., Acute appendicitis, closed head injury...'
                    : 'e.g., Pneumonia, CHF exacerbation, Diabetes...'
                }
                enableVoice={true}
              />
            </div>
          </div>
        );

      case 2: // Medications
        return (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h4 className="font-semibold text-gray-800">Discharge Medications</h4>
              <button
                onClick={addMedication}
                className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
              >
                <i className="fas fa-plus mr-1"></i>Add Medication
              </button>
            </div>
            {data.medications.map((med, index) => (
              <div key={index} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <div className="flex justify-between items-start mb-3">
                  <h5 className="font-medium text-gray-700">Medication {index + 1}</h5>
                  <button
                    onClick={() => removeMedication(index)}
                    className="text-red-600 hover:text-red-800 text-sm"
                  >
                    <i className="fas fa-trash"></i>
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <input
                    type="text"
                    value={med.name}
                    onChange={(e) => updateMedication(index, 'name', e.target.value)}
                    placeholder="Medication name"
                    className="p-2 border border-gray-300 rounded"
                  />
                  <input
                    type="text"
                    value={med.dosage}
                    onChange={(e) => updateMedication(index, 'dosage', e.target.value)}
                    placeholder="Dosage (e.g., 500 mg)"
                    className="p-2 border border-gray-300 rounded"
                  />
                  <input
                    type="text"
                    value={med.frequency}
                    onChange={(e) => updateMedication(index, 'frequency', e.target.value)}
                    placeholder="Frequency (e.g., twice daily)"
                    className="p-2 border border-gray-300 rounded"
                  />
                  <input
                    type="text"
                    value={med.instructions}
                    onChange={(e) => updateMedication(index, 'instructions', e.target.value)}
                    placeholder="Instructions (e.g., with food)"
                    className="p-2 border border-gray-300 rounded"
                  />
                </div>
              </div>
            ))}
            {data.medications.length === 0 && (
              <p className="text-gray-500 text-center py-4">No medications added yet</p>
            )}
          </div>
        );

      case 3: // Follow-up
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Follow-up Appointments
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={newItem}
                  onChange={(e) => setNewItem(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      addArrayItem('follow_up_appointments', newItem);
                      setNewItem('');
                    }
                  }}
                  placeholder="e.g., See your primary care doctor in 7-10 days"
                  className="flex-1 p-2 border border-gray-300 rounded"
                />
                <button
                  onClick={() => {
                    addArrayItem('follow_up_appointments', newItem);
                    setNewItem('');
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Add
                </button>
              </div>
              <ul className="space-y-2">
                {data.follow_up_appointments.map((item, index) => (
                  <li key={index} className="flex justify-between items-center bg-gray-50 p-2 rounded">
                    <span>{item}</span>
                    <button
                      onClick={() => removeArrayItem('follow_up_appointments', index)}
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

      case 4: // Instructions
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Activity Restrictions
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={newItem}
                  onChange={(e) => setNewItem(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      addArrayItem('activity_restrictions', newItem);
                      setNewItem('');
                    }
                  }}
                  placeholder="e.g., No heavy lifting for 2 weeks"
                  className="flex-1 p-2 border border-gray-300 rounded"
                />
                <button
                  onClick={() => {
                    addArrayItem('activity_restrictions', newItem);
                    setNewItem('');
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Add
                </button>
              </div>
              <ul className="space-y-2">
                {data.activity_restrictions.map((item, index) => (
                  <li key={index} className="flex justify-between items-center bg-gray-50 p-2 rounded">
                    <span>{item}</span>
                    <button
                      onClick={() => removeArrayItem('activity_restrictions', index)}
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
                Diet Instructions (Optional)
              </label>
              <textarea
                value={data.diet_instructions || ''}
                onChange={(e) => updateData('diet_instructions', e.target.value)}
                placeholder="e.g., Low sodium diet, drink plenty of fluids..."
                rows={3}
                className="w-full p-3 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Wound Care (Optional)
              </label>
              <textarea
                value={data.wound_care || ''}
                onChange={(e) => updateData('wound_care', e.target.value)}
                placeholder="e.g., Keep incision clean and dry, change dressing daily..."
                rows={3}
                className="w-full p-3 border border-gray-300 rounded-lg"
              />
            </div>
          </div>
        );

      case 5: // Safety
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Warning Signs to Watch For <span className="text-red-500">*</span>
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={newItem}
                  onChange={(e) => setNewItem(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      addArrayItem('warning_signs', newItem);
                      setNewItem('');
                    }
                  }}
                  placeholder="e.g., Fever over 101°F, increased pain..."
                  className="flex-1 p-2 border border-gray-300 rounded"
                />
                <button
                  onClick={() => {
                    addArrayItem('warning_signs', newItem);
                    setNewItem('');
                  }}
                  className="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700"
                >
                  Add
                </button>
              </div>
              <ul className="space-y-2">
                {data.warning_signs.map((item, index) => (
                  <li key={index} className="flex justify-between items-center bg-yellow-50 p-2 rounded border-l-4 border-yellow-500">
                    <span>{item}</span>
                    <button
                      onClick={() => removeArrayItem('warning_signs', index)}
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
                When to Call 911 / Go to ER <span className="text-red-500">*</span>
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={newItem}
                  onChange={(e) => setNewItem(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      addArrayItem('emergency_criteria', newItem);
                      setNewItem('');
                    }
                  }}
                  placeholder="e.g., Severe difficulty breathing, chest pain..."
                  className="flex-1 p-2 border border-gray-300 rounded"
                />
                <button
                  onClick={() => {
                    addArrayItem('emergency_criteria', newItem);
                    setNewItem('');
                  }}
                  className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                >
                  Add
                </button>
              </div>
              <ul className="space-y-2">
                {data.emergency_criteria.map((item, index) => (
                  <li key={index} className="flex justify-between items-center bg-red-50 p-2 rounded border-l-4 border-red-500">
                    <span>{item}</span>
                    <button
                      onClick={() => removeArrayItem('emergency_criteria', index)}
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

      case 6: // Review
        return (
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">Patient</h4>
              <p className="text-gray-700">{data.patient_name || 'Not specified'}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">Diagnosis</h4>
              <p className="text-gray-700">{data.primary_diagnosis}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">Medications</h4>
              <p className="text-gray-700">{data.medications.length} medication(s)</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">Warning Signs</h4>
              <p className="text-gray-700">{data.warning_signs.length} warning sign(s)</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">Emergency Criteria</h4>
              <p className="text-gray-700">{data.emergency_criteria.length} criteria</p>
            </div>
            <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
              <p className="text-sm text-blue-900">
                <i className="fas fa-info-circle mr-2"></i>
                Click "Generate" to create your discharge instructions PDF
              </p>
            </div>
          </div>
        );

      default:
        return <div>Unknown step</div>;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Discharge Instructions Wizard</h1>
          <p className="text-gray-600">Comprehensive patient discharge documentation</p>
        </div>

        {/* Care Setting Banner */}
        {careSetting && <CareSettingContextBanner className="mb-6" />}

        {/* Wizard Container */}
        <div className="wizard-container bg-white rounded-lg shadow-lg overflow-visible">
          {/* Progress Steps */}
          <div className="wizard-progress bg-gray-50 p-6 rounded-t-lg">
            <div className="flex justify-between items-center">
              {steps.map((step, index) => (
                <div key={step.id} className="flex flex-col items-center flex-1">
                  <button
                    onClick={() => setCurrentStep(index)}
                    className={`w-12 h-12 rounded-full flex items-center justify-center transition-all ${
                      index === currentStep
                        ? 'bg-blue-600 text-white ring-4 ring-blue-200'
                        : index < currentStep
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-200 text-gray-600'
                    }`}
                  >
                    <i className={`fas ${step.icon}`}></i>
                  </button>
                  <span className="text-xs mt-2 font-medium text-gray-600">{step.title}</span>
                  {index < steps.length - 1 && (
                    <div className={`h-1 w-full mt-4 ${index < currentStep ? 'bg-green-500' : 'bg-gray-200'}`}></div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Step Content */}
          <div className="wizard-content p-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">{steps[currentStep].title}</h3>
            {renderStepContent()}
          </div>

          {/* Navigation */}
          <div className="wizard-navigation bg-gray-50 p-4 rounded-b-lg flex justify-between">
            <button
              onClick={previousStep}
              disabled={currentStep === 0}
              className={`px-6 py-2 text-gray-600 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors ${
                currentStep === 0 ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              <i className="fas fa-arrow-left mr-2"></i>Previous
            </button>

            {currentStep === steps.length - 1 ? (
              <div className="flex gap-2">
                <button
                  onClick={() => handleGenerate('pdf')}
                  disabled={isGenerating}
                  className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
                >
                  {isGenerating ? (
                    <>
                      <i className="fas fa-spinner fa-spin mr-2"></i>Generating...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-file-pdf mr-2"></i>Export PDF
                    </>
                  )}
                </button>
                <button
                  onClick={() => handleGenerate('docx')}
                  disabled={isGenerating}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  <i className="fas fa-file-word mr-2"></i>Export Word
                </button>
                <button
                  onClick={() => handleGenerate('txt')}
                  disabled={isGenerating}
                  className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50"
                >
                  <i className="fas fa-file-alt mr-2"></i>Export Text
                </button>
              </div>
            ) : (
              <button
                onClick={nextStep}
                disabled={isGenerating}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                Next<i className="fas fa-arrow-right ml-2"></i>
              </button>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-gray-600 text-sm">
          <p>&copy; 2025 AI Nurse Florence</p>
        </div>
      </div>

      {/* Help System */}
      <HelpSystem />
    </div>
  );
}
