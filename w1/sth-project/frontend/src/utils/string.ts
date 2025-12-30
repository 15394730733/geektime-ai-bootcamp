/**
 * 截断文本，超出指定长度时添加省略号
 * @param text 原始文本
 * @param maxLength 最大长度
 * @param suffix 后缀，默认 '...'
 * @returns 截断后的文本
 */
export function truncateText(text: string, maxLength: number, suffix: string = '...'): string {
  if (!text || text.length <= maxLength) {
    return text
  }
  return text.substring(0, maxLength) + suffix
}

/**
 * 转换为驼峰命名
 * @param str 原始字符串
 * @returns 驼峰命名字符串
 */
export function toCamelCase(str: string): string {
  return str
    .replace(/[-_\s]+(.)?/g, (_, c) => (c ? c.toUpperCase() : ''))
    .replace(/^(.)/, c => c.toLowerCase())
}

/**
 * 转换为短横线命名
 * @param str 原始字符串
 * @returns 短横线命名字符串
 */
export function toKebabCase(str: string): string {
  return str
    .replace(/([a-z])([A-Z])/g, '$1-$2')
    .replace(/[\s_]+/g, '-')
    .toLowerCase()
}

/**
 * 转换为蛇形命名
 * @param str 原始字符串
 * @returns 蛇形命名字符串
 */
export function toSnakeCase(str: string): string {
  return str
    .replace(/([a-z])([A-Z])/g, '$1_$2')
    .replace(/[\s-]+/g, '_')
    .toLowerCase()
}

/**
 * 首字母大写
 * @param str 原始字符串
 * @returns 首字母大写的字符串
 */
export function capitalize(str: string): string {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
}

/**
 * 移除字符串中的所有空格
 * @param str 原始字符串
 * @returns 移除空格后的字符串
 */
export function removeSpaces(str: string): string {
  return str.replace(/\s+/g, '')
}

/**
 * 高亮搜索关键词
 * @param text 原始文本
 * @param keyword 搜索关键词
 * @param highlightClass 高亮样式类名
 * @returns 带高亮标记的 HTML 字符串
 */
export function highlightKeyword(text: string, keyword: string, highlightClass: string = 'highlight'): string {
  if (!keyword || !text) {
    return text
  }
  
  const regex = new RegExp(`(${keyword})`, 'gi')
  return text.replace(regex, `<span class="${highlightClass}">$1</span>`)
}

/**
 * 生成随机字符串
 * @param length 字符串长度
 * @param charset 字符集
 * @returns 随机字符串
 */
export function randomString(length: number = 8, charset: string = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'): string {
  let result = ''
  for (let i = 0; i < length; i++) {
    result += charset.charAt(Math.floor(Math.random() * charset.length))
  }
  return result
}
