import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTagStore } from '@/stores/tag'
import { tagApi } from '@/api/tags'

vi.mock('@/api/tags')

describe('useTagStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('fetchTags', () => {
    it('应该成功获取 Tag 列表', async () => {
      const mockResponse = {
        code: 200,
        data: {
          tags: [
            {
              id: '1',
              name: 'Test Tag',
              color: '#FF0000',
              created_at: '2024-01-01T00:00:00Z',
              updated_at: '2024-01-01T00:00:00Z'
            }
          ],
          total: 1
        }
      }

      vi.mocked(tagApi.getTags).mockResolvedValue(mockResponse)

      const store = useTagStore()
      await store.fetchTags({ page: 1, page_size: 20 })

      expect(store.tags).toEqual(mockResponse.data.tags)
      expect(store.total).toBe(mockResponse.data.total)
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
    })

    it('应该处理获取失败的情况', async () => {
      const mockError = new Error('获取失败')
      vi.mocked(tagApi.getTags).mockRejectedValue(mockError)

      const store = useTagStore()
      
      await expect(store.fetchTags()).rejects.toThrow('获取失败')
      expect(store.error).toBe('获取失败')
      expect(store.loading).toBe(false)
    })
  })

  describe('createTag', () => {
    it('应该成功创建 Tag', async () => {
      const mockTag = {
        id: '2',
        name: 'New Tag',
        color: '#00FF00',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      }

      const mockResponse = {
        code: 200,
        data: mockTag
      }

      vi.mocked(tagApi.createTag).mockResolvedValue(mockResponse)

      const store = useTagStore()
      await store.createTag({
        name: 'New Tag',
        color: '#00FF00'
      })

      expect(store.tags).toContainEqual(mockTag)
    })
  })

  describe('deleteTag', () => {
    it('应该成功删除 Tag', async () => {
      const mockResponse = {
        code: 200,
        data: null
      }

      vi.mocked(tagApi.deleteTag).mockResolvedValue(mockResponse)

      const store = useTagStore()
      store.tags = [
        {
          id: '1',
          name: 'Test Tag',
          color: '#FF0000',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      ]

      await store.deleteTag('1')

      expect(store.tags).toHaveLength(0)
    })
  })

  describe('getTagById', () => {
    it('应该返回指定 ID 的 Tag', () => {
      const store = useTagStore()
      store.tags = [
        {
          id: '1',
          name: 'Test Tag',
          color: '#FF0000',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      ]

      const tag = store.getTagById('1')
      expect(tag).toEqual(store.tags[0])
    })

    it('应该返回 undefined 如果 Tag 不存在', () => {
      const store = useTagStore()
      store.tags = []

      const tag = store.getTagById('1')
      expect(tag).toBeUndefined()
    })
  })

  describe('tagMap', () => {
    it('应该返回 Tag ID 到 Tag 的映射', () => {
      const store = useTagStore()
      store.tags = [
        {
          id: '1',
          name: 'Tag 1',
          color: '#FF0000',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        },
        {
          id: '2',
          name: 'Tag 2',
          color: '#00FF00',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      ]

      expect(store.tagMap.size).toBe(2)
      expect(store.tagMap.get('1')?.name).toBe('Tag 1')
      expect(store.tagMap.get('2')?.name).toBe('Tag 2')
    })
  })
})
