import { useState, useEffect } from 'react';
import { useCareSettings, useCareSettingTemplates } from '../hooks/useCareSettings';
import { useDocumentLanguage } from '../hooks/useDocumentLanguage';
import CareSettingContextBanner from '../components/CareSettingContextBanner';
import DiagnosisSelector from '../components/DiagnosisSelector';

interface WizardData {
  [key: string]: string | number;
}

interface WizardStep {
  title: string;
  description?: string;
  fields?: WizardField[];
  render?: (data: WizardData) => React.ReactNode;
}

interface WizardField {
  id: string;
  type: 'text' | 'select' | 'textarea' | 'radio';
  label: string;
  placeholder?: string;
  required?: boolean;
  help?: string;
  options?: Array<{ value: string; label: string }>;
  rows?: number;
}

interface DiagnosisOption {
  id: string;
  label: string;
  value: string;
  icd10_code: string;
}

export default function PatientEducation() {
  const [currentStep, setCurrentStep] = useState(0);
  const [data, setData] = useState<WizardData>({});
  const [selectedDiagnosis, setSelectedDiagnosis] = useState<DiagnosisOption | null>(null);

  // Care setting integration
  const { careSetting } = useCareSettings();
  const { getTemplateDefaults } = useCareSettingTemplates();

  // Document language from settings
  const { documentLanguage } = useDocumentLanguage();

  // Load care setting template defaults when setting changes
  useEffect(() => {
    if (careSetting) {
      const defaults = getTemplateDefaults('patient-education');
      setData((prev) => ({
        ...prev,
        reading_level: defaults.readingLevel || prev.reading_level || 'middle',
      }));
    }
  }, [careSetting, getTemplateDefaults]);

  // Auto-set language from document language setting
  useEffect(() => {
    setData((prev) => ({
      ...prev,
      language: documentLanguage,
    }));
  }, [documentLanguage]);

  const steps: WizardStep[] = [
    {
      title: 'Select Diagnosis',
      description: 'Choose the primary diagnosis from the content library for patient education',
      render: (data) => (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Search for Diagnosis <span className="text-red-500">*</span>
          </label>
          <DiagnosisSelector
            onChange={(diagnosis) => {
              setSelectedDiagnosis(diagnosis);
              if (diagnosis) {
                setData({
                  ...data,
                  diagnosis_id: diagnosis.id,
                  diagnosis_name: diagnosis.label,
                  icd10_code: diagnosis.icd10_code,
                });
              } else {
                setData({ ...data, diagnosis_id: '', diagnosis_name: '', icd10_code: '' });
              }
            }}
            placeholder="Type to search for diagnosis (e.g., diabetes, hypertension, pneumonia)..."
          />
          <p className="text-sm text-gray-500 mt-2">
            <i className="fas fa-info-circle mr-1"></i>
            Start typing the diagnosis name (minimum 2 characters). Only diagnoses from the content library with verified medical information will appear.
          </p>
          {selectedDiagnosis && (
            <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                <i className="fas fa-check-circle mr-2"></i>
                <strong>Selected:</strong> {selectedDiagnosis.label}
              </p>
              <p className="text-xs text-blue-600 mt-1">
                ICD-10: {selectedDiagnosis.icd10_code}
              </p>
            </div>
          )}
        </div>
      ),
    },
    {
      title: 'Patient Information',
      description: 'Provide basic patient demographics',
      fields: [
        {
          id: 'patient_name',
          type: 'text',
          label: 'Patient Name',
          placeholder: 'Enter patient name',
          required: true,
          help: 'Patient name for document personalization (not stored)',
        },
        {
          id: 'preferred_language',
          type: 'select',
          label: 'Preferred Language',
          required: true,
          help: 'Language for the patient education document',
          options: [
            { value: 'en', label: 'English' },
            { value: 'es', label: 'Spanish (Español)' },
            { value: 'zh', label: 'Chinese (中文)' },
          ],
        },
        {
          id: 'reading_level',
          type: 'select',
          label: 'Reading Level',
          required: true,
          help: 'Choose the appropriate reading level for the patient',
          options: [
            { value: 'basic', label: 'Basic (Grades 3-5)' },
            { value: 'intermediate', label: 'Intermediate (Grades 6-8) - Recommended' },
            { value: 'advanced', label: 'Advanced (Grades 9-12)' },
          ],
        },
      ],
    },
    {
      title: 'Content Preferences',
      description: 'Customize the educational content',
      fields: [
        {
          id: 'include_images',
          type: 'radio',
          label: 'Include Diagrams/Images',
          required: true,
          options: [
            { value: 'yes', label: 'Yes, include visual aids' },
            { value: 'no', label: 'No, text only' },
          ],
        },
        {
          id: 'format',
          type: 'select',
          label: 'Download Format',
          required: true,
          help: 'Choose the file format for the patient education document',
          options: [
            { value: 'pdf', label: 'PDF (Recommended)' },
            { value: 'docx', label: 'Word Document (.docx)' },
            { value: 'text', label: 'Plain Text (.txt)' },
          ],
        },
        {
          id: 'sections',
          type: 'textarea',
          label: 'Additional Topics (Optional)',
          placeholder: 'E.g., Diet recommendations, Exercise tips, Medication reminders...',
          rows: 4,
          help: 'List any specific topics you want included in the education material',
        },
      ],
    },
    {
      title: 'Review & Generate',
      description: 'Review your selections and generate the patient education document',
    },
  ];


  const updateData = (field: string, value: string) => {
    setData({ ...data, [field]: value });
  };

  const validateStep = (): boolean => {
    const step = steps[currentStep];

    // Special validation for diagnosis step
    if (currentStep === 0) {
      if (!data.diagnosis_id || !selectedDiagnosis) {
        alert('Please select a diagnosis from the dropdown list. Start typing to see available options.');
        return false;
      }
      return true;
    }

    // Validate required fields
    if (step.fields) {
      for (const field of step.fields) {
        if (field.required && !data[field.id]) {
          alert(`Please fill in: ${field.label}`);
          return false;
        }
      }
    }

    return true;
  };

  const nextStep = () => {
    if (!validateStep()) return;

    if (currentStep === steps.length - 1) {
      handleComplete();
    } else {
      setCurrentStep(currentStep + 1);
    }
  };

  const previousStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = async () => {
    console.log('=== handleComplete called ===');
    console.log('Current data:', data);
    console.log('Selected diagnosis:', selectedDiagnosis);
    console.log('Care setting:', careSetting);

    try {
      const format = data.format || 'pdf';

      const requestPayload = {
        ...data,
        format,
        care_setting: careSetting || 'med-surg'
      };

      console.log('About to send POST request with payload:', requestPayload);

      const response = await fetch('/api/v1/documents/patient-education', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestPayload),
      });

      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);

      if (response.ok) {
        const result = await response.json();
        // Open the PDF URL in a new tab or download it
        if (result.pdf_url) {
          window.open(result.pdf_url, '_blank');
        }
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        console.error('Patient education generation failed:', errorData);
        console.error('Request data sent:', { ...data, format, care_setting: careSetting || 'med-surg' });
        const errorMessage = typeof errorData.detail === 'string'
          ? errorData.detail
          : JSON.stringify(errorData.detail, null, 2);
        alert(`Failed to generate document: ${errorMessage}`);
      }
    } catch (error) {
      console.error('Error generating document:', error);
      alert('An error occurred. Please try again.');
    }
  };

  const renderField = (field: WizardField) => {
    switch (field.type) {
      case 'text':
        return (
          <div className="mb-4" key={field.id}>
            <label htmlFor={field.id} className="block text-sm font-medium text-gray-700 mb-2">
              {field.label} {field.required && <span className="text-red-500">*</span>}
            </label>
            <input
              id={field.id}
              name={field.id}
              type="text"
              value={data[field.id] || ''}
              onChange={(e) => updateData(field.id, e.target.value)}
              placeholder={field.placeholder}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            {field.help && <p className="text-sm text-gray-500 mt-1">{field.help}</p>}
          </div>
        );

      case 'select':
        return (
          <div className="mb-4" key={field.id}>
            <label htmlFor={field.id} className="block text-sm font-medium text-gray-700 mb-2">
              {field.label} {field.required && <span className="text-red-500">*</span>}
            </label>
            <select
              id={field.id}
              name={field.id}
              value={data[field.id] || ''}
              onChange={(e) => updateData(field.id, e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select {field.label}</option>
              {field.options?.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            {field.help && <p className="text-sm text-gray-500 mt-1">{field.help}</p>}
          </div>
        );

      case 'textarea':
        return (
          <div className="mb-4" key={field.id}>
            <label htmlFor={field.id} className="block text-sm font-medium text-gray-700 mb-2">
              {field.label} {field.required && <span className="text-red-500">*</span>}
            </label>
            <textarea
              id={field.id}
              name={field.id}
              value={data[field.id] || ''}
              onChange={(e) => updateData(field.id, e.target.value)}
              placeholder={field.placeholder}
              rows={field.rows || 4}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            {field.help && <p className="text-sm text-gray-500 mt-1">{field.help}</p>}
          </div>
        );

      case 'radio':
        return (
          <div className="mb-4" key={field.id}>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {field.label} {field.required && <span className="text-red-500">*</span>}
            </label>
            <div className="space-y-2">
              {field.options?.map((opt) => (
                <label key={opt.value} className="flex items-center">
                  <input
                    type="radio"
                    name={field.id}
                    value={opt.value}
                    checked={data[field.id] === opt.value}
                    onChange={(e) => updateData(field.id, e.target.value)}
                    className="mr-2 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-gray-700">{opt.label}</span>
                </label>
              ))}
            </div>
            {field.help && <p className="text-sm text-gray-500 mt-1">{field.help}</p>}
          </div>
        );

      default:
        return null;
    }
  };

  const renderStepContent = () => {
    const step = steps[currentStep];

    if (step.render) {
      return step.render(data);
    }

    if (currentStep === steps.length - 1) {
      const formatLabels: Record<string, string> = {
        pdf: 'PDF',
        docx: 'Word Document (.docx)',
        text: 'Plain Text (.txt)',
      };

      return (
        <div className="space-y-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-2">Selected Diagnosis</h4>
            <p className="text-gray-700">{selectedDiagnosis?.label || data.diagnosis_name}</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-2">Reading Level</h4>
            <p className="text-gray-700 capitalize">{data.reading_level}</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-2 flex items-center justify-between">
              <span>Language</span>
              <a href="/settings" className="text-sm text-blue-600 hover:text-blue-800">
                <i className="fas fa-cog mr-1"></i>
                Change in Settings
              </a>
            </h4>
            <p className="text-gray-700">{data.language}</p>
            <p className="text-xs text-gray-500 mt-1">
              <i className="fas fa-info-circle mr-1"></i>
              Document language is managed in Settings → Language
            </p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-2">Download Format</h4>
            <p className="text-gray-700">{formatLabels[data.format as string] || data.format}</p>
          </div>
          <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
            <p className="text-sm text-blue-900">
              <i className="fas fa-info-circle mr-2"></i>
              Click "Complete" to generate your patient education document in {formatLabels[data.format as string] || 'the selected'} format.
            </p>
          </div>
        </div>
      );
    }

    return <div className="space-y-4">{step.fields?.map(renderField)}</div>;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8 max-w-3xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Patient Education Wizard</h1>
          <p className="text-gray-600">Generate customized patient education materials</p>
        </div>

        {/* Care Setting Context Banner */}
        {careSetting && <CareSettingContextBanner className="mb-6" />}

        {/* Wizard Container */}
        <div className="wizard-container bg-white rounded-lg shadow-lg overflow-visible">
          {/* Wizard Header */}
          <div className="wizard-header bg-blue-600 text-white p-6 rounded-t-lg">
            <h2 className="text-2xl font-bold">Patient Education Document</h2>
            <p className="text-blue-100 mt-2">Complete the steps below to generate your patient education material</p>
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
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
              ></div>
            </div>
            <div className="flex justify-between mt-2">
              {steps.map((step, index) => (
                <div key={index} className="flex flex-col items-center">
                  <button
                    onClick={() => setCurrentStep(index)}
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                      index <= currentStep
                        ? 'bg-blue-600 text-white hover:bg-blue-700'
                        : 'bg-gray-300 text-gray-600 hover:bg-gray-400'
                    } ${index === currentStep ? 'ring-2 ring-blue-400 ring-offset-2' : ''}`}
                    title={`Go to step ${index + 1}: ${step.title}`}
                  >
                    {index + 1}
                  </button>
                  <span className="text-xs text-gray-600 mt-1">{step.title}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Step Content */}
          <div className="wizard-content p-6 overflow-visible">
            <div className="step-content">
              <h3 className="text-xl font-bold text-gray-800 mb-4">{steps[currentStep].title}</h3>
              {steps[currentStep].description && (
                <p className="text-gray-600 mb-6">{steps[currentStep].description}</p>
              )}
              <div className="step-fields">{renderStepContent()}</div>
            </div>
          </div>

          {/* Navigation */}
          <div className="wizard-navigation bg-gray-50 p-4 rounded-b-lg flex justify-between">
            <button
              onClick={previousStep}
              disabled={currentStep === 0}
              className={`px-4 py-2 text-gray-600 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors ${
                currentStep === 0 ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              <i className="fas fa-arrow-left mr-2"></i>Previous
            </button>

            <button
              onClick={nextStep}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              {currentStep === steps.length - 1 ? (
                <>
                  <i className="fas fa-check mr-2"></i>Complete
                </>
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
