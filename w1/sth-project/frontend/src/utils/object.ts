/**
 * 深度克隆对象
 * @param obj 待克隆的对象
 * @returns 克隆后的对象
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj
  }
  
  if (obj instanceof Date) {
    return new Date(obj.getTime()) as any
  }
  
  if (obj instanceof Array) {
    return obj.map(item => deepClone(item)) as any
  }
  
  if (obj instanceof Object) {
    const clonedObj = {} as any
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key])
      }
    }
    return clonedObj
  }
  
  return obj
}

/**
 * 深度合并对象
 * @param target 目标对象
 * @param sources 源对象
 * @returns 合并后的对象
 */
export function deepMerge<T extends object>(target: T, ...sources: Partial<T>[]): T {
  if (!sources.length) return target
  const source = sources.shift()
  
  if (isObject(target) && isObject(source)) {
    for (const key in source) {
      if (isObject(source[key])) {
        if (!target[key as keyof T]) {
          Object.assign(target, { [key]: {} })
        }
        deepMerge(target[key as keyof T] as object, source[key] as object)
      } else {
        Object.assign(target, { [key]: source[key] })
      }
    }
  }
  
  return deepMerge(target, ...sources)
}

/**
 * 判断是否为对象
 * @param obj 待判断的值
 * @returns 是否为对象
 */
function isObject(item: any): boolean {
  return item && typeof item === 'object' && !Array.isArray(item)
}

/**
 * 获取对象的嵌套属性值
 * @param obj 对象
 * @param path 属性路径，如 'a.b.c'
 * @param defaultValue 默认值
 * @returns 属性值
 */
export function getNestedValue<T = any>(obj: any, path: string, defaultValue?: T): T {
  const keys = path.split('.')
  let result = obj
  
  for (const key of keys) {
    if (result === null || result === undefined) {
      return defaultValue as T
    }
    result = result[key]
  }
  
  return result !== undefined ? result : (defaultValue as T)
}

/**
 * 设置对象的嵌套属性值
 * @param obj 对象
 * @param path 属性路径，如 'a.b.c'
 * @param value 值
 */
export function setNestedValue(obj: any, path: string, value: any): void {
  const keys = path.split('.')
  let current = obj
  
  for (let i = 0; i < keys.length - 1; i++) {
    const key = keys[i]
    if (!(key in current)) {
      current[key] = {}
    }
    current = current[key]
  }
  
  current[keys[keys.length - 1]] = value
}

/**
 * 删除对象的嵌套属性
 * @param obj 对象
 * @param path 属性路径，如 'a.b.c'
 */
export function deleteNestedValue(obj: any, path: string): void {
  const keys = path.split('.')
  let current = obj
  
  for (let i = 0; i < keys.length - 1; i++) {
    const key = keys[i]
    if (!(key in current)) {
      return
    }
    current = current[key]
  }
  
  delete current[keys[keys.length - 1]]
}

/**
 * 过滤对象的属性
 * @param obj 对象
 * @param predicate 过滤函数
 * @returns 过滤后的对象
 */
export function filterObject<T extends object>(
  obj: T,
  predicate: (key: keyof T, value: T[keyof T]) => boolean
): Partial<T> {
  const result: Partial<T> = {}
  
  for (const key in obj) {
    if (obj.hasOwnProperty(key) && predicate(key, obj[key])) {
      result[key] = obj[key]
    }
  }
  
  return result
}

/**
 * 映射对象的属性
 * @param obj 对象
 * @param mapper 映射函数
 * @returns 映射后的对象
 */
export function mapObject<T extends object, R>(
  obj: T,
  mapper: (key: keyof T, value: T[keyof T]) => R
): Record<keyof T, R> {
  const result = {} as Record<keyof T, R>
  
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      result[key] = mapper(key, obj[key])
    }
  }
  
  return result
}

/**
 * 检查对象是否包含某个属性
 * @param obj 对象
 * @param path 属性路径
 * @returns 是否包含
 */
export function hasProperty(obj: any, path: string): boolean {
  const keys = path.split('.')
  let current = obj
  
  for (const key of keys) {
    if (current === null || current === undefined || !(key in current)) {
      return false
    }
    current = current[key]
  }
  
  return true
}
