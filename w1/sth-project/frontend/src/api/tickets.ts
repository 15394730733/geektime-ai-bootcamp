/**
 * Ticket API 封装
 */
import apiClient from './client'
import type {
  Ticket,
  TicketCreate,
  TicketUpdate,
  TicketListResponse,
  ApiResponse
} from '@/types'
import type { SearchParams } from '@/types'

/**
 * 创建 Ticket
 */
export async function createTicket(data: TicketCreate): Promise<ApiResponse<string>> {
  const response = await apiClient.post<ApiResponse<string>>('/api/v1/addTickets', data)
  return response.data
}

/**
 * 获取 Ticket 列表
 */
export async function getTickets(params?: SearchParams): Promise<ApiResponse<TicketListResponse>> {
  const response = await apiClient.get<ApiResponse<TicketListResponse>>('/api/v1/listTickets', { params })
  return response.data
}

/**
 * 获取单个 Ticket
 */
export async function getTicket(id: string): Promise<ApiResponse<Ticket>> {
  const response = await apiClient.get<ApiResponse<Ticket>>(`/api/v1/tickets/${id}`)
  return response.data
}

/**
 * 更新 Ticket
 */
export async function updateTicket(id: string, data: TicketUpdate): Promise<ApiResponse<Ticket>> {
  const response = await apiClient.put<ApiResponse<Ticket>>(`/api/v1/updateTickets/${id}`, data)
  return response.data
}

/**
 * 删除 Ticket
 */
export async function deleteTicket(id: string): Promise<ApiResponse<void>> {
  const response = await apiClient.delete<ApiResponse<void>>(`/api/v1/tickets/${id}`)
  return response.data
}
