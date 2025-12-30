/**
 * 验证邮箱格式
 * @param email 邮箱地址
 * @returns 是否有效
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * 验证 URL 格式
 * @param url URL 地址
 * @returns 是否有效
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * 验证手机号格式（中国大陆）
 * @param phone 手机号
 * @returns 是否有效
 */
export function isValidPhone(phone: string): boolean {
  const phoneRegex = /^1[3-9]\d{9}$/
  return phoneRegex.test(phone)
}

/**
 * 验证是否为空值
 * @param value 待验证的值
 * @returns 是否为空
 */
export function isEmpty(value: any): boolean {
  if (value === null || value === undefined) {
    return true
  }
  if (typeof value === 'string') {
    return value.trim().length === 0
  }
  if (Array.isArray(value)) {
    return value.length === 0
  }
  if (typeof value === 'object') {
    return Object.keys(value).length === 0
  }
  return false
}

/**
 * 验证字符串长度
 * @param str 字符串
 * @param min 最小长度
 * @param max 最大长度
 * @returns 是否在范围内
 */
export function isValidLength(str: string, min: number, max: number): boolean {
  return str.length >= min && str.length <= max
}

/**
 * 验证是否为数字
 * @param value 待验证的值
 * @returns 是否为数字
 */
export function isNumber(value: any): boolean {
  return typeof value === 'number' && !isNaN(value)
}

/**
 * 验证是否为整数
 * @param value 待验证的值
 * @returns 是否为整数
 */
export function isInteger(value: any): boolean {
  return Number.isInteger(value)
}

/**
 * 验证是否为正数
 * @param value 待验证的值
 * @returns 是否为正数
 */
export function isPositive(value: any): boolean {
  return isNumber(value) && value > 0
}

/**
 * 验证是否为负数
 * @param value 待验证的值
 * @returns 是否为负数
 */
export function isNegative(value: any): boolean {
  return isNumber(value) && value < 0
}

/**
 * 验证是否在指定范围内
 * @param value 待验证的值
 * @param min 最小值
 * @param max 最大值
 * @returns 是否在范围内
 */
export function isInRange(value: number, min: number, max: number): boolean {
  return value >= min && value <= max
}

/**
 * 验证是否为有效的 JSON 字符串
 * @param str JSON 字符串
 * @returns 是否有效
 */
export function isValidJson(str: string): boolean {
  try {
    JSON.parse(str)
    return true
  } catch {
    return false
  }
}

/**
 * 验证是否为有效的日期
 * @param date 日期字符串或日期对象
 * @returns 是否有效
 */
export function isValidDate(date: any): boolean {
  if (date instanceof Date) {
    return !isNaN(date.getTime())
  }
  const d = new Date(date)
  return !isNaN(d.getTime())
}
