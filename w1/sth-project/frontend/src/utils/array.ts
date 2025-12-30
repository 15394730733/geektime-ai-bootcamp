/**
 * 数组去重
 * @param arr 数组
 * @param key 对象数组的去重键
 * @returns 去重后的数组
 */
export function unique<T>(arr: T[], key?: keyof T): T[] {
  if (!key) {
    return [...new Set(arr)]
  }
  
  const seen = new Set()
  return arr.filter(item => {
    const value = item[key]
    if (seen.has(value)) {
      return false
    }
    seen.add(value)
    return true
  })
}

/**
 * 数组分组
 * @param arr 数组
 * @param key 分组键
 * @returns 分组后的对象
 */
export function groupBy<T>(arr: T[], key: keyof T): Record<string, T[]> {
  return arr.reduce((result, item) => {
    const groupKey = String(item[key])
    if (!result[groupKey]) {
      result[groupKey] = []
    }
    result[groupKey].push(item)
    return result
  }, {} as Record<string, T[]>)
}

/**
 * 数组排序
 * @param arr 数组
 * @param key 排序键
 * @param order 排序顺序
 * @returns 排序后的数组
 */
export function sortBy<T>(arr: T[], key: keyof T, order: 'asc' | 'desc' = 'asc'): T[] {
  return [...arr].sort((a, b) => {
    const aVal = a[key]
    const bVal = b[key]
    
    if (aVal < bVal) {
      return order === 'asc' ? -1 : 1
    }
    if (aVal > bVal) {
      return order === 'asc' ? 1 : -1
    }
    return 0
  })
}

/**
 * 数组分块
 * @param arr 数组
 * @param size 块大小
 * @returns 分块后的二维数组
 */
export function chunk<T>(arr: T[], size: number): T[][] {
  const result: T[][] = []
  for (let i = 0; i < arr.length; i += size) {
    result.push(arr.slice(i, i + size))
  }
  return result
}

/**
 * 数组扁平化
 * @param arr 数组
 * @param depth 扁平化深度
 * @returns 扁平化后的数组
 */
export function flatten<T>(arr: any[], depth: number = 1): T[] {
  return arr.reduce<T[]>((acc, val) => {
    if (Array.isArray(val) && depth > 0) {
      acc.push(...flatten(val, depth - 1))
    } else {
      acc.push(val)
    }
    return acc
  }, [])
}

/**
 * 数组差集
 * @param arr1 数组1
 * @param arr2 数组2
 * @returns 差集
 */
export function difference<T>(arr1: T[], arr2: T[]): T[] {
  return arr1.filter(item => !arr2.includes(item))
}

/**
 * 数组交集
 * @param arr1 数组1
 * @param arr2 数组2
 * @returns 交集
 */
export function intersection<T>(arr1: T[], arr2: T[]): T[] {
  return arr1.filter(item => arr2.includes(item))
}

/**
 * 数组并集
 * @param arr1 数组1
 * @param arr2 数组2
 * @returns 并集
 */
export function union<T>(arr1: T[], arr2: T[]): T[] {
  return unique([...arr1, ...arr2])
}

/**
 * 数组随机打乱
 * @param arr 数组
 * @returns 打乱后的数组
 */
export function shuffle<T>(arr: T[]): T[] {
  const result = [...arr]
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[result[i], result[j]] = [result[j], result[i]]
  }
  return result
}

/**
 * 数组求和
 * @param arr 数组
 * @param key 求和键
 * @returns 和
 */
export function sum<T>(arr: T[], key?: keyof T): number {
  if (key) {
    return arr.reduce((acc, item) => acc + (Number(item[key]) || 0), 0)
  }
  return arr.reduce((acc, item) => acc + (Number(item) || 0), 0)
}

/**
 * 数组求平均值
 * @param arr 数组
 * @param key 求平均值键
 * @returns 平均值
 */
export function average<T>(arr: T[], key?: keyof T): number {
  if (arr.length === 0) return 0
  return sum(arr, key) / arr.length
}

/**
 * 数组最大值
 * @param arr 数组
 * @param key 比较键
 * @returns 最大值
 */
export function max<T>(arr: T[], key?: keyof T): T | undefined {
  if (arr.length === 0) return undefined
  if (key) {
    return arr.reduce((max, item) => (item[key] > max[key] ? item : max), arr[0])
  }
  return arr.reduce((max, item) => (item > max ? item : max), arr[0])
}

/**
 * 数组最小值
 * @param arr 数组
 * @param key 比较键
 * @returns 最小值
 */
export function min<T>(arr: T[], key?: keyof T): T | undefined {
  if (arr.length === 0) return undefined
  if (key) {
    return arr.reduce((min, item) => (item[key] < min[key] ? item : min), arr[0])
  }
  return arr.reduce((min, item) => (item < min ? item : min), arr[0])
}

/**
 * 数组分页
 * @param arr 数组
 * @param page 页码
 * @param pageSize 每页大小
 * @returns 分页结果
 */
export function paginate<T>(arr: T[], page: number, pageSize: number): {
  data: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
} {
  const total = arr.length
  const totalPages = Math.ceil(total / pageSize)
  const start = (page - 1) * pageSize
  const end = start + pageSize
  const data = arr.slice(start, end)
  
  return {
    data,
    total,
    page,
    pageSize,
    totalPages
  }
}
