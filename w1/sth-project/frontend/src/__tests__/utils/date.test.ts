import { describe, it, expect } from 'vitest'
import { formatDate, formatRelativeTime, isToday, isYesterday } from '@/utils/date'

describe('date utils', () => {
  describe('formatDate', () => {
    it('应该正确格式化日期', () => {
      const date = new Date('2024-01-15T10:30:45Z')
      expect(formatDate(date)).toBe('2024-01-15 10:30:45')
    })

    it('应该支持自定义格式', () => {
      const date = new Date('2024-01-15T10:30:45Z')
      expect(formatDate(date, 'YYYY-MM-DD')).toBe('2024-01-15')
      expect(formatDate(date, 'HH:mm:ss')).toBe('10:30:45')
    })

    it('应该处理无效日期', () => {
      expect(formatDate('invalid')).toBe('')
    })
  })

  describe('formatRelativeTime', () => {
    it('应该返回"刚刚"对于刚刚的时间', () => {
      const now = new Date()
      expect(formatRelativeTime(now)).toBe('刚刚')
    })

    it('应该返回"X分钟前"', () => {
      const date = new Date(Date.now() - 5 * 60 * 1000)
      expect(formatRelativeTime(date)).toBe('5分钟前')
    })

    it('应该返回"X小时前"', () => {
      const date = new Date(Date.now() - 3 * 60 * 60 * 1000)
      expect(formatRelativeTime(date)).toBe('3小时前')
    })

    it('应该返回"X天前"', () => {
      const date = new Date(Date.now() - 2 * 24 * 60 * 60 * 1000)
      expect(formatRelativeTime(date)).toBe('2天前')
    })

    it('应该返回完整日期对于超过7天的时间', () => {
      const date = new Date(Date.now() - 10 * 24 * 60 * 60 * 1000)
      const result = formatRelativeTime(date)
      expect(result).toMatch(/^\d{4}-\d{2}-\d{2}$/)
    })
  })

  describe('isToday', () => {
    it('应该正确判断今天', () => {
      const now = new Date()
      expect(isToday(now)).toBe(true)
    })

    it('应该正确判断不是今天', () => {
      const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000)
      expect(isToday(yesterday)).toBe(false)
    })
  })

  describe('isYesterday', () => {
    it('应该正确判断昨天', () => {
      const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000)
      expect(isYesterday(yesterday)).toBe(true)
    })

    it('应该正确判断不是昨天', () => {
      const now = new Date()
      expect(isYesterday(now)).toBe(false)
    })
  })
})
