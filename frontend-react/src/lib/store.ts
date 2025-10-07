import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from './api';
import type { SbarData } from '../types/sbar';

interface SbarWizardState {
  wizardId: string | null;
  currentStep: number;
  formData: SbarData;
  formErrors: Partial<Record<keyof SbarData, string>>;
  isLoading: boolean;
  error: string | null;
  isEnhancing: boolean;
  enhancementResult: string | null;
  isPriorityChecking: boolean;
  suggestedPriority: string | null;
  priorityReasoning: string | null;
  isMedicationChecking: boolean;
  medicationResults: any | null;
  isCompleted: boolean;
  finalReport: SbarData | null;

  // Actions
  startWizard: () => Promise<void>;
  nextStep: () => void;
  previousStep: () => void;
  updateFormData: (section: keyof SbarData, value: string) => void;
  enhanceText: (section: keyof SbarData) => Promise<void>;
  checkPriority: () => Promise<void>;
  checkMedications: () => Promise<void>;
  reset: () => void;
}

const initialState = {
  wizardId: null,
  currentStep: 1,
  formData: {
    situation: '',
    background: '',
    assessment: '',
    recommendation: '',
  },
  formErrors: {},
  isLoading: false,
  error: null,
  isEnhancing: false,
  enhancementResult: null,
  isPriorityChecking: false,
  suggestedPriority: null,
  priorityReasoning: null,
  isMedicationChecking: false,
  medicationResults: null,
  isCompleted: false,
  finalReport: null,
};

export const useSbarWizardStore = create<SbarWizardState>()(
  persist(
    (set, get) => ({
      ...initialState,

      startWizard: async () => {
        try {
          const response = await api.post('/api/v1/wizards/sbar/start');
          set({
            wizardId: response.data.data.wizard_session.wizard_id,
            currentStep: 1,
            error: null,
          });
        } catch (error: any) {
          set({ error: error.message || 'Failed to start wizard' });
        }
      },

      // NO VALIDATION - users can freely navigate forward
      nextStep: () => {
        const { currentStep, formData } = get();

        if (currentStep < 4) {
          set({ currentStep: currentStep + 1, formErrors: {} });
        } else {
          // Complete wizard
          set({
            isCompleted: true,
            finalReport: formData,
          });
        }
      },

      previousStep: () => {
        const { currentStep } = get();
        if (currentStep > 1) {
          set({ currentStep: currentStep - 1, formErrors: {} });
        }
      },

      updateFormData: (section, value) => {
        set((state) => ({
          formData: {
            ...state.formData,
            [section]: value,
          },
        }));
      },

      enhanceText: async (section) => {
        const { formData } = get();
        const text = formData[section];

        if (!text) return;

        set({ isEnhancing: true, error: null });

        try {
          const response = await api.post('/api/v1/ai/enhance-clinical-text', {
            text,
            context: `SBAR ${section}`,
          });

          set({
            enhancementResult: response.data.enhanced_text || response.data.data?.enhanced_text,
            isEnhancing: false,
          });
        } catch (error: any) {
          set({
            error: error.message || 'Failed to enhance text',
            isEnhancing: false,
          });
        }
      },

      checkPriority: async () => {
        const { formData } = get();

        set({ isPriorityChecking: true, error: null });

        try {
          const response = await api.post('/api/v1/ai/suggest-priority', {
            situation: formData.situation,
            assessment: formData.assessment,
          });

          set({
            suggestedPriority: response.data.priority || response.data.data?.priority,
            priorityReasoning: response.data.reasoning || response.data.data?.reasoning,
            isPriorityChecking: false,
          });
        } catch (error: any) {
          set({
            error: error.message || 'Failed to check priority',
            isPriorityChecking: false,
          });
        }
      },

      checkMedications: async () => {
        const { formData } = get();

        set({ isMedicationChecking: true, error: null });

        try {
          const response = await api.post('/api/v1/medications/check-interactions', {
            text: formData.background,
          });

          set({
            medicationResults: response.data.data || response.data,
            isMedicationChecking: false,
          });
        } catch (error: any) {
          set({
            error: error.message || 'Failed to check medications',
            isMedicationChecking: false,
          });
        }
      },

      reset: () => {
        set({ ...initialState });
      },
    }),
    {
      name: 'sbar-wizard-storage',
    }
  )
);
