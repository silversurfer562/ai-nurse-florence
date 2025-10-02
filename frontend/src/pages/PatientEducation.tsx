import { useState, useEffect } from 'react';
import { HelpSystem } from '../components/Help/HelpSystem';
import { useCareSettings, useCareSettingTemplates } from '../hooks/useCareSettings';
import CareSettingContextBanner from '../components/CareSettingContextBanner';

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
  disease_id: number;
  disease_name: string;
  category: string;
}

export default function PatientEducation() {
  const [currentStep, setCurrentStep] = useState(0);
  const [data, setData] = useState<WizardData>({});
  const [diagnosisQuery, setDiagnosisQuery] = useState('');
  const [diagnosisResults, setDiagnosisResults] = useState<DiagnosisOption[]>([]);
  const [selectedDiagnosis, setSelectedDiagnosis] = useState<DiagnosisOption | null>(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);

  // Care setting integration
  const { careSetting } = useCareSettings();
  const { getTemplateDefaults } = useCareSettingTemplates();

  // Load care setting template defaults when setting changes
  useEffect(() => {
    if (careSetting) {
      const defaults = getTemplateDefaults('patient-education');
      setData((prev) => ({
        ...prev,
        reading_level: defaults.readingLevel || prev.reading_level || 'middle',
        language: prev.language || 'en',
      }));
    }
  }, [careSetting, getTemplateDefaults]);

  const steps: WizardStep[] = [
    {
      title: 'Select Diagnosis',
      description: 'Choose the primary diagnosis for patient education',
      render: (data) => (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Search for Diagnosis <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <i className="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
            <input
              type="text"
              value={diagnosisQuery}
              onChange={(e) => handleDiagnosisSearch(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => diagnosisResults.length > 0 && setShowDropdown(true)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Type the disease name (e.g., diabetes, hypertension, asthma)..."
              autoComplete="off"
            />
            {showDropdown && diagnosisResults.length > 0 && (
              <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                {diagnosisResults.map((result, index) => (
                  <div
                    key={result.disease_id}
                    onClick={() => selectDiagnosis(result)}
                    className={`px-4 py-2 cursor-pointer ${
                      index === highlightedIndex ? 'bg-blue-50' : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className="font-medium text-gray-900">{result.disease_name}</div>
                    <div className="text-xs text-gray-500">{result.category}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
          {selectedDiagnosis && (
            <div className="mt-3 bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-center justify-between">
              <div>
                <div className="font-medium text-blue-900">{selectedDiagnosis.disease_name}</div>
                <div className="text-xs text-blue-700">{selectedDiagnosis.category}</div>
              </div>
              <button
                onClick={() => {
                  setSelectedDiagnosis(null);
                  setDiagnosisQuery('');
                  setData({ ...data, diagnosis_id: '', diagnosis_name: '' });
                }}
                className="text-blue-600 hover:text-blue-800"
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
          )}
          <p className="text-sm text-gray-500 mt-2">
            <i className="fas fa-info-circle mr-1"></i>
            Start typing the disease name - results refine as you type. Use arrow keys to navigate, Enter to select.
          </p>
        </div>
      ),
    },
    {
      title: 'Patient Information',
      description: 'Provide basic patient demographics',
      fields: [
        {
          id: 'reading_level',
          type: 'select',
          label: 'Reading Level',
          required: true,
          help: 'Choose the appropriate reading level for the patient',
          options: [
            { value: 'elementary', label: 'Elementary (Grades 3-5)' },
            { value: 'middle', label: 'Middle School (Grades 6-8) - Recommended' },
            { value: 'high', label: 'High School (Grades 9-12)' },
          ],
        },
        {
          id: 'language',
          type: 'select',
          label: 'Language',
          required: true,
          help: 'Select the patient\'s preferred language',
          options: [
            { value: 'en', label: 'English' },
            { value: 'es', label: 'Spanish' },
            { value: 'zh', label: 'Chinese (Mandarin)' },
            { value: 'hi', label: 'Hindi' },
            { value: 'ar', label: 'Arabic' },
            { value: 'pt', label: 'Portuguese' },
            { value: 'bn', label: 'Bengali' },
            { value: 'ru', label: 'Russian' },
            { value: 'ja', label: 'Japanese' },
            { value: 'pa', label: 'Punjabi' },
            { value: 'de', label: 'German' },
            { value: 'ko', label: 'Korean' },
            { value: 'fr', label: 'French' },
            { value: 'vi', label: 'Vietnamese' },
            { value: 'it', label: 'Italian' },
            { value: 'tl', label: 'Tagalog' },
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

  const handleDiagnosisSearch = async (query: string) => {
    setDiagnosisQuery(query);
    setHighlightedIndex(-1);

    if (query.length >= 3) {
      try {
        const response = await fetch(`/api/v1/content-settings/diagnosis/search?q=${encodeURIComponent(query)}&limit=15`);
        const results = await response.json();
        setDiagnosisResults(results);
        setShowDropdown(true);
      } catch (error) {
        console.error('Failed to search diagnoses:', error);
        setDiagnosisResults([]);
      }
    } else {
      setDiagnosisResults([]);
      setShowDropdown(false);
    }
  };

  const selectDiagnosis = (diagnosis: DiagnosisOption) => {
    setSelectedDiagnosis(diagnosis);
    setDiagnosisQuery(diagnosis.disease_name);
    setData({
      ...data,
      diagnosis_id: diagnosis.disease_id,
      diagnosis_name: diagnosis.disease_name,
    });
    setShowDropdown(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showDropdown || diagnosisResults.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex((prev) => (prev < diagnosisResults.length - 1 ? prev + 1 : prev));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0 && highlightedIndex < diagnosisResults.length) {
          selectDiagnosis(diagnosisResults[highlightedIndex]);
        }
        break;
      case 'Escape':
        setShowDropdown(false);
        break;
    }
  };

  const updateData = (field: string, value: string) => {
    setData({ ...data, [field]: value });
  };

  const validateStep = (): boolean => {
    const step = steps[currentStep];

    // Special validation for diagnosis step
    if (currentStep === 0) {
      if (!selectedDiagnosis) {
        alert('Please select a diagnosis');
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
    try {
      const format = data.format || 'pdf';

      const response = await fetch('/api/v1/documents/patient-education', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...data,
          format,
          care_setting: careSetting || 'med-surg'
        }),
      });

      if (response.ok) {
        const result = await response.json();
        // Open the PDF URL in a new tab or download it
        if (result.pdf_url) {
          window.open(result.pdf_url, '_blank');
        }
      } else {
        alert('Failed to generate document. Please try again.');
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
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {field.label} {field.required && <span className="text-red-500">*</span>}
            </label>
            <input
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
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {field.label} {field.required && <span className="text-red-500">*</span>}
            </label>
            <select
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
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {field.label} {field.required && <span className="text-red-500">*</span>}
            </label>
            <textarea
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
            <p className="text-gray-700">{selectedDiagnosis?.disease_name || data.diagnosis_name}</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-2">Reading Level</h4>
            <p className="text-gray-700 capitalize">{data.reading_level}</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-2">Language</h4>
            <p className="text-gray-700">{data.language}</p>
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
      <div className="container mx-auto px-4 py-8 max-w-4xl">
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

      {/* Help System */}
      <HelpSystem />
    </div>
  );
}
