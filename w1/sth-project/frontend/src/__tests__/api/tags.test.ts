import { describe, it, expect, vi, beforeEach } from 'vitest'
import { tagApi } from '@/api/tags'
import { apiClient } from '@/api/client'

vi.mock('@/api/client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

describe('tagApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getTags', () => {
    it('应该成功获取 Tag 列表', async () => {
      const mockResponse = {
        code: 200,
        message: 'success',
        data: {
          tags: [
            {
              id: '1',
              name: 'Test Tag',
              color: '#FF0000',
              created_at: '2024-01-01T00:00:00Z',
              updated_at: '2024-01-01T00:00:00Z'
            }
          ],
          total: 1
        }
      }

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse)

      const result = await tagApi.getTags({ page: 1, page_size: 20 })

      expect(apiClient.get).toHaveBeenCalledWith('/tags', {
        params: { page: 1, page_size: 20 }
      })
      expect(result).toEqual(mockResponse)
    })
  })

  describe('getTagById', () => {
    it('应该成功获取指定 Tag', async () => {
      const mockResponse = {
        code: 200,
        message: 'success',
        data: {
          id: '1',
          name: 'Test Tag',
          color: '#FF0000',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      }

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse)

      const result = await tagApi.getTagById('1')

      expect(apiClient.get).toHaveBeenCalledWith('/tags/1')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('createTag', () => {
    it('应该成功创建 Tag', async () => {
      const mockData = {
        name: 'New Tag',
        color: '#00FF00'
      }

      const mockResponse = {
        code: 200,
        message: 'success',
        data: {
          id: '2',
          ...mockData,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      }

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse)

      const result = await tagApi.createTag(mockData)

      expect(apiClient.post).toHaveBeenCalledWith('/tags', mockData)
      expect(result).toEqual(mockResponse)
    })
  })

  describe('deleteTag', () => {
    it('应该成功删除 Tag', async () => {
      const mockResponse = {
        code: 200,
        message: 'success',
        data: null
      }

      vi.mocked(apiClient.delete).mockResolvedValue(mockResponse)

      const result = await tagApi.deleteTag('1')

      expect(apiClient.delete).toHaveBeenCalledWith('/tags/1')
      expect(result).toEqual(mockResponse)
    })
  })
})
