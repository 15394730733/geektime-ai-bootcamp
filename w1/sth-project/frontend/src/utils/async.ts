/**
 * 防抖函数
 * @param fn 要防抖的函数
 * @param delay 延迟时间（毫秒）
 * @returns 防抖后的函数
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null
  
  return function (this: any, ...args: Parameters<T>) {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    
    timeoutId = setTimeout(() => {
      fn.apply(this, args)
      timeoutId = null
    }, delay)
  }
}

/**
 * 节流函数
 * @param fn 要节流的函数
 * @param delay 延迟时间（毫秒）
 * @returns 节流后的函数
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let lastCallTime = 0
  let timeoutId: ReturnType<typeof setTimeout> | null = null
  
  return function (this: any, ...args: Parameters<T>) {
    const now = Date.now()
    const remainingTime = delay - (now - lastCallTime)
    
    if (remainingTime <= 0) {
      if (timeoutId) {
        clearTimeout(timeoutId)
        timeoutId = null
      }
      lastCallTime = now
      fn.apply(this, args)
    } else if (!timeoutId) {
      timeoutId = setTimeout(() => {
        lastCallTime = Date.now()
        timeoutId = null
        fn.apply(this, args)
      }, remainingTime)
    }
  }
}

/**
 * 延迟执行
 * @param ms 延迟时间（毫秒）
 * @returns Promise
 */
export function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * 重试函数
 * @param fn 要重试的函数
 * @param options 配置选项
 * @returns Promise
 */
export async function retry<T>(
  fn: () => Promise<T>,
  options: {
    times?: number
    delay?: number
    backoff?: boolean
    onRetry?: (error: Error, attempt: number) => void
  } = {}
): Promise<T> {
  const {
    times = 3,
    delay: retryDelay = 1000,
    backoff = true,
    onRetry
  } = options
  
  let lastError: Error | null = null
  
  for (let attempt = 1; attempt <= times; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error as Error
      
      if (attempt < times) {
        if (onRetry) {
          onRetry(lastError, attempt)
        }
        
        const currentDelay = backoff ? retryDelay * attempt : retryDelay
        await delay(currentDelay)
      }
    }
  }
  
  throw lastError
}

/**
 * 批量执行异步函数
 * @param items 项目数组
 * @param fn 执行函数
 * @param concurrency 并发数
 * @returns Promise
 */
export async function parallel<T, R>(
  items: T[],
  fn: (item: T, index: number) => Promise<R>,
  concurrency: number = 5
): Promise<R[]> {
  const results: R[] = []
  const executing: Promise<void>[] = []
  
  for (let i = 0; i < items.length; i++) {
    const promise = fn(items[i], i).then(result => {
      results[i] = result
    })
    
    executing.push(promise)
    
    if (executing.length >= concurrency) {
      await Promise.race(executing)
      executing.splice(
        executing.findIndex(p => {
          return p === promise
        }),
        1
      )
    }
  }
  
  await Promise.all(executing)
  return results
}

/**
 * 缓存函数结果
 * @param fn 要缓存的函数
 * @param options 配置选项
 * @returns 带缓存的函数
 */
export function memoize<T extends (...args: any[]) => any>(
  fn: T,
  options: {
    key?: (...args: Parameters<T>) => string
    ttl?: number
  } = {}
): T {
  const cache = new Map<string, { value: ReturnType<T>; expiry: number }>()
  const { key, ttl } = options
  
  return function (this: any, ...args: Parameters<T>): ReturnType<T> {
    const cacheKey = key ? key(...args) : JSON.stringify(args)
    const cached = cache.get(cacheKey)
    
    if (cached && (!ttl || Date.now() < cached.expiry)) {
      return cached.value
    }
    
    const result = fn.apply(this, args)
    cache.set(cacheKey, {
      value: result,
      expiry: ttl ? Date.now() + ttl : Infinity
    })
    
    return result
  } as T
}

/**
 * 清除缓存
 * @param memoizedFn 缓存的函数
 */
export function clearMemoize<T extends (...args: any[]) => any>(memoizedFn: T): void {
  const cache = (memoizedFn as any).cache as Map<string, any>
  if (cache) {
    cache.clear()
  }
}
