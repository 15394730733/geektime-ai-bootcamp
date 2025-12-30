/**
 * Ticket Store
 * 管理 Ticket 相关的状态和操作
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Ticket, TicketCreate, TicketUpdate } from '@/types'
import * as ticketApi from '@/api/tickets'
import type { SearchParams } from '@/types'

export const useTicketStore = defineStore('ticket', () => {
  const tickets = ref<Ticket[]>([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const completedTickets = computed(() => 
    tickets.value.filter(t => t.is_completed)
  )

  const activeTickets = computed(() => 
    tickets.value.filter(t => !t.is_completed)
  )

  /**
   * 获取 Ticket 列表
   */
  async function fetchTickets(params?: SearchParams) {
    loading.value = true
    error.value = null
    try {
      const response = await ticketApi.getTickets(params)
      if (response.code === 200 && response.data) {
        tickets.value = response.data.tickets
        total.value = response.data.total
      }
    } catch (e: any) {
      error.value = e.message || '获取 Ticket 列表失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建 Ticket
   */
  async function createTicket(data: TicketCreate) {
    loading.value = true
    error.value = null
    try {
      const response = await ticketApi.createTicket(data)
      if (response.code === 200) {
        await fetchTickets()
      }
    } catch (e: any) {
      error.value = e.message || '创建 Ticket 失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新 Ticket
   */
  async function updateTicket(id: string, data: TicketUpdate) {
    loading.value = true
    error.value = null
    try {
      const response = await ticketApi.updateTicket(id, data)
      if (response.code === 200 && response.data) {
        const index = tickets.value.findIndex(t => t.id === id)
        if (index !== -1) {
          tickets.value[index] = response.data
        }
      }
    } catch (e: any) {
      error.value = e.message || '更新 Ticket 失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除 Ticket
   */
  async function deleteTicket(id: string) {
    loading.value = true
    error.value = null
    try {
      const response = await ticketApi.deleteTicket(id)
      if (response.code === 200) {
        tickets.value = tickets.value.filter(t => t.id !== id)
        total.value -= 1
      }
    } catch (e: any) {
      error.value = e.message || '删除 Ticket 失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 切换 Ticket 完成状态
   */
  async function toggleTicketComplete(id: string) {
    const ticket = tickets.value.find(t => t.id === id)
    if (ticket) {
      await updateTicket(id, { is_completed: !ticket.is_completed })
    }
  }

  return {
    tickets,
    total,
    loading,
    error,
    completedTickets,
    activeTickets,
    fetchTickets,
    createTicket,
    updateTicket,
    deleteTicket,
    toggleTicketComplete
  }
})
