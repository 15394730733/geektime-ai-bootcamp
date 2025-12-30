/**
 * API 基础配置
 */
import axios, { type AxiosInstance, type AxiosResponse, type AxiosError } from 'axios'
import type { ApiResponse, ErrorResponse } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

/**
 * 创建 axios 实例
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * 请求拦截器
 */
apiClient.interceptors.request.use(
  (config) => {
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    return response
  },
  (error: AxiosError<ErrorResponse>) => {
    const errorResponse: ErrorResponse = {
      code: error.response?.status || 500,
      message: error.response?.data?.message || error.message || '请求失败',
      details: error.response?.data?.details,
      timestamp: Date.now()
    }
    return Promise.reject(errorResponse)
  }
)

export default apiClient
