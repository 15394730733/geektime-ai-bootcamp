import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ticketApi } from '@/api/tickets'
import { apiClient } from '@/api/client'

vi.mock('@/api/client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

describe('ticketApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getTickets', () => {
    it('应该成功获取 Ticket 列表', async () => {
      const mockResponse = {
        code: 200,
        message: 'success',
        data: {
          tickets: [
            {
              id: '1',
              title: 'Test Ticket',
              description: 'Test Description',
              is_completed: false,
              created_at: '2024-01-01T00:00:00Z',
              updated_at: '2024-01-01T00:00:00Z',
              tags: []
            }
          ],
          total: 1
        }
      }

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse)

      const result = await ticketApi.getTickets({ page: 1, page_size: 20 })

      expect(apiClient.get).toHaveBeenCalledWith('/tickets', {
        params: { page: 1, page_size: 20 }
      })
      expect(result).toEqual(mockResponse)
    })

    it('应该正确处理搜索参数', async () => {
      const mockResponse = {
        code: 200,
        message: 'success',
        data: {
          tickets: [],
          total: 0
        }
      }

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse)

      await ticketApi.getTickets({ keyword: 'test' })

      expect(apiClient.get).toHaveBeenCalledWith('/tickets', {
        params: { keyword: 'test' }
      })
    })
  })

  describe('getTicketById', () => {
    it('应该成功获取指定 Ticket', async () => {
      const mockResponse = {
        code: 200,
        message: 'success',
        data: {
          id: '1',
          title: 'Test Ticket',
          description: 'Test Description',
          is_completed: false,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          tags: []
        }
      }

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse)

      const result = await ticketApi.getTicketById('1')

      expect(apiClient.get).toHaveBeenCalledWith('/tickets/1')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('createTicket', () => {
    it('应该成功创建 Ticket', async () => {
      const mockData = {
        title: 'New Ticket',
        description: 'New Description',
        tag_ids: ['tag1']
      }

      const mockResponse = {
        code: 200,
        message: 'success',
        data: {
          id: '2',
          ...mockData,
          is_completed: false,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          tags: []
        }
      }

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse)

      const result = await ticketApi.createTicket(mockData)

      expect(apiClient.post).toHaveBeenCalledWith('/tickets', mockData)
      expect(result).toEqual(mockResponse)
    })
  })

  describe('updateTicket', () => {
    it('应该成功更新 Ticket', async () => {
      const mockData = {
        title: 'Updated Ticket',
        description: 'Updated Description'
      }

      const mockResponse = {
        code: 200,
        message: 'success',
        data: {
          id: '1',
          ...mockData,
          is_completed: false,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          tags: []
        }
      }

      vi.mocked(apiClient.put).mockResolvedValue(mockResponse)

      const result = await ticketApi.updateTicket('1', mockData)

      expect(apiClient.put).toHaveBeenCalledWith('/tickets/1', mockData)
      expect(result).toEqual(mockResponse)
    })
  })

  describe('deleteTicket', () => {
    it('应该成功删除 Ticket', async () => {
      const mockResponse = {
        code: 200,
        message: 'success',
        data: null
      }

      vi.mocked(apiClient.delete).mockResolvedValue(mockResponse)

      const result = await ticketApi.deleteTicket('1')

      expect(apiClient.delete).toHaveBeenCalledWith('/tickets/1')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('toggleTicketComplete', () => {
    it('应该成功切换 Ticket 完成状态', async () => {
      const mockResponse = {
        code: 200,
        message: 'success',
        data: {
          id: '1',
          title: 'Test Ticket',
          description: 'Test Description',
          is_completed: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          tags: []
        }
      }

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse)

      const result = await ticketApi.toggleTicketComplete('1')

      expect(apiClient.post).toHaveBeenCalledWith('/tickets/1/toggle-complete')
      expect(result).toEqual(mockResponse)
    })
  })
})
