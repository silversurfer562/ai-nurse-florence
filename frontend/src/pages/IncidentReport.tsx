import { useState, useEffect } from 'react';
import Joyride, { Step, CallBackProps, STATUS } from 'react-joyride';
import { useCareSettings, useCareSettingTemplates } from '../hooks/useCareSettings';
import CareSettingContextBanner from '../components/CareSettingContextBanner';

interface WizardData {
  incident_date: string;
  incident_time: string;
  location: string;
  patient_id?: string;
  incident_type: string;
  severity: string;
  description: string;
  immediate_action: string;
  witnesses: string[];
  injuries?: string;
  equipment_involved?: string;
  contributing_factors: string[];
  preventive_measures: string[];
  reporter_name: string;
  reporter_role: string;
}

export default function IncidentReport() {
  const [currentStep, setCurrentStep] = useState(0);
  const [data, setData] = useState<WizardData>({
    incident_date: new Date().toISOString().split('T')[0],
    incident_time: new Date().toTimeString().slice(0, 5),
    location: '',
    incident_type: '',
    severity: 'minor',
    description: '',
    immediate_action: '',
    witnesses: [],
    contributing_factors: [],
    preventive_measures: [],
    reporter_name: '',
    reporter_role: 'Registered Nurse'
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
          <p className="mb-2">Welcome to the Incident Report Wizard! Document safety events objectively and thoroughly.</p>
          <p className="text-sm text-gray-600 mt-3 pt-2 border-t border-gray-200">
            💡 <strong>Tip:</strong> Press <kbd className="px-2 py-1 bg-gray-100 rounded border border-gray-300">ESC</kbd> anytime to exit this tour
          </p>
        </div>
      ),
      disableBeacon: true,
    },
    {
      target: '.wizard-progress',
      content: 'Track your progress through all seven steps: When & Where, What Happened, Details, Response, Analysis, Reporter Info, and Review.',
    },
    {
      target: '.wizard-content',
      content: 'Complete each section objectively. Focus on facts, not blame. This tool helps create thorough safety documentation.',
    },
    {
      target: '.help-button',
      content: 'Need help anytime? Click this button to restart the tour.',
    },
  ];

  // Auto-launch tour on first visit
  useEffect(() => {
    const tourSeen = localStorage.getItem('incidentReportTourSeen');
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
      localStorage.setItem('incidentReportTourSeen', 'true');
    }
  };

  useEffect(() => {
    if (careSetting) {
      const defaults = getTemplateDefaults('incident-report');
      if (defaults.location) {
        updateData('location', defaults.location);
      }
    }
  }, [careSetting, getTemplateDefaults]);

  const steps = [
    { title: 'When & Where', icon: 'fa-clock' },
    { title: 'What Happened', icon: 'fa-exclamation-circle' },
    { title: 'Details', icon: 'fa-clipboard' },
    { title: 'Response', icon: 'fa-first-aid' },
    { title: 'Analysis', icon: 'fa-search' },
    { title: 'Reporter Info', icon: 'fa-user-md' },
    { title: 'Review', icon: 'fa-check' }
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
    switch (currentStep) {
      case 0:
        if (!data.location.trim()) {
          alert('Please enter the incident location');
          return false;
        }
        break;
      case 1:
        if (!data.incident_type.trim() || !data.description.trim()) {
          alert('Please select incident type and provide description');
          return false;
        }
        break;
      case 3:
        if (!data.immediate_action.trim()) {
          alert('Please describe the immediate action taken');
          return false;
        }
        break;
      case 5:
        if (!data.reporter_name.trim()) {
          alert('Please enter reporter information');
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
    if (currentStep > 0) setCurrentStep(currentStep - 1);
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      // Placeholder - actual API endpoint would be created
      const response = await fetch('/api/v1/incident-reports/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...data, care_setting: careSetting || 'med-surg' }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `incident-report-${data.incident_date}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
        alert('Incident report generated successfully!');
      } else {
        // Fallback: create text report
        const reportText = `
INCIDENT REPORT

Date: ${data.incident_date} ${data.incident_time}
Location: ${data.location}
Severity: ${data.severity.toUpperCase()}

INCIDENT TYPE: ${data.incident_type}

DESCRIPTION:
${data.description}

IMMEDIATE ACTION TAKEN:
${data.immediate_action}

WITNESSES:
${data.witnesses.join('\n') || 'None'}

CONTRIBUTING FACTORS:
${data.contributing_factors.join('\n') || 'None identified'}

PREVENTIVE MEASURES:
${data.preventive_measures.join('\n') || 'To be determined'}

REPORTED BY:
${data.reporter_name} - ${data.reporter_role}

Care Setting: ${careSetting || 'Not specified'}
Generated: ${new Date().toLocaleString()}
        `;

        const blob = new Blob([reportText], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `incident-report-${data.incident_date}.txt`;
        a.click();
        window.URL.revokeObjectURL(url);
        alert('Incident report created (text format)');
      }
    } catch (error) {
      console.error('Error generating incident report:', error);
      alert('An error occurred. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0: // When & Where
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Incident Date <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  value={data.incident_date}
                  onChange={(e) => updateData('incident_date', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Incident Time <span className="text-red-500">*</span>
                </label>
                <input
                  type="time"
                  value={data.incident_time}
                  onChange={(e) => updateData('incident_time', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Location <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={data.location}
                onChange={(e) => updateData('location', e.target.value)}
                placeholder={
                  careSetting === 'icu'
                    ? 'e.g., ICU Room 412, ICU Hallway'
                    : careSetting === 'emergency'
                    ? 'e.g., ED Bay 3, Triage Area'
                    : 'e.g., Room 304, Hallway 2B'
                }
                className="w-full p-3 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Patient ID (if applicable)
              </label>
              <input
                type="text"
                value={data.patient_id || ''}
                onChange={(e) => updateData('patient_id', e.target.value)}
                placeholder="Patient initials or ID"
                className="w-full p-3 border border-gray-300 rounded-lg"
              />
            </div>
          </div>
        );

      case 1: // What Happened
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Incident Type <span className="text-red-500">*</span>
              </label>
              <select
                value={data.incident_type}
                onChange={(e) => updateData('incident_type', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg"
              >
                <option value="">Select incident type</option>
                <option value="patient-fall">Patient Fall</option>
                <option value="medication-error">Medication Error</option>
                <option value="equipment-malfunction">Equipment Malfunction</option>
                <option value="pressure-injury">Pressure Injury</option>
                <option value="infection">Healthcare-Associated Infection</option>
                <option value="patient-elopement">Patient Elopement</option>
                <option value="workplace-injury">Staff/Visitor Injury</option>
                <option value="behavioral-event">Behavioral Event</option>
                <option value="specimen-error">Specimen/Lab Error</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Severity Level <span className="text-red-500">*</span>
              </label>
              <select
                value={data.severity}
                onChange={(e) => updateData('severity', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg"
              >
                <option value="minor">Minor - No harm or minimal harm</option>
                <option value="moderate">Moderate - Temporary harm requiring intervention</option>
                <option value="major">Major - Permanent harm or extended hospitalization</option>
                <option value="sentinel">Sentinel Event - Death or serious injury</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description of Incident <span className="text-red-500">*</span>
              </label>
              <textarea
                value={data.description}
                onChange={(e) => updateData('description', e.target.value)}
                placeholder="Describe exactly what happened, including sequence of events..."
                rows={5}
                className="w-full p-3 border border-gray-300 rounded-lg"
              />
            </div>
          </div>
        );

      case 2: // Details
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Injuries/Harm (if any)
              </label>
              <textarea
                value={data.injuries || ''}
                onChange={(e) => updateData('injuries', e.target.value)}
                placeholder="Describe any injuries, patient status changes, or harm..."
                rows={3}
                className="w-full p-3 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Equipment Involved (if any)
              </label>
              <textarea
                value={data.equipment_involved || ''}
                onChange={(e) => updateData('equipment_involved', e.target.value)}
                placeholder="List any equipment involved, including serial/model numbers..."
                rows={3}
                className="w-full p-3 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Witnesses
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={newItem}
                  onChange={(e) => setNewItem(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addArrayItem('witnesses', newItem)}
                  placeholder="Name and role of witness"
                  className="flex-1 p-2 border border-gray-300 rounded"
                />
                <button
                  onClick={() => addArrayItem('witnesses', newItem)}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Add
                </button>
              </div>
              <ul className="space-y-2">
                {data.witnesses.map((item, index) => (
                  <li key={index} className="flex justify-between items-center bg-gray-50 p-2 rounded">
                    <span>{item}</span>
                    <button
                      onClick={() => removeArrayItem('witnesses', index)}
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

      case 3: // Response
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Immediate Action Taken <span className="text-red-500">*</span>
              </label>
              <textarea
                value={data.immediate_action}
                onChange={(e) => updateData('immediate_action', e.target.value)}
                placeholder="Describe the immediate response and any interventions..."
                rows={5}
                className="w-full p-3 border border-gray-300 rounded-lg"
              />
              <p className="text-sm text-gray-500 mt-2">
                <i className="fas fa-info-circle mr-1"></i>
                Include patient assessment, notifications made, and any immediate corrective actions
              </p>
            </div>
          </div>
        );

      case 4: // Analysis
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Contributing Factors
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={newItem}
                  onChange={(e) => setNewItem(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addArrayItem('contributing_factors', newItem)}
                  placeholder="e.g., Understaffing, Equipment failure, Communication breakdown"
                  className="flex-1 p-2 border border-gray-300 rounded"
                />
                <button
                  onClick={() => addArrayItem('contributing_factors', newItem)}
                  className="px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700"
                >
                  Add
                </button>
              </div>
              <ul className="space-y-2">
                {data.contributing_factors.map((item, index) => (
                  <li key={index} className="flex justify-between items-center bg-orange-50 p-2 rounded">
                    <span>{item}</span>
                    <button
                      onClick={() => removeArrayItem('contributing_factors', index)}
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
                Preventive Measures / Recommendations
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={newItem}
                  onChange={(e) => setNewItem(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addArrayItem('preventive_measures', newItem)}
                  placeholder="e.g., Implement hourly rounding, Staff re-education"
                  className="flex-1 p-2 border border-gray-300 rounded"
                />
                <button
                  onClick={() => addArrayItem('preventive_measures', newItem)}
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Add
                </button>
              </div>
              <ul className="space-y-2">
                {data.preventive_measures.map((item, index) => (
                  <li key={index} className="flex justify-between items-center bg-green-50 p-2 rounded">
                    <span>{item}</span>
                    <button
                      onClick={() => removeArrayItem('preventive_measures', index)}
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

      case 5: // Reporter Info
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Reporter Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={data.reporter_name}
                onChange={(e) => updateData('reporter_name', e.target.value)}
                placeholder="Your full name"
                className="w-full p-3 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Role/Title <span className="text-red-500">*</span>
              </label>
              <select
                value={data.reporter_role}
                onChange={(e) => updateData('reporter_role', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg"
              >
                <option value="Registered Nurse">Registered Nurse (RN)</option>
                <option value="Licensed Practical Nurse">Licensed Practical Nurse (LPN)</option>
                <option value="Nurse Practitioner">Nurse Practitioner (NP)</option>
                <option value="Physician">Physician (MD/DO)</option>
                <option value="Nursing Assistant">Certified Nursing Assistant (CNA)</option>
                <option value="Pharmacist">Pharmacist</option>
                <option value="Respiratory Therapist">Respiratory Therapist</option>
                <option value="Other">Other Healthcare Professional</option>
              </select>
            </div>
            <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded">
              <p className="text-sm text-yellow-900">
                <i className="fas fa-shield-alt mr-2"></i>
                This report is for quality improvement purposes and may be subject to peer review protections
              </p>
            </div>
          </div>
        );

      case 6: // Review
        return (
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">Incident Details</h4>
              <p className="text-gray-700">{data.incident_date} at {data.incident_time}</p>
              <p className="text-gray-700">{data.location}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">Type & Severity</h4>
              <p className="text-gray-700">{data.incident_type} - {data.severity}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">Witnesses</h4>
              <p className="text-gray-700">{data.witnesses.length} witness(es)</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">Reported By</h4>
              <p className="text-gray-700">{data.reporter_name} - {data.reporter_role}</p>
            </div>
            <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
              <p className="text-sm text-blue-900">
                <i className="fas fa-info-circle mr-2"></i>
                Click "Generate" to create your incident report
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
        continuous
        showSkipButton
        callback={handleTourCallback}
        styles={{
          options: {
            primaryColor: '#d4af37',
            zIndex: 10000,
          },
        }}
      />
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <div className="text-center mb-8">
          <div className="flex justify-center items-center gap-4 mb-2">
            <h1 className="text-4xl font-bold text-gray-800">Incident Report Wizard</h1>
            <button
              onClick={() => setRunTour(true)}
              className={`help-button px-3 py-2 bg-accent-500 text-white rounded-lg hover:bg-accent-600 transition-all text-sm ${
                showPulse ? 'animate-pulse' : ''
              }`}
              title="Quick tour - Press ESC anytime to exit"
            >
              <i className="fas fa-question-circle mr-2"></i>
              Quick Start
            </button>
          </div>
          <p className="text-gray-600">Comprehensive safety event documentation</p>
        </div>

        {careSetting && <CareSettingContextBanner className="mb-6" />}

        <div className="wizard-container bg-white rounded-lg shadow-lg">
          <div className="wizard-header bg-red-600 text-white p-6 rounded-t-lg">
            <h2 className="text-2xl font-bold">Safety Incident Report</h2>
            <p className="text-red-100 mt-2">Document safety events for quality improvement</p>
          </div>

          <div className="wizard-progress bg-gray-50 p-6">
            <div className="flex justify-between items-center">
              {steps.map((step, index) => (
                <div key={index} className="flex flex-col items-center flex-1">
                  <button
                    onClick={() => setCurrentStep(index)}
                    className={`w-12 h-12 rounded-full flex items-center justify-center transition-all ${
                      index === currentStep
                        ? 'bg-red-600 text-white ring-4 ring-red-200'
                        : index < currentStep
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-200 text-gray-600'
                    }`}
                  >
                    <i className={`fas ${step.icon}`}></i>
                  </button>
                  <span className="text-xs mt-2 font-medium text-gray-600">{step.title}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="wizard-content p-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">{steps[currentStep].title}</h3>
            {renderStepContent()}
          </div>

          <div className="wizard-navigation bg-gray-50 p-4 rounded-b-lg flex justify-between">
            <button
              onClick={previousStep}
              disabled={currentStep === 0}
              className={`px-6 py-2 text-gray-600 bg-gray-200 rounded-lg hover:bg-gray-300 ${
                currentStep === 0 ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              <i className="fas fa-arrow-left mr-2"></i>Previous
            </button>
            <button
              onClick={nextStep}
              disabled={isGenerating}
              className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
            >
              {currentStep === steps.length - 1 ? (
                isGenerating ? (
                  <>
                    <i className="fas fa-spinner fa-spin mr-2"></i>Generating...
                  </>
                ) : (
                  <>
                    <i className="fas fa-file-alt mr-2"></i>Generate Report
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
