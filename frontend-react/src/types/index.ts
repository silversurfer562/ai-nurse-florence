/**
 * Central type exports for AI Nurse Florence React components
 */

export * from './sbar';

// Common types used across all widgets
export interface ApiError {
  detail: string;
  status_code?: number;
}

export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
}

export interface LoadingState {
  isLoading: boolean;
  error: string | null;
}
