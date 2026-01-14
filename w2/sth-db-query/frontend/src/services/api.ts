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
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
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
  rows: any[][] | Record<string, any>[];
  rowCount: number;
  executionTimeMs: number;
  truncated?: boolean;
}

export interface NaturalLanguageQueryRequest {
  prompt: string;
}

export interface NaturalLanguageQueryResult {
  generatedSql: string;
  columns?: string[];
  rows?: any[][];
  rowCount?: number;
  executionTimeMs?: number;
  truncated?: boolean;
}

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || '/api/v1',
      timeout: 30000, // 30 seconds timeout
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        // Extract structured error information if available
        if (error.response?.data) {
          const errorData = error.response.data;
          
          // If the response contains structured error information
          if (errorData.error && typeof errorData.error === 'object') {
            // Create a structured error with the backend error information
            const structuredError = new Error(errorData.message || errorData.error.userMessage || 'Request failed');
            (structuredError as any).errorInfo = errorData.error;
            (structuredError as any).statusCode = error.response.status;
            throw structuredError;
          }
          
          // If it's a simple error message
          if (errorData.message) {
            throw new Error(errorData.message);
          }
        }

        // Handle HTTP status codes
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
    const response = await this.client.get<any>('/dbs/');

    // Handle both wrapped and direct array responses
    let result: DatabaseConnection[] = [];
    if (Array.isArray(response.data)) {
      // Direct array response
      result = response.data;
    } else if (response.data && typeof response.data === 'object' && 'data' in response.data) {
      // Wrapped response
      if (!response.data.success) {
        throw new Error(response.data.message);
      }
      result = response.data.data || [];
    } else {
      throw new Error('Unexpected response format');
    }

    return result;
  }

  async createDatabase(data: Omit<DatabaseConnection, 'id' | 'createdAt' | 'updatedAt'>): Promise<DatabaseConnection> {
    const response = await this.client.put<APIResponse<DatabaseConnection>>(`/dbs/${data.name}`, data);
    if (!response.data.success) {
      throw new Error(response.data.message);
    }
    return response.data.data!;
  }

  async updateDatabase(name: string, data: Partial<DatabaseConnection>): Promise<DatabaseConnection> {
    // Use new name if provided, otherwise use old name
    const targetName = data.name || name;
    const response = await this.client.put<APIResponse<DatabaseConnection>>(`/dbs/${targetName}`, data);
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

  // Refresh database metadata
  async refreshDatabaseMetadata(name: string): Promise<DatabaseMetadata> {
    const response = await this.client.post<APIResponse<DatabaseMetadata>>(`/dbs/${name}/refresh`);
    if (!response.data.success) {
      throw new Error(response.data.message);
    }
    return response.data.data!;
  }

  // Query execution
  async executeQuery(databaseName: string, query: QueryRequest): Promise<QueryResult> {
    console.log('=== API.executeQuery called ===');
    console.log('Database name:', databaseName);
    console.log('Query:', query.sql);
    
    const url = `/dbs/${databaseName}/query`;
    console.log('Full URL:', url);
    
    const response = await this.client.post<APIResponse<QueryResult>>(
      url,
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

  // Test database connection
  async testDatabaseConnection(data: Omit<DatabaseConnection, 'id' | 'createdAt' | 'updatedAt' | 'isActive'>): Promise<{ success: boolean; message: string; latency_ms?: number }> {
    // Set a timeout for the test connection request (5 seconds)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);
    
    try {
      const response = await this.client.post<APIResponse<{ success: boolean; message: string; latency_ms?: number }>>(
        '/dbs/test-connection', 
        data,
        { signal: controller.signal }
      );
      clearTimeout(timeoutId);
      
      if (!response.data.success) {
        throw new Error(response.data.message);
      }
      return response.data.data!;
    } catch (error: any) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        throw new Error('Connection test timed out after 5 seconds');
      }
      throw error;
    }
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
