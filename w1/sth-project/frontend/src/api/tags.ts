/**
 * Tag API 封装
 */
import apiClient from './client'
import type {
  Tag,
  TagCreate,
  TagUpdate,
  TagListResponse,
  ApiResponse
} from '@/types'
import type { PaginationParams } from '@/types'

/**
 * 创建 Tag
 */
export async function createTag(data: TagCreate): Promise<ApiResponse<string>> {
  const response = await apiClient.post<ApiResponse<string>>('/api/v1/addTags', data)
  return response.data
}

/**
 * 获取 Tag 列表
 */
export async function getTags(params?: PaginationParams): Promise<ApiResponse<TagListResponse>> {
  const response = await apiClient.get<ApiResponse<TagListResponse>>('/api/v1/listTags', { params })
  return response.data
}

/**
 * 删除 Tag
 */
export async function deleteTag(id: string): Promise<ApiResponse<void>> {
  const response = await apiClient.delete<ApiResponse<void>>(`/api/v1/tags/${id}`)
  return response.data
}
