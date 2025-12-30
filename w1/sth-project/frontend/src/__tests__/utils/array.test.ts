import { describe, it, expect } from 'vitest'
import {
  unique,
  groupBy,
  sortBy,
  chunk,
  flatten,
  difference,
  intersection,
  union,
  shuffle,
  sum,
  average,
  max,
  min,
  paginate
} from '@/utils/array'

describe('array utils', () => {
  describe('unique', () => {
    it('应该去重数组', () => {
      expect(unique([1, 2, 2, 3, 3, 3])).toEqual([1, 2, 3])
    })

    it('应该基于键去重对象数组', () => {
      const arr = [
        { id: 1, name: 'A' },
        { id: 2, name: 'B' },
        { id: 1, name: 'A' }
      ]
      expect(unique(arr, 'id')).toEqual([
        { id: 1, name: 'A' },
        { id: 2, name: 'B' }
      ])
    })
  })

  describe('groupBy', () => {
    it('应该按指定键分组', () => {
      const arr = [
        { type: 'A', value: 1 },
        { type: 'A', value: 2 },
        { type: 'B', value: 3 }
      ]
      const result = groupBy(arr, 'type')
      expect(result['A']).toHaveLength(2)
      expect(result['B']).toHaveLength(1)
    })
  })

  describe('sortBy', () => {
    it('应该按指定键升序排序', () => {
      const arr = [
        { id: 3, name: 'C' },
        { id: 1, name: 'A' },
        { id: 2, name: 'B' }
      ]
      const result = sortBy(arr, 'id', 'asc')
      expect(result[0].id).toBe(1)
      expect(result[2].id).toBe(3)
    })

    it('应该按指定键降序排序', () => {
      const arr = [
        { id: 1, name: 'A' },
        { id: 3, name: 'C' },
        { id: 2, name: 'B' }
      ]
      const result = sortBy(arr, 'id', 'desc')
      expect(result[0].id).toBe(3)
      expect(result[2].id).toBe(1)
    })
  })

  describe('chunk', () => {
    it('应该分块数组', () => {
      expect(chunk([1, 2, 3, 4, 5], 2)).toEqual([[1, 2], [3, 4], [5]])
    })
  })

  describe('flatten', () => {
    it('应该扁平化数组', () => {
      expect(flatten([1, [2, [3, 4]]])).toEqual([1, 2, [3, 4]])
      expect(flatten([1, [2, [3, 4]]], 2)).toEqual([1, 2, 3, 4])
    })
  })

  describe('difference', () => {
    it('应该返回差集', () => {
      expect(difference([1, 2, 3], [2, 3, 4])).toEqual([1])
    })
  })

  describe('intersection', () => {
    it('应该返回交集', () => {
      expect(intersection([1, 2, 3], [2, 3, 4])).toEqual([2, 3])
    })
  })

  describe('union', () => {
    it('应该返回并集', () => {
      expect(union([1, 2], [2, 3])).toEqual([1, 2, 3])
    })
  })

  describe('shuffle', () => {
    it('应该打乱数组', () => {
      const arr = [1, 2, 3, 4, 5]
      const shuffled = shuffle(arr)
      expect(shuffled).toHaveLength(5)
      expect(shuffled).toEqual(expect.arrayContaining(arr))
    })
  })

  describe('sum', () => {
    it('应该计算数组和', () => {
      expect(sum([1, 2, 3, 4, 5])).toBe(15)
    })

    it('应该基于键计算对象数组和', () => {
      const arr = [{ value: 1 }, { value: 2 }, { value: 3 }]
      expect(sum(arr, 'value')).toBe(6)
    })
  })

  describe('average', () => {
    it('应该计算数组平均值', () => {
      expect(average([1, 2, 3, 4, 5])).toBe(3)
    })

    it('应该处理空数组', () => {
      expect(average([])).toBe(0)
    })
  })

  describe('max', () => {
    it('应该返回最大值', () => {
      expect(max([1, 2, 3, 4, 5])).toBe(5)
    })

    it('应该基于键返回对象数组最大值', () => {
      const arr = [{ value: 1 }, { value: 3 }, { value: 2 }]
      expect(max(arr, 'value')).toEqual({ value: 3 })
    })
  })

  describe('min', () => {
    it('应该返回最小值', () => {
      expect(min([1, 2, 3, 4, 5])).toBe(1)
    })

    it('应该基于键返回对象数组最小值', () => {
      const arr = [{ value: 1 }, { value: 3 }, { value: 2 }]
      expect(min(arr, 'value')).toEqual({ value: 1 })
    })
  })

  describe('paginate', () => {
    it('应该分页数组', () => {
      const arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
      const result = paginate(arr, 2, 3)
      expect(result.data).toEqual([4, 5, 6])
      expect(result.total).toBe(10)
      expect(result.page).toBe(2)
      expect(result.pageSize).toBe(3)
      expect(result.totalPages).toBe(4)
    })
  })
})
