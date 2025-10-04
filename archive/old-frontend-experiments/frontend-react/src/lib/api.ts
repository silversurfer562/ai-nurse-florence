/**
 * API Client for AI Nurse Florence
 * Handles all communication with the FastAPI backend
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  SbarStartResponse,
  SbarStepResponse,
  SbarEnhanceRequest,
  SbarEnhanceResponse,
  SbarPriorityRequest,
  SbarPriorityResponse,
  SbarMedicationRequest,
  SbarMedicationResponse,
  SbarData,
} from '@/types';

class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = '/api/v1') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 second timeout
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response) {
          // Server responded with error
          console.error('API Error:', error.response.status, error.response.data);
        } else if (error.request) {
          // Request made but no response
          console.error('Network Error:', error.message);
        } else {
          // Something else happened
          console.error('Request Error:', error.message);
        }
        return Promise.reject(error);
      }
    );
  }

  // ===== SBAR Wizard Endpoints =====

  async startSbarWizard(): Promise<SbarStartResponse> {
    const response = await this.client.post<SbarStartResponse>(
      '/wizard/sbar-report/start'
    );
    return response.data;
  }

  async submitSbarStep(
    wizardId: string,
    stepData: Partial<SbarData>
  ): Promise<SbarStepResponse> {
    const response = await this.client.post<SbarStepResponse>(
      `/wizard/sbar-report/${wizardId}/step`,
      stepData
    );
    return response.data;
  }

  async enhanceSbarText(
    text: string,
    section: string
  ): Promise<SbarEnhanceResponse> {
    const request: SbarEnhanceRequest = { text, section };
    const response = await this.client.post<SbarEnhanceResponse>(
      '/wizard/sbar-report/ai/enhance',
      request
    );
    return response.data;
  }

  async suggestPriority(
    assessmentData: SbarPriorityRequest
  ): Promise<SbarPriorityResponse> {
    const response = await this.client.post<SbarPriorityResponse>(
      '/wizard/sbar-report/ai/suggest-priority',
      assessmentData
    );
    return response.data;
  }

  async checkMedicationInteractions(
    medications: string
  ): Promise<SbarMedicationResponse> {
    const request: SbarMedicationRequest = { medications };
    const response = await this.client.post<SbarMedicationResponse>(
      '/wizard/sbar-report/ai/check-medications',
      request
    );
    return response.data;
  }

  // ===== Health Check =====

  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export class for testing
export default ApiClient;
