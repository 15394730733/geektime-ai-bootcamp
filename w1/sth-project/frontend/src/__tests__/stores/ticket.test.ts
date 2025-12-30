import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTicketStore } from '@/stores/ticket'
import { ticketApi } from '@/api/tickets'

vi.mock('@/api/tickets')

describe('useTicketStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('fetchTickets', () => {
    it('应该成功获取 Ticket 列表', async () => {
      const mockResponse = {
        code: 200,
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

      vi.mocked(ticketApi.getTickets).mockResolvedValue(mockResponse)

      const store = useTicketStore()
      await store.fetchTickets({ page: 1, page_size: 20 })

      expect(store.tickets).toEqual(mockResponse.data.tickets)
      expect(store.total).toBe(mockResponse.data.total)
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
    })

    it('应该处理获取失败的情况', async () => {
      const mockError = new Error('获取失败')
      vi.mocked(ticketApi.getTickets).mockRejectedValue(mockError)

      const store = useTicketStore()
      
      await expect(store.fetchTickets()).rejects.toThrow('获取失败')
      expect(store.error).toBe('获取失败')
      expect(store.loading).toBe(false)
    })
  })

  describe('createTicket', () => {
    it('应该成功创建 Ticket', async () => {
      const mockTicket = {
        id: '2',
        title: 'New Ticket',
        description: 'New Description',
        is_completed: false,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        tags: []
      }

      const mockResponse = {
        code: 200,
        data: mockTicket
      }

      vi.mocked(ticketApi.createTicket).mockResolvedValue(mockResponse)

      const store = useTicketStore()
      await store.createTicket({
        title: 'New Ticket',
        description: 'New Description'
      })

      expect(store.tickets).toContainEqual(mockTicket)
    })
  })

  describe('updateTicket', () => {
    it('应该成功更新 Ticket', async () => {
      const mockTicket = {
        id: '1',
        title: 'Updated Ticket',
        description: 'Updated Description',
        is_completed: false,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        tags: []
      }

      const mockResponse = {
        code: 200,
        data: mockTicket
      }

      vi.mocked(ticketApi.updateTicket).mockResolvedValue(mockResponse)

      const store = useTicketStore()
      store.tickets = [
        {
          id: '1',
          title: 'Old Ticket',
          description: 'Old Description',
          is_completed: false,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          tags: []
        }
      ]

      await store.updateTicket('1', {
        title: 'Updated Ticket',
        description: 'Updated Description'
      })

      expect(store.tickets[0].title).toBe('Updated Ticket')
      expect(store.tickets[0].description).toBe('Updated Description')
    })
  })

  describe('deleteTicket', () => {
    it('应该成功删除 Ticket', async () => {
      const mockResponse = {
        code: 200,
        data: null
      }

      vi.mocked(ticketApi.deleteTicket).mockResolvedValue(mockResponse)

      const store = useTicketStore()
      store.tickets = [
        {
          id: '1',
          title: 'Test Ticket',
          description: 'Test Description',
          is_completed: false,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          tags: []
        }
      ]

      await store.deleteTicket('1')

      expect(store.tickets).toHaveLength(0)
    })
  })

  describe('toggleTicketComplete', () => {
    it('应该成功切换 Ticket 完成状态', async () => {
      const mockTicket = {
        id: '1',
        title: 'Test Ticket',
        description: 'Test Description',
        is_completed: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        tags: []
      }

      const mockResponse = {
        code: 200,
        data: mockTicket
      }

      vi.mocked(ticketApi.toggleTicketComplete).mockResolvedValue(mockResponse)

      const store = useTicketStore()
      store.tickets = [
        {
          id: '1',
          title: 'Test Ticket',
          description: 'Test Description',
          is_completed: false,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          tags: []
        }
      ]

      await store.toggleTicketComplete('1')

      expect(store.tickets[0].is_completed).toBe(true)
    })
  })

  describe('computed properties', () => {
    it('completedTickets 应该返回已完成的 Ticket', () => {
      const store = useTicketStore()
      store.tickets = [
        {
          id: '1',
          title: 'Completed Ticket',
          description: 'Test',
          is_completed: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          tags: []
        },
        {
          id: '2',
          title: 'Active Ticket',
          description: 'Test',
          is_completed: false,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          tags: []
        }
      ]

      expect(store.completedTickets).toHaveLength(1)
      expect(store.completedTickets[0].title).toBe('Completed Ticket')
    })

    it('activeTickets 应该返回未完成的 Ticket', () => {
      const store = useTicketStore()
      store.tickets = [
        {
          id: '1',
          title: 'Completed Ticket',
          description: 'Test',
          is_completed: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          tags: []
        },
        {
          id: '2',
          title: 'Active Ticket',
          description: 'Test',
          is_completed: false,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
          tags: []
        }
      ]

      expect(store.activeTickets).toHaveLength(1)
      expect(store.activeTickets[0].title).toBe('Active Ticket')
    })
  })
})
