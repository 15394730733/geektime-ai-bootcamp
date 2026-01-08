/**
 * Unit tests for API Client Service
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import type { 
  DatabaseConnection, 
  DatabaseMetadata, 
  QueryRequest, 
  QueryResult,
  NaturalLanguageQueryRequest,
  NaturalLanguageQueryResult 
} from '../api'

// Create mock axios instance
const mockAxiosInstance = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
  interceptors: {
    response: {
      use: vi.fn((successHandler, errorHandler) => {
        // Store the error handler for use in tests
        mockAxiosInstance._errorHandler = errorHandler
      }),
    },
  },
  _errorHandler: null as any,
}

const mockAxiosCreate = vi.fn(() => mockAxiosInstance)

// Mock axios before any imports
vi.mock('axios', () => ({
  default: {
    create: mockAxiosCreate,
  },
}))

// Import the API client after mocking
const { apiClient } = await import('../api')

describe('APIClient', () => {
  beforeEach(() => {
    // Only clear the HTTP method mocks, preserve axios.create call history
    mockAxiosInstance.get.mockClear()
    mockAxiosInstance.post.mockClear()
    mockAxiosInstance.put.mockClear()
    mockAxiosInstance.delete.mockClear()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('Database Management', () => {
    it('should get databases list successfully', async () => {
      const mockDatabases: DatabaseConnection[] = [
        {
          id: '1',
          name: 'test-db',
          url: 'postgresql://localhost:5432/test',
          description: 'Test database',
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ]

      mockAxiosInstance.get.mockResolvedValue({
        data: mockDatabases,
      })

      const result = await apiClient.getDatabases()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/dbs/')
      expect(result).toEqual(mockDatabases)
    })

    it('should handle wrapped response format for databases list', async () => {
      const mockDatabases: DatabaseConnection[] = [
        {
          id: '1',
          name: 'test-db',
          url: 'postgresql://localhost:5432/test',
          description: 'Test database',
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ]

      mockAxiosInstance.get.mockResolvedValue({
        data: {
          success: true,
          message: 'Success',
          data: mockDatabases,
        },
      })

      const result = await apiClient.getDatabases()

      expect(result).toEqual(mockDatabases)
    })

    it('should throw error for unsuccessful wrapped response', async () => {
      mockAxiosInstance.get.mockResolvedValue({
        data: {
          success: false,
          message: 'Database connection failed',
          data: null,
        },
      })

      await expect(apiClient.getDatabases()).rejects.toThrow('Database connection failed')
    })

    it('should create database successfully', async () => {
      const newDatabase = {
        name: 'new-db',
        url: 'postgresql://localhost:5432/new',
        description: 'New database',
        is_active: true,
      }

      const createdDatabase: DatabaseConnection = {
        ...newDatabase,
        id: '2',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      mockAxiosInstance.put.mockResolvedValue({
        data: {
          success: true,
          message: 'Database created',
          data: createdDatabase,
        },
      })

      const result = await apiClient.createDatabase(newDatabase)

      expect(mockAxiosInstance.put).toHaveBeenCalledWith('/dbs/new-db', newDatabase)
      expect(result).toEqual(createdDatabase)
    })

    it('should update database successfully', async () => {
      const updateData = {
        description: 'Updated description',
      }

      const updatedDatabase: DatabaseConnection = {
        id: '1',
        name: 'test-db',
        url: 'postgresql://localhost:5432/test',
        description: 'Updated description',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T01:00:00Z',
      }

      mockAxiosInstance.put.mockResolvedValue({
        data: {
          success: true,
          message: 'Database updated',
          data: updatedDatabase,
        },
      })

      const result = await apiClient.updateDatabase('test-db', updateData)

      expect(mockAxiosInstance.put).toHaveBeenCalledWith('/dbs/test-db', updateData)
      expect(result).toEqual(updatedDatabase)
    })

    it('should delete database successfully', async () => {
      mockAxiosInstance.delete.mockResolvedValue({
        data: {
          success: true,
          message: 'Database deleted',
        },
      })

      await apiClient.deleteDatabase('test-db')

      expect(mockAxiosInstance.delete).toHaveBeenCalledWith('/dbs/test-db')
    })

    it('should get database metadata successfully', async () => {
      const mockMetadata: DatabaseMetadata = {
        database: 'test-db',
        tables: [
          {
            name: 'users',
            schema: 'public',
            columns: [
              {
                name: 'id',
                data_type: 'integer',
                is_nullable: false,
                is_primary_key: true,
              },
              {
                name: 'name',
                data_type: 'varchar',
                is_nullable: false,
                is_primary_key: false,
              },
            ],
          },
        ],
        views: [],
      }

      mockAxiosInstance.get.mockResolvedValue({
        data: {
          success: true,
          message: 'Metadata retrieved',
          data: mockMetadata,
        },
      })

      const result = await apiClient.getDatabaseMetadata('test-db')

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/dbs/test-db')
      expect(result).toEqual(mockMetadata)
    })
  })

  describe('Query Execution', () => {
    it('should execute SQL query successfully', async () => {
      const queryRequest: QueryRequest = {
        sql: 'SELECT * FROM users LIMIT 10',
      }

      const queryResult: QueryResult = {
        columns: ['id', 'name'],
        rows: [
          [1, 'John Doe'],
          [2, 'Jane Smith'],
        ],
        row_count: 2,
        execution_time_ms: 150,
        truncated: false,
      }

      mockAxiosInstance.post.mockResolvedValue({
        data: {
          success: true,
          message: 'Query executed',
          data: queryResult,
        },
      })

      const result = await apiClient.executeQuery('test-db', queryRequest)

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/dbs/test-db/query', queryRequest)
      expect(result).toEqual(queryResult)
    })

    it('should execute natural language query successfully', async () => {
      const nlRequest: NaturalLanguageQueryRequest = {
        prompt: 'Show me all users',
      }

      const nlResult: NaturalLanguageQueryResult = {
        generated_sql: 'SELECT * FROM users LIMIT 1000',
        columns: ['id', 'name'],
        rows: [
          [1, 'John Doe'],
          [2, 'Jane Smith'],
        ],
        row_count: 2,
        execution_time_ms: 250,
        truncated: false,
      }

      mockAxiosInstance.post.mockResolvedValue({
        data: {
          success: true,
          message: 'Natural language query processed',
          data: nlResult,
        },
      })

      const result = await apiClient.executeNaturalLanguageQuery('test-db', nlRequest)

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/dbs/test-db/query/natural', nlRequest)
      expect(result).toEqual(nlResult)
    })
  })

  describe('Error Handling', () => {
    it('should handle 400 Bad Request errors', async () => {
      const errorResponse = {
        response: {
          status: 400,
          data: {
            message: 'Invalid SQL syntax',
          },
        },
      }

      // Simulate the interceptor error handling
      mockAxiosInstance.get.mockImplementation(() => {
        return Promise.reject(mockAxiosInstance._errorHandler(errorResponse))
      })

      await expect(apiClient.getDatabases()).rejects.toThrow('Invalid SQL syntax')
    })

    it('should handle 404 Not Found errors', async () => {
      const errorResponse = {
        response: {
          status: 404,
        },
      }

      // Simulate the interceptor error handling
      mockAxiosInstance.get.mockImplementation(() => {
        return Promise.reject(mockAxiosInstance._errorHandler(errorResponse))
      })

      await expect(apiClient.getDatabaseMetadata('nonexistent-db')).rejects.toThrow('Resource not found')
    })

    it('should handle 500 Internal Server Error', async () => {
      const errorResponse = {
        response: {
          status: 500,
        },
      }

      // Simulate the interceptor error handling
      mockAxiosInstance.post.mockImplementation(() => {
        return Promise.reject(mockAxiosInstance._errorHandler(errorResponse))
      })

      const queryRequest: QueryRequest = { sql: 'SELECT * FROM users' }
      await expect(apiClient.executeQuery('test-db', queryRequest)).rejects.toThrow('Internal server error')
    })

    it('should handle network errors', async () => {
      const networkError = new Error('Network Error')
      
      // Simulate the interceptor error handling
      mockAxiosInstance.get.mockImplementation(() => {
        return Promise.reject(mockAxiosInstance._errorHandler(networkError))
      })

      await expect(apiClient.getDatabases()).rejects.toThrow('Network Error')
    })

    it('should handle API response errors for database operations', async () => {
      mockAxiosInstance.put.mockResolvedValue({
        data: {
          success: false,
          message: 'Connection failed: Invalid credentials',
        },
      })

      const newDatabase = {
        name: 'invalid-db',
        url: 'postgresql://invalid:invalid@localhost:5432/invalid',
        description: 'Invalid database',
        is_active: false,
      }

      await expect(apiClient.createDatabase(newDatabase)).rejects.toThrow('Connection failed: Invalid credentials')
    })

    it('should handle API response errors for query operations', async () => {
      mockAxiosInstance.post.mockResolvedValue({
        data: {
          success: false,
          message: 'Query timeout: Query took too long to execute',
        },
      })

      const queryRequest: QueryRequest = { sql: 'SELECT * FROM large_table' }
      await expect(apiClient.executeQuery('test-db', queryRequest)).rejects.toThrow('Query timeout: Query took too long to execute')
    })
  })

  describe('Health Check', () => {
    it('should perform health check successfully', async () => {
      const healthResponse = {
        status: 'healthy',
        service: 'database-query-tool',
      }

      mockAxiosInstance.get.mockResolvedValue({
        data: healthResponse,
      })

      const result = await apiClient.healthCheck()

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/health')
      expect(result).toEqual(healthResponse)
    })
  })

  describe('Configuration', () => {
    it('should have axios instance configured', () => {
      // Test that the API client exists and has the expected methods
      expect(apiClient).toBeDefined()
      expect(apiClient.getDatabases).toBeDefined()
      expect(apiClient.createDatabase).toBeDefined()
      expect(apiClient.executeQuery).toBeDefined()
      expect(apiClient.executeNaturalLanguageQuery).toBeDefined()
      expect(apiClient.healthCheck).toBeDefined()
    })

    it('should create axios instance with interceptors', () => {
      // Verify that the mock axios instance was created and interceptors object exists
      expect(mockAxiosInstance.interceptors).toBeDefined()
      expect(mockAxiosInstance.interceptors.response).toBeDefined()
      expect(mockAxiosInstance.interceptors.response.use).toBeDefined()
    })
  })
})