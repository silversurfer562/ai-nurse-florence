/**
 * Zustand State Management for SBAR Wizard
 * Clean, type-safe global state for React components
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  SbarData,
  SbarFormErrors,
  Priority,
  SbarMedicationResponse,
  SbarWizardState,
} from '@/types';
import { apiClient } from './api';

interface SbarWizardStore extends SbarWizardState {
  // Actions
  startWizard: () => Promise<void>;
  nextStep: () => Promise<void>;
  previousStep: () => void;
  updateFormData: (field: keyof SbarData, value: string) => void;
  validateCurrentStep: () => boolean;
  enhanceText: (field: keyof SbarData) => Promise<void>;
  checkPriority: () => Promise<void>;
  checkMedications: () => Promise<void>;
  saveDraft: () => void;
  loadDraft: () => void;
  reset: () => void;
}

const initialState: SbarWizardState = {
  wizardId: null,
  currentStep: 1,
  isLoading: false,
  error: null,
  formData: {},
  formErrors: {},
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

export const useSbarWizardStore = create<SbarWizardStore>(
  persist(
    (set, get) => ({
        ...initialState,

        startWizard: async () => {
          set({ isLoading: true, error: null });
          try {
            const response = await apiClient.startSbarWizard();
            set({
              wizardId: response.wizard_id,
              currentStep: response.current_step,
              isLoading: false,
            });
          } catch (error) {
            set({
              error: 'Failed to start wizard. Please try again.',
              isLoading: false,
            });
          }
        },

        nextStep: async () => {
          const { wizardId, currentStep, formData, validateCurrentStep } = get();

          if (!validateCurrentStep()) {
            return;
          }

          if (!wizardId) {
            set({ error: 'No active wizard session' });
            return;
          }

          set({ isLoading: true, error: null });

          try {
            const response = await apiClient.submitSbarStep(wizardId, formData);

            if (response.completed) {
              set({
                isCompleted: true,
                finalReport: response.sbar_report || null,
                isLoading: false,
              });
            } else {
              set({
                currentStep: response.current_step || currentStep + 1,
                isLoading: false,
              });
            }
          } catch (error) {
            set({
              error: 'Failed to submit step. Please try again.',
              isLoading: false,
            });
          }
        },

        previousStep: () => {
          const { currentStep } = get();
          if (currentStep > 1) {
            set({ currentStep: currentStep - 1, error: null });
          }
        },

        updateFormData: (field, value) => {
          set((state) => ({
            formData: {
              ...state.formData,
              [field]: value,
            },
            formErrors: {
              ...state.formErrors,
              [field]: undefined,
            },
          }));
        },

        validateCurrentStep: () => {
          const { currentStep, formData } = get();
          const fields: (keyof SbarData)[] = [
            'situation',
            'background',
            'assessment',
            'recommendation',
          ];
          const currentField = fields[currentStep - 1];
          const value = formData[currentField];

          if (!value || value.trim().length === 0) {
            set((state) => ({
              formErrors: {
                ...state.formErrors,
                [currentField]: 'This field is required',
              },
            }));
            return false;
          }

          if (value.trim().length < 10) {
            set((state) => ({
              formErrors: {
                ...state.formErrors,
                [currentField]: 'Please provide more detail (at least 10 characters)',
              },
            }));
            return false;
          }

          return true;
        },

        enhanceText: async (field) => {
          const { formData } = get();
          const text = formData[field];

          if (!text || text.trim().length === 0) {
            set({ error: 'Please enter some text first' });
            return;
          }

          set({ isEnhancing: true, error: null, enhancementResult: null });

          try {
            const response = await apiClient.enhanceSbarText(text, field);
            set({
              enhancementResult: response.enhanced,
              isEnhancing: false,
            });
          } catch (error) {
            set({
              error: 'AI enhancement temporarily unavailable',
              isEnhancing: false,
            });
          }
        },

        checkPriority: async () => {
          const { formData } = get();

          set({ isPriorityChecking: true, error: null });

          try {
            const response = await apiClient.suggestPriority({
              vital_signs: formData.assessment || '',
              clinical_concerns: formData.assessment || '',
            });

            set({
              suggestedPriority: response.suggested_priority,
              priorityReasoning: response.reasoning,
              isPriorityChecking: false,
            });
          } catch (error) {
            set({
              error: 'Priority suggestion temporarily unavailable',
              isPriorityChecking: false,
            });
          }
        },

        checkMedications: async () => {
          const { formData } = get();
          const medications = formData.background || '';

          if (!medications || medications.trim().length < 3) {
            set({ error: 'Please enter medication information first' });
            return;
          }

          set({ isMedicationChecking: true, error: null });

          try {
            const response = await apiClient.checkMedicationInteractions(medications);
            set({
              medicationResults: response,
              isMedicationChecking: false,
            });
          } catch (error) {
            set({
              error: 'Medication check temporarily unavailable',
              isMedicationChecking: false,
            });
          }
        },

        saveDraft: () => {
          // Persist middleware automatically saves to localStorage
          console.log('Draft saved automatically');
        },

        loadDraft: () => {
          // Persist middleware automatically loads from localStorage
          console.log('Draft loaded automatically');
        },

        reset: () => {
          set(initialState);
        },
      }),
      {
        name: 'sbar-wizard-storage',
        partialize: (state) => ({
          formData: state.formData,
          currentStep: state.currentStep,
          wizardId: state.wizardId,
        }),
      }
    )
);
