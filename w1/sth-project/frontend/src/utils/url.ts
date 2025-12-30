/**
 * 获取 URL 查询参数
 * @param url URL 字符串
 * @returns 查询参数对象
 */
export function getQueryParams(url?: string): Record<string, string> {
  const urlString = url || window.location.href
  const params: Record<string, string> = {}
  
  try {
    const urlObj = new URL(urlString)
    urlObj.searchParams.forEach((value, key) => {
      params[key] = value
    })
  } catch {
    const queryString = urlString.split('?')[1]
    if (queryString) {
      queryString.split('&').forEach(param => {
        const [key, value] = param.split('=')
        if (key) {
          params[decodeURIComponent(key)] = value ? decodeURIComponent(value) : ''
        }
      })
    }
  }
  
  return params
}

/**
 * 设置 URL 查询参数
 * @param params 查询参数对象
 * @param baseUrl 基础 URL
 * @returns 新的 URL
 */
export function setQueryParams(params: Record<string, any>, baseUrl?: string): string {
  const url = new URL(baseUrl || window.location.href)
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      url.searchParams.set(key, String(value))
    } else {
      url.searchParams.delete(key)
    }
  })
  
  return url.toString()
}

/**
 * 更新 URL 查询参数
 * @param params 查询参数对象
 */
export function updateQueryParams(params: Record<string, any>): void {
  const url = setQueryParams(params)
  window.history.replaceState({}, '', url)
}

/**
 * 获取 URL 路径参数
 * @param pattern 路径模式，如 '/users/:id'
 * @param url URL 字符串
 * @returns 路径参数对象
 */
export function getPathParams(pattern: string, url?: string): Record<string, string> {
  const urlString = url || window.location.pathname
  const patternParts = pattern.split('/')
  const urlParts = urlString.split('/')
  const params: Record<string, string> = {}
  
  for (let i = 0; i < patternParts.length; i++) {
    const patternPart = patternParts[i]
    if (patternPart.startsWith(':')) {
      const key = patternPart.substring(1)
      params[key] = urlParts[i] || ''
    }
  }
  
  return params
}

/**
 * 构建 URL
 * @param baseUrl 基础 URL
 * @param path 路径
 * @param params 查询参数
 * @returns 完整的 URL
 */
export function buildUrl(
  baseUrl: string,
  path: string = '',
  params?: Record<string, any>
): string {
  let url = baseUrl
  
  if (path) {
    url = url.replace(/\/$/, '') + '/' + path.replace(/^\//, '')
  }
  
  if (params) {
    const queryString = Object.entries(params)
      .filter(([_, value]) => value !== undefined && value !== null)
      .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
      .join('&')
    
    if (queryString) {
      url += `?${queryString}`
    }
  }
  
  return url
}

/**
 * 解析 URL
 * @param url URL 字符串
 * @returns URL 对象
 */
export function parseUrl(url: string): {
  protocol: string
  hostname: string
  port: string
  pathname: string
  search: string
  hash: string
} {
  try {
    const urlObj = new URL(url)
    return {
      protocol: urlObj.protocol,
      hostname: urlObj.hostname,
      port: urlObj.port,
      pathname: urlObj.pathname,
      search: urlObj.search,
      hash: urlObj.hash
    }
  } catch {
    return {
      protocol: '',
      hostname: '',
      port: '',
      pathname: '',
      search: '',
      hash: ''
    }
  }
}

/**
 * 判断是否为外部链接
 * @param url URL 字符串
 * @returns 是否为外部链接
 */
export function isExternalLink(url: string): boolean {
  try {
    const urlObj = new URL(url, window.location.origin)
    return urlObj.origin !== window.location.origin
  } catch {
    return false
  }
}

/**
 * 下载文件
 * @param url 文件 URL
 * @param filename 文件名
 */
export function downloadFile(url: string, filename?: string): void {
  const link = document.createElement('a')
  link.href = url
  if (filename) {
    link.download = filename
  }
  link.click()
}

/**
 * 复制到剪贴板
 * @param text 文本
 * @returns 是否成功
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text)
      return true
    } else {
      const textarea = document.createElement('textarea')
      textarea.value = text
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      const success = document.execCommand('copy')
      document.body.removeChild(textarea)
      return success
    }
  } catch {
    return false
  }
}
