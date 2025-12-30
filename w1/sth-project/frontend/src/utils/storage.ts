/**
 * 本地存储工具
 */
export const storage = {
  /**
   * 设置本地存储
   * @param key 键
   * @param value 值
   * @param expiry 过期时间（毫秒）
   */
  set<T>(key: string, value: T, expiry?: number): void {
    const item: {
      value: T
      expiry?: number
    } = { value }
    
    if (expiry) {
      item.expiry = Date.now() + expiry
    }
    
    localStorage.setItem(key, JSON.stringify(item))
  },
  
  /**
   * 获取本地存储
   * @param key 键
   * @returns 值
   */
  get<T>(key: string): T | null {
    const itemStr = localStorage.getItem(key)
    
    if (!itemStr) {
      return null
    }
    
    try {
      const item = JSON.parse(itemStr)
      
      if (item.expiry && Date.now() > item.expiry) {
        localStorage.removeItem(key)
        return null
      }
      
      return item.value
    } catch {
      return null
    }
  },
  
  /**
   * 删除本地存储
   * @param key 键
   */
  remove(key: string): void {
    localStorage.removeItem(key)
  },
  
  /**
   * 清空本地存储
   */
  clear(): void {
    localStorage.clear()
  },
  
  /**
   * 获取所有键
   * @returns 键数组
   */
  keys(): string[] {
    return Object.keys(localStorage)
  },
  
  /**
   * 获取存储大小（字节）
   * @returns 大小
   */
  size(): number {
    let size = 0
    for (const key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        size += localStorage[key].length + key.length
      }
    }
    return size
  }
}

/**
 * 会话存储工具
 */
export const sessionStorage = {
  /**
   * 设置会话存储
   * @param key 键
   * @param value 值
   */
  set<T>(key: string, value: T): void {
    window.sessionStorage.setItem(key, JSON.stringify(value))
  },
  
  /**
   * 获取会话存储
   * @param key 键
   * @returns 值
   */
  get<T>(key: string): T | null {
    const itemStr = window.sessionStorage.getItem(key)
    
    if (!itemStr) {
      return null
    }
    
    try {
      return JSON.parse(itemStr)
    } catch {
      return null
    }
  },
  
  /**
   * 删除会话存储
   * @param key 键
   */
  remove(key: string): void {
    window.sessionStorage.removeItem(key)
  },
  
  /**
   * 清空会话存储
   */
  clear(): void {
    window.sessionStorage.clear()
  },
  
  /**
   * 获取所有键
   * @returns 键数组
   */
  keys(): string[] {
    return Object.keys(window.sessionStorage)
  }
}

/**
 * Cookie 工具
 */
export const cookie = {
  /**
   * 设置 Cookie
   * @param key 键
   * @param value 值
   * @param options 配置选项
   */
  set(key: string, value: string, options?: {
    expires?: number | Date
    path?: string
    domain?: string
    secure?: boolean
    sameSite?: 'strict' | 'lax' | 'none'
  }): void {
    let cookieStr = `${encodeURIComponent(key)}=${encodeURIComponent(value)}`
    
    if (options) {
      if (options.expires) {
        const expires = typeof options.expires === 'number'
          ? new Date(Date.now() + options.expires * 864e5)
          : options.expires
        cookieStr += `; expires=${expires.toUTCString()}`
      }
      
      if (options.path) {
        cookieStr += `; path=${options.path}`
      }
      
      if (options.domain) {
        cookieStr += `; domain=${options.domain}`
      }
      
      if (options.secure) {
        cookieStr += '; secure'
      }
      
      if (options.sameSite) {
        cookieStr += `; samesite=${options.sameSite}`
      }
    }
    
    document.cookie = cookieStr
  },
  
  /**
   * 获取 Cookie
   * @param key 键
   * @returns 值
   */
  get(key: string): string | null {
    const cookies = document.cookie.split('; ')
    
    for (const cookie of cookies) {
      const [name, value] = cookie.split('=')
      if (decodeURIComponent(name) === key) {
        return decodeURIComponent(value)
      }
    }
    
    return null
  },
  
  /**
   * 删除 Cookie
   * @param key 键
   * @param options 配置选项
   */
  remove(key: string, options?: { path?: string; domain?: string }): void {
    this.set(key, '', {
      ...options,
      expires: new Date(0)
    })
  },
  
  /**
   * 获取所有 Cookie
   * @returns Cookie 对象
   */
  getAll(): Record<string, string> {
    const cookies: Record<string, string> = {}
    
    document.cookie.split('; ').forEach(cookie => {
      const [name, value] = cookie.split('=')
      cookies[decodeURIComponent(name)] = decodeURIComponent(value)
    })
    
    return cookies
  }
}
