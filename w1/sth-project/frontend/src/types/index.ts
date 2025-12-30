/**
 * 通用类型定义
 */
export interface PaginationParams {
  skip?: number
  limit?: number
}

export interface SearchParams extends PaginationParams {
  tag?: string
  search?: string
}

export interface ErrorResponse {
  code: number
  message: string
  details?: any
  timestamp: number
}
