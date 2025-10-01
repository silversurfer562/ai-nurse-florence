/**
 * TypeScript type definitions for SBAR Wizard
 * AI Nurse Florence - Professional clinical documentation
 */

export interface SbarData {
  situation: string;
  background: string;
  assessment: string;
  recommendation: string;
}

export interface SbarStep {
  id: number;
  title: string;
  section: keyof SbarData;
  prompt: string;
  placeholder: string;
  helpText: string;
  required: boolean;
}

export interface SbarWizardSession {
  wizard_id: string;
  created_at: string;
  current_step: number;
  total_steps: number;
  completed: boolean;
  sbar_data: Partial<SbarData>;
  sections: string[];
}

export interface SbarStartResponse {
  wizard_id: string;
  current_step: number;
  section: string;
  prompt: string;
}

export interface SbarStepResponse {
  wizard_id: string;
  current_step?: number;
  section?: string;
  prompt?: string;
  completed?: boolean;
  sbar_report?: SbarData;
}

export interface SbarEnhanceRequest {
  text: string;
  section: string;
}

export interface SbarEnhanceResponse {
  original: string;
  enhanced: string;
  section: string;
  error?: string;
}

export interface SbarPriorityRequest {
  vital_signs?: string;
  physical_assessment?: string;
  mental_status?: string;
  clinical_concerns?: string;
}

export interface SbarPriorityResponse {
  suggested_priority: 'stat' | 'urgent' | 'routine';
  reasoning: string;
  error?: string;
}

export interface SbarMedicationRequest {
  medications: string;
}

export interface DrugInteraction {
  drug1: string;
  drug2: string;
  severity: 'major' | 'moderate' | 'minor';
  description: string;
  recommendation?: string;
}

export interface SbarMedicationResponse {
  has_interactions: boolean;
  medications_found: string[];
  total_interactions: number;
  has_major_interactions: boolean;
  interactions: DrugInteraction[];
  full_report_available: boolean;
  error?: string;
  error_detail?: string;
}

export type Priority = 'stat' | 'urgent' | 'routine';

export interface SbarFormErrors {
  situation?: string;
  background?: string;
  assessment?: string;
  recommendation?: string;
}

export interface SbarWizardState {
  // Session info
  wizardId: string | null;
  currentStep: number;
  isLoading: boolean;
  error: string | null;

  // Form data
  formData: Partial<SbarData>;
  formErrors: SbarFormErrors;

  // AI features
  isEnhancing: boolean;
  enhancementResult: string | null;

  isPriorityChecking: boolean;
  suggestedPriority: Priority | null;
  priorityReasoning: string | null;

  isMedicationChecking: boolean;
  medicationResults: SbarMedicationResponse | null;

  // Wizard completion
  isCompleted: boolean;
  finalReport: SbarData | null;
}
