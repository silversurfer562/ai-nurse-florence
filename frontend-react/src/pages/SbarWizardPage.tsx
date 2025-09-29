import { useMutation } from '@tanstack/react-query'
import { ArrowLeft, ArrowRight, CheckCircle, FileText } from 'lucide-react'
import { useState } from 'react'

interface WizardStep {
  id: string
  title: string
  description: string
  icon: React.ComponentType<any>
}

const steps: WizardStep[] = [
  {
    id: 'situation',
    title: 'Situation',
    description: 'Describe the current patient situation clearly and concisely',
    icon: FileText,
  },
  {
    id: 'background',
    title: 'Background',
    description: 'Provide relevant medical history and context',
    icon: FileText,
  },
  {
    id: 'assessment',
    title: 'Assessment',
    description: 'Your professional nursing assessment of the situation',
    icon: FileText,
  },
  {
    id: 'recommendation',
    title: 'Recommendation',
    description: 'What specific actions do you recommend?',
    icon: FileText,
  },
]

interface SbarData {
  situation: {
    patientId: string
    currentSituation: string
  }
  background: {
    medicalHistory: string
    recentEvents: string
  }
  assessment: {
    clinicalAssessment: string
    concerns: string
  }
  recommendation: {
    recommendations: string
    urgency: string
  }
}

export function SbarWizardPage() {
  const [currentStep, setCurrentStep] = useState(0)
  const [wizardId, setWizardId] = useState<string | null>(null)
  const [sbarData, setSbarData] = useState<Partial<SbarData>>({})
  const [isComplete, setIsComplete] = useState(false)
  const [generatedReport, setGeneratedReport] = useState<string>('')

  // Start wizard mutation
  const startWizardMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/v1/wizards/sbar-report/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
      if (!response.ok) throw new Error('Failed to start wizard')
      return response.json()
    },
    onSuccess: (data) => {
      if (data.success) {
        setWizardId(data.data.wizard_id)
      }
    },
  })

  // Submit step mutation
  const submitStepMutation = useMutation({
    mutationFn: async ({ stepData }: { stepData: any }) => {
      const stepName = steps[currentStep].id
      const response = await fetch(`/api/v1/wizards/sbar-report/${stepName}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          wizard_id: wizardId,
          ...stepData,
        }),
      })
      if (!response.ok) throw new Error('Failed to submit step')
      return response.json()
    },
    onSuccess: (data) => {
      if (data.success && currentStep < steps.length - 1) {
        setCurrentStep(currentStep + 1)
      } else if (currentStep === steps.length - 1) {
        generateReport()
      }
    },
  })

  // Generate report mutation
  const generateReportMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/v1/wizards/sbar-report/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ wizard_id: wizardId }),
      })
      if (!response.ok) throw new Error('Failed to generate report')
      return response.json()
    },
    onSuccess: (data) => {
      if (data.success) {
        setGeneratedReport(data.data.sbar_report)
        setIsComplete(true)
      }
    },
  })

  const generateReport = () => {
    generateReportMutation.mutate()
  }

  const handleNext = () => {
    const stepName = steps[currentStep].id
    const stepData = getStepData(stepName)

    if (!wizardId) {
      startWizardMutation.mutate()
      return
    }

    submitStepMutation.mutate({ stepData })
  }

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const getStepData = (stepName: string) => {
    switch (stepName) {
      case 'situation':
        return sbarData.situation || {}
      case 'background':
        return sbarData.background || {}
      case 'assessment':
        return sbarData.assessment || {}
      case 'recommendation':
        return sbarData.recommendation || {}
      default:
        return {}
    }
  }

  const updateStepData = (stepName: string, data: any) => {
    setSbarData(prev => ({
      ...prev,
      [stepName]: { ...prev[stepName as keyof SbarData], ...data }
    }))
  }

  if (isComplete) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-gray-900 mb-2">SBAR Report Generated</h1>
          <p className="text-gray-600">Your structured clinical communication is ready</p>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="text-lg font-semibold mb-4">Generated SBAR Report</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <pre className="whitespace-pre-wrap text-sm font-mono">{generatedReport}</pre>
          </div>

          <div className="mt-6 flex gap-4">
            <button className="btn-clinical-primary">
              Copy to Clipboard
            </button>
            <button className="btn-clinical-secondary">
              Download PDF
            </button>
            <button
              onClick={() => window.location.reload()}
              className="btn-clinical-secondary"
            >
              Create New Report
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">SBAR Report Generator</h1>
        <p className="text-gray-600">Create structured clinical communication for effective handoffs</p>
      </div>

      {/* Progress */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className={`flex items-center ${index < steps.length - 1 ? 'flex-1' : ''}`}
            >
              <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                index <= currentStep
                  ? 'bg-clinical-600 border-clinical-600 text-white'
                  : 'border-gray-300 text-gray-400'
              }`}>
                {index + 1}
              </div>
              <div className="ml-3">
                <p className={`text-sm font-medium ${
                  index <= currentStep ? 'text-clinical-600' : 'text-gray-400'
                }`}>
                  {step.title}
                </p>
              </div>
              {index < steps.length - 1 && (
                <div className={`flex-1 h-0.5 mx-4 ${
                  index < currentStep ? 'bg-clinical-600' : 'bg-gray-300'
                }`} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Current Step Content */}
      <div className="bg-white rounded-xl border border-gray-200 p-8 mb-8">
        <div className="mb-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">
            {steps[currentStep].title}
          </h2>
          <p className="text-gray-600">
            {steps[currentStep].description}
          </p>
        </div>

        {/* Step-specific forms would go here */}
        <div className="space-y-6">
          {currentStep === 0 && <SituationStep data={sbarData.situation} onChange={(data) => updateStepData('situation', data)} />}
          {currentStep === 1 && <BackgroundStep data={sbarData.background} onChange={(data) => updateStepData('background', data)} />}
          {currentStep === 2 && <AssessmentStep data={sbarData.assessment} onChange={(data) => updateStepData('assessment', data)} />}
          {currentStep === 3 && <RecommendationStep data={sbarData.recommendation} onChange={(data) => updateStepData('recommendation', data)} />}
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between">
        <button
          onClick={handlePrevious}
          disabled={currentStep === 0}
          className="btn-clinical-secondary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Previous
        </button>

        <button
          onClick={handleNext}
          disabled={submitStepMutation.isPending || startWizardMutation.isPending}
          className="btn-clinical-primary"
        >
          {currentStep === steps.length - 1 ? 'Generate Report' : 'Next'}
          <ArrowRight className="w-4 h-4 ml-2" />
        </button>
      </div>
    </div>
  )
}

// Step Components
function SituationStep({ data, onChange }: { data?: any, onChange: (data: any) => void }) {
  return (
    <div className="space-y-4">
      <div>
        <label className="form-label-clinical">Patient Identifier</label>
        <input
          type="text"
          className="form-input-clinical"
          placeholder="Room 302A, Initial J.D."
          value={data?.patientId || ''}
          onChange={(e) => onChange({ patientId: e.target.value })}
        />
      </div>
      <div>
        <label className="form-label-clinical">Current Situation</label>
        <textarea
          className="form-input-clinical"
          rows={4}
          placeholder="Patient presenting with... Current vital signs... Immediate concerns..."
          value={data?.currentSituation || ''}
          onChange={(e) => onChange({ currentSituation: e.target.value })}
        />
      </div>
    </div>
  )
}

function BackgroundStep({ data, onChange }: { data?: any, onChange: (data: any) => void }) {
  return (
    <div className="space-y-4">
      <div>
        <label className="form-label-clinical">Relevant Medical History</label>
        <textarea
          className="form-input-clinical"
          rows={3}
          placeholder="Pertinent diagnoses, allergies, medications..."
          value={data?.medicalHistory || ''}
          onChange={(e) => onChange({ medicalHistory: e.target.value })}
        />
      </div>
      <div>
        <label className="form-label-clinical">Recent Events</label>
        <textarea
          className="form-input-clinical"
          rows={3}
          placeholder="Recent procedures, treatments, changes in condition..."
          value={data?.recentEvents || ''}
          onChange={(e) => onChange({ recentEvents: e.target.value })}
        />
      </div>
    </div>
  )
}

function AssessmentStep({ data, onChange }: { data?: any, onChange: (data: any) => void }) {
  return (
    <div className="space-y-4">
      <div>
        <label className="form-label-clinical">Clinical Assessment</label>
        <textarea
          className="form-input-clinical"
          rows={4}
          placeholder="Your professional assessment of the patient's condition..."
          value={data?.clinicalAssessment || ''}
          onChange={(e) => onChange({ clinicalAssessment: e.target.value })}
        />
      </div>
      <div>
        <label className="form-label-clinical">Specific Concerns</label>
        <textarea
          className="form-input-clinical"
          rows={3}
          placeholder="What are you most concerned about? What has changed?"
          value={data?.concerns || ''}
          onChange={(e) => onChange({ concerns: e.target.value })}
        />
      </div>
    </div>
  )
}

function RecommendationStep({ data, onChange }: { data?: any, onChange: (data: any) => void }) {
  return (
    <div className="space-y-4">
      <div>
        <label className="form-label-clinical">Recommendations</label>
        <textarea
          className="form-input-clinical"
          rows={4}
          placeholder="Specific actions you recommend..."
          value={data?.recommendations || ''}
          onChange={(e) => onChange({ recommendations: e.target.value })}
        />
      </div>
      <div>
        <label className="form-label-clinical">Urgency Level</label>
        <select
          className="form-input-clinical"
          value={data?.urgency || 'routine'}
          onChange={(e) => onChange({ urgency: e.target.value })}
        >
          <option value="routine">Routine - Within normal timeframe</option>
          <option value="soon">Soon - Within next hour</option>
          <option value="urgent">Urgent - Within 30 minutes</option>
          <option value="immediate">Immediate - Right now</option>
        </select>
      </div>
    </div>
  )
}
