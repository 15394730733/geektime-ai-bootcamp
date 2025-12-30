import { describe, it, expect } from 'vitest'
import {
  isValidEmail,
  isValidUrl,
  isValidPhone,
  isEmpty,
  isValidLength,
  isNumber,
  isInteger,
  isPositive,
  isNegative,
  isInRange,
  isValidJson,
  isValidDate
} from '@/utils/validate'

describe('validate utils', () => {
  describe('isValidEmail', () => {
    it('应该验证有效的邮箱', () => {
      expect(isValidEmail('test@example.com')).toBe(true)
      expect(isValidEmail('user.name+tag@example.co.uk')).toBe(true)
    })

    it('应该拒绝无效的邮箱', () => {
      expect(isValidEmail('invalid')).toBe(false)
      expect(isValidEmail('invalid@')).toBe(false)
      expect(isValidEmail('@example.com')).toBe(false)
    })
  })

  describe('isValidUrl', () => {
    it('应该验证有效的 URL', () => {
      expect(isValidUrl('https://example.com')).toBe(true)
      expect(isValidUrl('http://example.com/path')).toBe(true)
    })

    it('应该拒绝无效的 URL', () => {
      expect(isValidUrl('not-a-url')).toBe(false)
      expect(isValidUrl('example')).toBe(false)
    })
  })

  describe('isValidPhone', () => {
    it('应该验证有效的手机号', () => {
      expect(isValidPhone('13800138000')).toBe(true)
      expect(isValidPhone('15912345678')).toBe(true)
    })

    it('应该拒绝无效的手机号', () => {
      expect(isValidPhone('12345678901')).toBe(false)
      expect(isValidPhone('1380013800')).toBe(false)
      expect(isValidPhone('138001380001')).toBe(false)
    })
  })

  describe('isEmpty', () => {
    it('应该识别空值', () => {
      expect(isEmpty(null)).toBe(true)
      expect(isEmpty(undefined)).toBe(true)
      expect(isEmpty('')).toBe(true)
      expect(isEmpty([])).toBe(true)
      expect(isEmpty({})).toBe(true)
    })

    it('应该识别非空值', () => {
      expect(isEmpty('test')).toBe(false)
      expect(isEmpty([1])).toBe(false)
      expect(isEmpty({ a: 1 })).toBe(false)
      expect(isEmpty(0)).toBe(false)
      expect(isEmpty(false)).toBe(false)
    })
  })

  describe('isValidLength', () => {
    it('应该验证字符串长度', () => {
      expect(isValidLength('test', 1, 10)).toBe(true)
      expect(isValidLength('test', 5, 10)).toBe(false)
    })
  })

  describe('isNumber', () => {
    it('应该识别数字', () => {
      expect(isNumber(123)).toBe(true)
      expect(isNumber(12.34)).toBe(true)
      expect(isNumber(0)).toBe(true)
    })

    it('应该拒绝非数字', () => {
      expect(isNumber('123')).toBe(false)
      expect(isNumber(NaN)).toBe(false)
      expect(isNumber(null)).toBe(false)
    })
  })

  describe('isInteger', () => {
    it('应该识别整数', () => {
      expect(isInteger(123)).toBe(true)
      expect(isInteger(0)).toBe(true)
      expect(isInteger(-123)).toBe(true)
    })

    it('应该拒绝非整数', () => {
      expect(isInteger(12.34)).toBe(false)
      expect(isInteger('123')).toBe(false)
    })
  })

  describe('isPositive', () => {
    it('应该识别正数', () => {
      expect(isPositive(123)).toBe(true)
      expect(isPositive(0.01)).toBe(true)
    })

    it('应该拒绝非正数', () => {
      expect(isPositive(0)).toBe(false)
      expect(isPositive(-123)).toBe(false)
    })
  })

  describe('isNegative', () => {
    it('应该识别负数', () => {
      expect(isNegative(-123)).toBe(true)
      expect(isNegative(-0.01)).toBe(true)
    })

    it('应该拒绝非负数', () => {
      expect(isNegative(0)).toBe(false)
      expect(isNegative(123)).toBe(false)
    })
  })

  describe('isInRange', () => {
    it('应该验证范围', () => {
      expect(isInRange(5, 1, 10)).toBe(true)
      expect(isInRange(1, 1, 10)).toBe(true)
      expect(isInRange(10, 1, 10)).toBe(true)
    })

    it('应该拒绝超出范围的值', () => {
      expect(isInRange(0, 1, 10)).toBe(false)
      expect(isInRange(11, 1, 10)).toBe(false)
    })
  })

  describe('isValidJson', () => {
    it('应该验证有效的 JSON', () => {
      expect(isValidJson('{"key":"value"}')).toBe(true)
      expect(isValidJson('[1,2,3]')).toBe(true)
    })

    it('应该拒绝无效的 JSON', () => {
      expect(isValidJson('not json')).toBe(false)
      expect(isValidJson('{invalid}')).toBe(false)
    })
  })

  describe('isValidDate', () => {
    it('应该验证有效的日期', () => {
      expect(isValidDate(new Date())).toBe(true)
      expect(isValidDate('2024-01-01')).toBe(true)
    })

    it('应该拒绝无效的日期', () => {
      expect(isValidDate('invalid')).toBe(false)
      expect(isValidDate('2024-13-01')).toBe(false)
    })
  })
})
