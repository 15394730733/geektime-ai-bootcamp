/**
 * Unit tests for Data Provider Service
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'

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

// Import the data provider after mocking
const { dataProvider } = await import('../dataProvider')

describe('DataProvider', () => {
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

  describe('getList', () => {
    it('should get databases list successfully with direct array response', async () => {
      const mockDatabases = [
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

      const result = await dataProvider.getList({
        resource: 'dbs',
        pagination: { current: 1, pageSize: 10 },
        filters: [],
        sorters: [],
        meta: {},
      })

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/dbs/')
      expect(result).toEqual({
        data: mockDatabases,
        total: 1,
      })
    })

    it('should get databases list successfully with wrapped response', async () => {
      const mockDatabases = [
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
          data: mockDatabases,
        },
      })

      const result = await dataProvider.getList({
        resource: 'dbs',
        pagination: { current: 1, pageSize: 10 },
        filters: [],
        sorters: [],
        meta: {},
      })

      expect(result).toEqual({
        data: mockDatabases,
        total: 1,
      })
    })

    it('should handle empty databases list', async () => {
      mockAxiosInstance.get.mockResolvedValue({
        data: [],
      })

      const result = await dataProvider.getList({
        resource: 'dbs',
        pagination: { current: 1, pageSize: 10 },
        filters: [],
        sorters: [],
        meta: {},
      })

      expect(result).toEqual({
        data: [],
        total: 0,
      })
    })

    it('should throw error for unsupported resource', async () => {
      await expect(
        dataProvider.getList({
          resource: 'unsupported',
          pagination: { current: 1, pageSize: 10 },
          filters: [],
          sorters: [],
          meta: {},
        })
      ).rejects.toThrow('Unsupported resource: unsupported')
    })
  })

  describe('getOne', () => {
    it('should get single database successfully', async () => {
      const mockDatabase = {
        id: '1',
        name: 'test-db',
        url: 'postgresql://localhost:5432/test',
        description: 'Test database',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      mockAxiosInstance.get.mockResolvedValue({
        data: {
          data: mockDatabase,
        },
      })

      const result = await dataProvider.getOne({
        resource: 'dbs',
        id: 'test-db',
        meta: {},
      })

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/dbs/test-db')
      expect(result).toEqual({
        data: mockDatabase,
      })
    })

    it('should throw error for unsupported resource', async () => {
      await expect(
        dataProvider.getOne({
          resource: 'unsupported',
          id: '1',
          meta: {},
        })
      ).rejects.toThrow('Unsupported resource: unsupported')
    })
  })

  describe('create', () => {
    it('should create database successfully', async () => {
      const newDatabase = {
        name: 'new-db',
        url: 'postgresql://localhost:5432/new',
        description: 'New database',
        is_active: true,
      }

      const createdDatabase = {
        ...newDatabase,
        id: '2',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }

      mockAxiosInstance.put.mockResolvedValue({
        data: {
          data: createdDatabase,
        },
      })

      const result = await dataProvider.create({
        resource: 'dbs',
        variables: newDatabase,
        meta: {},
      })

      expect(mockAxiosInstance.put).toHaveBeenCalledWith('/dbs/new-db', newDatabase)
      expect(result).toEqual({
        data: createdDatabase,
      })
    })

    it('should throw error for unsupported resource', async () => {
      await expect(
        dataProvider.create({
          resource: 'unsupported',
          variables: {},
          meta: {},
        })
      ).rejects.toThrow('Unsupported resource: unsupported')
    })
  })

  describe('update', () => {
    it('should update database successfully', async () => {
      const updateData = {
        description: 'Updated description',
      }

      const updatedDatabase = {
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
          data: updatedDatabase,
        },
      })

      const result = await dataProvider.update({
        resource: 'dbs',
        id: 'test-db',
        variables: updateData,
        meta: {},
      })

      expect(mockAxiosInstance.put).toHaveBeenCalledWith('/dbs/test-db', updateData)
      expect(result).toEqual({
        data: updatedDatabase,
      })
    })

    it('should throw error for unsupported resource', async () => {
      await expect(
        dataProvider.update({
          resource: 'unsupported',
          id: '1',
          variables: {},
          meta: {},
        })
      ).rejects.toThrow('Unsupported resource: unsupported')
    })
  })

  describe('deleteOne', () => {
    it('should delete database successfully', async () => {
      mockAxiosInstance.delete.mockResolvedValue({
        data: {
          success: true,
          message: 'Database deleted',
        },
      })

      const result = await dataProvider.deleteOne({
        resource: 'dbs',
        id: 'test-db',
        meta: {},
      })

      expect(mockAxiosInstance.delete).toHaveBeenCalledWith('/dbs/test-db')
      expect(result).toEqual({
        data: {
          success: true,
          message: 'Database deleted',
        },
      })
    })

    it('should throw error for unsupported resource', async () => {
      await expect(
        dataProvider.deleteOne({
          resource: 'unsupported',
          id: '1',
          meta: {},
        })
      ).rejects.toThrow('Unsupported resource: unsupported')
    })
  })

  describe('Error Handling', () => {
    it('should handle 400 Bad Request errors', async () => {
      const errorResponse = {
        response: {
          status: 400,
          data: {
            message: 'Invalid database configuration',
          },
        },
      }

      // Simulate the interceptor error handling
      mockAxiosInstance.get.mockImplementation(() => {
        return Promise.reject(mockAxiosInstance._errorHandler(errorResponse))
      })

      await expect(
        dataProvider.getList({
          resource: 'dbs',
          pagination: { current: 1, pageSize: 10 },
          filters: [],
          sorters: [],
          meta: {},
        })
      ).rejects.toThrow('Invalid database configuration')
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

      await expect(
        dataProvider.getOne({
          resource: 'dbs',
          id: 'nonexistent-db',
          meta: {},
        })
      ).rejects.toThrow('Resource not found')
    })

    it('should handle 500 Internal Server Error', async () => {
      const errorResponse = {
        response: {
          status: 500,
        },
      }

      // Simulate the interceptor error handling
      mockAxiosInstance.put.mockImplementation(() => {
        return Promise.reject(mockAxiosInstance._errorHandler(errorResponse))
      })

      await expect(
        dataProvider.create({
          resource: 'dbs',
          variables: { name: 'test' },
          meta: {},
        })
      ).rejects.toThrow('Internal server error')
    })

    it('should handle network errors', async () => {
      const networkError = new Error('Network Error')
      
      // Simulate the interceptor error handling
      mockAxiosInstance.get.mockImplementation(() => {
        return Promise.reject(mockAxiosInstance._errorHandler(networkError))
      })

      await expect(
        dataProvider.getList({
          resource: 'dbs',
          pagination: { current: 1, pageSize: 10 },
          filters: [],
          sorters: [],
          meta: {},
        })
      ).rejects.toThrow('Network Error')
    })
  })

  describe('Configuration', () => {
    it('should return correct API URL', () => {
      const apiUrl = dataProvider.getApiUrl()
      expect(apiUrl).toBe('http://localhost:8000/api/v1')
    })

    it('should have data provider configured', () => {
      // Test that the data provider exists and has the expected methods
      expect(dataProvider).toBeDefined()
      expect(dataProvider.getList).toBeDefined()
      expect(dataProvider.getOne).toBeDefined()
      expect(dataProvider.create).toBeDefined()
      expect(dataProvider.update).toBeDefined()
      expect(dataProvider.deleteOne).toBeDefined()
    })
  })
})