import axios from 'axios';

// Use Vite proxy in development, full URL in production
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API Service Functions
export const clinicalTrialsService = {
  search: async (condition: string, maxStudies: number = 10, status?: string) => {
    const params: any = { condition, max_studies: maxStudies };
    if (status) {
      params.status = status;
    }
    const response = await api.get('/api/v1/clinical-trials/search', { params });
    return response.data;
  },
};

export const diseaseService = {
  lookup: async (query: string) => {
    const response = await api.get('/api/v1/disease/lookup', {
      params: { q: query },
    });
    return response.data;
  },
};

export const literatureService = {
  search: async (query: string, maxResults: number = 10) => {
    const response = await api.get('/api/v1/literature/search', {
      params: { q: query, max_results: maxResults },
    });
    return response.data;
  },
};

export const healthService = {
  checkHealth: async () => {
    const response = await api.get('/api/v1/health/');
    return response.data;
  },
};

export const drugInteractionService = {
  check: async (drugs: string[]) => {
    const response = await api.post('/api/v1/drug-interactions/check', {
      drugs: drugs,
    });
    return response.data;
  },
};