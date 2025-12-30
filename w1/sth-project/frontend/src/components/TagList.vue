<template>
  <div class="tag-list">
    <div class="tag-list-header">
      <h3>标签管理</h3>
      <el-button type="primary" @click="handleCreate">新建标签</el-button>
    </div>

    <div class="tag-list-content">
      <el-empty v-if="!loading && tags.length === 0" description="暂无标签" />

      <div v-else class="tag-items">
        <div
          v-for="tag in tags"
          :key="tag.id"
          class="tag-item"
        >
          <tag-badge :tag="tag" />
          <div class="tag-item-actions">
            <el-button
              type="danger"
              size="small"
              text
              @click="handleDelete(tag)"
            >
              删除
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <el-dialog
      v-model="formVisible"
      :title="isEdit ? '编辑标签' : '新建标签'"
      width="400px"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="标签名" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入标签名"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="颜色" prop="color">
          <el-color-picker v-model="formData.color" />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="formVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import TagBadge from './TagBadge.vue'
import { useTagStore } from '@/stores/tag'
import type { Tag } from '@/types/tag'

const tagStore = useTagStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const formVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)

const tags = computed(() => tagStore.tags)

const formData = reactive<Partial<Tag>>({
  name: '',
  color: '#409EFF'
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入标签名', trigger: 'blur' },
    { min: 1, max: 50, message: '标签名长度为 1-50 个字符', trigger: 'blur' }
  ],
  color: [
    { required: true, message: '请选择颜色', trigger: 'change' }
  ]
}

async function loadTags() {
  loading.value = true
  try {
    await tagStore.fetchTags({ page: 1, page_size: 100 })
  } catch (error) {
    ElMessage.error('加载标签列表失败')
  } finally {
    loading.value = false
  }
}

function handleCreate() {
  isEdit.value = false
  formData.name = ''
  formData.color = '#409EFF'
  formVisible.value = true
}

async function handleDelete(tag: Tag) {
  try {
    await ElMessageBox.confirm(
      `确定要删除标签 "${tag.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await tagStore.deleteTag(tag.id)
    ElMessage.success('删除成功')
    loadTags()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

async function handleSubmit() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitting.value = true
    
    await tagStore.createTag({
      name: formData.name!,
      color: formData.color!
    })
    
    ElMessage.success('创建成功')
    formVisible.value = false
    loadTags()
  } catch (error) {
    console.error('表单验证失败', error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadTags()
})
</script>

<style scoped>
.tag-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tag-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tag-list-header h3 {
  margin: 0;
}

.tag-list-content {
  min-height: 200px;
}

.tag-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tag-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fff;
}

.tag-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
