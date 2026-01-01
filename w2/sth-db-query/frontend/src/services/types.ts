/**
 * Common TypeScript types for the application
 */

// Utility types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

// API related types
export interface PaginationParams {
  page?: number;
  size?: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  size: number;
  totalPages: number;
}

// Form types
export interface FormFieldError {
  field: string;
  message: string;
}

export interface ValidationErrors {
  [field: string]: string[];
}

// Loading states
export interface LoadingState {
  isLoading: boolean;
  error?: string | null;
}

// Component props
export interface BaseComponentProps {
  className?: string;
  style?: React.CSSProperties;
  'data-testid'?: string;
}

// Database specific types
export type DatabaseType = 'postgresql' | 'mysql' | 'sqlite' | 'oracle' | 'sqlserver';

export interface ConnectionTestResult {
  success: boolean;
  message: string;
  latency?: number;
}

// Query execution types
export interface QueryExecutionContext {
  databaseName: string;
  connectionId: string;
  timeout?: number;
}

export interface QueryExecutionResult {
  success: boolean;
  data?: any;
  error?: string;
  executionTime: number;
  rowCount?: number;
}

// LLM types
export interface LLMConfig {
  apiKey: string;
  baseUrl: string;
  model: string;
  temperature?: number;
  maxTokens?: number;
}

export interface NaturalLanguageProcessingResult {
  sql: string;
  confidence: number;
  explanation?: string;
}

// UI state types
export interface UIState {
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark';
  language: string;
}

// Export commonly used types
export type { DatabaseConnection, DatabaseMetadata, QueryResult } from './api';
