/**
 * Tag Store
 * 管理 Tag 相关的状态和操作
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Tag, TagCreate } from '@/types'
import * as tagApi from '@/api/tags'
import type { PaginationParams } from '@/types'

export const useTagStore = defineStore('tag', () => {
  const tags = ref<Tag[]>([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const tagMap = computed(() => {
    const map = new Map<string, Tag>()
    tags.value.forEach(tag => map.set(tag.id, tag))
    return map
  })

  /**
   * 获取 Tag 列表
   */
  async function fetchTags(params?: PaginationParams) {
    loading.value = true
    error.value = null
    try {
      const response = await tagApi.getTags(params)
      if (response.code === 200 && response.data) {
        tags.value = response.data.tags
        total.value = response.data.total
      }
    } catch (e: any) {
      error.value = e.message || '获取 Tag 列表失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建 Tag
   */
  async function createTag(data: TagCreate) {
    loading.value = true
    error.value = null
    try {
      const response = await tagApi.createTag(data)
      if (response.code === 200) {
        await fetchTags()
      }
    } catch (e: any) {
      error.value = e.message || '创建 Tag 失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除 Tag
   */
  async function deleteTag(id: string) {
    loading.value = true
    error.value = null
    try {
      const response = await tagApi.deleteTag(id)
      if (response.code === 200) {
        tags.value = tags.value.filter(t => t.id !== id)
        total.value -= 1
      }
    } catch (e: any) {
      error.value = e.message || '删除 Tag 失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 根据 ID 获取 Tag
   */
  function getTagById(id: string): Tag | undefined {
    return tagMap.value.get(id)
  }

  return {
    tags,
    total,
    loading,
    error,
    tagMap,
    fetchTags,
    createTag,
    deleteTag,
    getTagById
  }
})
