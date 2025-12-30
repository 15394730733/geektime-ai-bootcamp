import { describe, it, expect } from 'vitest'
import { 
  truncateText, 
  toCamelCase, 
  toKebabCase, 
  toSnakeCase,
  capitalize,
  removeSpaces,
  randomString
} from '@/utils/string'

describe('string utils', () => {
  describe('truncateText', () => {
    it('应该截断超过最大长度的文本', () => {
      expect(truncateText('Hello World', 5)).toBe('Hello...')
    })

    it('应该不截断短于最大长度的文本', () => {
      expect(truncateText('Hello', 10)).toBe('Hello')
    })

    it('应该支持自定义后缀', () => {
      expect(truncateText('Hello World', 5, '***')).toBe('Hello***')
    })

    it('应该处理空字符串', () => {
      expect(truncateText('', 10)).toBe('')
    })
  })

  describe('toCamelCase', () => {
    it('应该转换为驼峰命名', () => {
      expect(toCamelCase('hello-world')).toBe('helloWorld')
      expect(toCamelCase('hello_world')).toBe('helloWorld')
      expect(toCamelCase('hello world')).toBe('helloWorld')
    })

    it('应该处理空格和下划线', () => {
      expect(toCamelCase('hello_world_test')).toBe('helloWorldTest')
    })
  })

  describe('toKebabCase', () => {
    it('应该转换为短横线命名', () => {
      expect(toKebabCase('helloWorld')).toBe('hello-world')
      expect(toKebabCase('hello_world')).toBe('hello-world')
      expect(toKebabCase('hello world')).toBe('hello-world')
    })
  })

  describe('toSnakeCase', () => {
    it('应该转换为蛇形命名', () => {
      expect(toSnakeCase('helloWorld')).toBe('hello_world')
      expect(toSnakeCase('hello-world')).toBe('hello_world')
      expect(toSnakeCase('hello world')).toBe('hello_world')
    })
  })

  describe('capitalize', () => {
    it('应该首字母大写', () => {
      expect(capitalize('hello')).toBe('Hello')
    })

    it('应该处理空字符串', () => {
      expect(capitalize('')).toBe('')
    })

    it('应该将其他字母小写', () => {
      expect(capitalize('HELLO')).toBe('Hello')
    })
  })

  describe('removeSpaces', () => {
    it('应该移除所有空格', () => {
      expect(removeSpaces('hello world test')).toBe('helloworldtest')
    })

    it('应该处理没有空格的字符串', () => {
      expect(removeSpaces('hello')).toBe('hello')
    })
  })

  describe('randomString', () => {
    it('应该生成指定长度的随机字符串', () => {
      const str = randomString(10)
      expect(str).toHaveLength(10)
    })

    it('应该生成不同的字符串', () => {
      const str1 = randomString(10)
      const str2 = randomString(10)
      expect(str1).not.toBe(str2)
    })

    it('应该使用默认长度', () => {
      const str = randomString()
      expect(str).toHaveLength(8)
    })
  })
})
