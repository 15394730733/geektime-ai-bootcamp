/**
 * Tag 类型定义
 */
export interface Tag {
  id: string
  name: string
  color: string
  created_at: string
}

export interface TagCreate {
  name: string
  color?: string
}

export interface TagUpdate {
  name?: string
  color?: string
}

export interface TagListResponse {
  tags: Tag[]
  total: number
}

export interface ApiResponse<T = any> {
  code: number
  message: string
  data?: T
  timestamp: number
}
