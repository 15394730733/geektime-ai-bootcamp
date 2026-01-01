/**
 * API Client Service
 *
 * Centralized API client for communicating with the backend
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';

// API Response types
export interface APIResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: {
    code: string;
    details?: any;
  };
}

// Database types
export interface DatabaseConnection {
  id: string;
  name: string;
  url: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ColumnMetadata {
  name: string;
  data_type: string;
  is_nullable: boolean;
  is_primary_key: boolean;
  default_value?: string;
}

export interface TableMetadata {
  name: string;
  schema: string;
  columns: ColumnMetadata[];
}

export interface DatabaseMetadata {
  database: string;
  tables: TableMetadata[];
  views: TableMetadata[];
}

// Query types
export interface QueryRequest {
  sql: string;
}

export interface QueryResult {
  columns: string[];
  rows: any[][];
  row_count: number;
  execution_time_ms: number;
  truncated: boolean;
}

export interface NaturalLanguageQueryRequest {
  prompt: string;
}

export interface NaturalLanguageQueryResult {
  generated_sql: string;
  columns: string[];
  rows: any[][];
  row_count: number;
  execution_time_ms: number;
  truncated: boolean;
}

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
      timeout: 30000, // 30 seconds timeout
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 400) {
          throw new Error(error.response.data?.message || 'Bad Request');
        }
        if (error.response?.status === 404) {
          throw new Error('Resource not found');
        }
        if (error.response?.status === 500) {
          throw new Error('Internal server error');
        }
        throw new Error(error.message || 'Network error');
      }
    );
  }

  // Database connections
  async getDatabases(): Promise<DatabaseConnection[]> {
    const response = await this.client.get<APIResponse<DatabaseConnection[]>>('/dbs');
    if (!response.data.success) {
      throw new Error(response.data.message);
    }
    return response.data.data || [];
  }

  async createDatabase(data: Omit<DatabaseConnection, 'id' | 'created_at' | 'updated_at'>): Promise<DatabaseConnection> {
    const response = await this.client.post<APIResponse<DatabaseConnection>>('/dbs', data);
    if (!response.data.success) {
      throw new Error(response.data.message);
    }
    return response.data.data!;
  }

  async updateDatabase(name: string, data: Partial<DatabaseConnection>): Promise<DatabaseConnection> {
    const response = await this.client.put<APIResponse<DatabaseConnection>>(`/dbs/${name}`, data);
    if (!response.data.success) {
      throw new Error(response.data.message);
    }
    return response.data.data!;
  }

  async deleteDatabase(name: string): Promise<void> {
    const response = await this.client.delete<APIResponse>(`/dbs/${name}`);
    if (!response.data.success) {
      throw new Error(response.data.message);
    }
  }

  // Database metadata
  async getDatabaseMetadata(name: string): Promise<DatabaseMetadata> {
    const response = await this.client.get<APIResponse<DatabaseMetadata>>(`/dbs/${name}`);
    if (!response.data.success) {
      throw new Error(response.data.message);
    }
    return response.data.data!;
  }

  // Query execution
  async executeQuery(databaseName: string, query: QueryRequest): Promise<QueryResult> {
    const response = await this.client.post<APIResponse<QueryResult>>(
      `/dbs/${databaseName}/query`,
      query
    );
    if (!response.data.success) {
      throw new Error(response.data.message);
    }
    return response.data.data!;
  }

  async executeNaturalLanguageQuery(
    databaseName: string,
    query: NaturalLanguageQueryRequest
  ): Promise<NaturalLanguageQueryResult> {
    const response = await this.client.post<APIResponse<NaturalLanguageQueryResult>>(
      `/dbs/${databaseName}/query/natural`,
      query
    );
    if (!response.data.success) {
      throw new Error(response.data.message);
    }
    return response.data.data!;
  }

  // Health check
  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new APIClient();

// Export types
export type { APIClient };
