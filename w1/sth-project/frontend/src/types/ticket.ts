/**
 * Ticket 类型定义
 */
export interface Tag {
  id: string
  name: string
  color: string
}

export interface Ticket {
  id: string
  title: string
  description?: string
  is_completed: boolean
  created_at: string
  updated_at: string
  tags: Tag[]
}

export interface TicketCreate {
  title: string
  description?: string
  tags?: string[]
}

export interface TicketUpdate {
  title?: string
  description?: string
  is_completed?: boolean
}

export interface TicketListResponse {
  tickets: Ticket[]
  total: number
}

export interface ApiResponse<T = any> {
  code: number
  message: string
  data?: T
  timestamp: number
}
