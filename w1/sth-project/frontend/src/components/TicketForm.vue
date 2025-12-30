<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑 Ticket' : '新建 Ticket'"
    width="600px"
    @update:model-value="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="80px"
    >
      <el-form-item label="标题" prop="title">
        <el-input
          v-model="formData.title"
          placeholder="请输入 Ticket 标题"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="描述" prop="description">
        <el-input
          v-model="formData.description"
          type="textarea"
          placeholder="请输入 Ticket 描述"
          :rows="4"
          maxlength="2000"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="标签" prop="tag_ids">
        <tag-select
          v-model="formData.tag_ids"
          :tags="tags"
          placeholder="选择标签"
          multiple
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="状态" prop="is_completed">
        <el-switch
          v-model="formData.is_completed"
          active-text="已完成"
          inactive-text="进行中"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import TagSelect from './TagSelect.vue'
import { useTagStore } from '@/stores/tag'
import type { Ticket, Tag } from '@/types'

interface Props {
  visible: boolean
  ticket?: Ticket | null
}

interface Emits {
  (e: 'update:visible', visible: boolean): void
  (e: 'submit', ticket: Partial<Ticket>): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const tagStore = useTagStore()
const formRef = ref<FormInstance>()
const submitting = ref(false)

const isEdit = computed(() => !!props.ticket)

const formData = reactive<Partial<Ticket>>({
  title: '',
  description: '',
  tag_ids: [],
  is_completed: false
})

const rules: FormRules = {
  title: [
    { required: true, message: '请输入 Ticket 标题', trigger: 'blur' },
    { min: 1, max: 200, message: '标题长度为 1-200 个字符', trigger: 'blur' }
  ]
}

const tags = computed(() => tagStore.tags)

watch(
  () => props.ticket,
  (ticket) => {
    if (ticket) {
      formData.title = ticket.title
      formData.description = ticket.description || ''
      formData.tag_ids = ticket.tags?.map(t => t.id) || []
      formData.is_completed = ticket.is_completed
    } else {
      formData.title = ''
      formData.description = ''
      formData.tag_ids = []
      formData.is_completed = false
    }
  },
  { immediate: true }
)

watch(
  () => props.visible,
  (visible) => {
    if (visible) {
      tagStore.fetchTags({ page: 1, page_size: 100 })
    }
  }
)

function handleClose() {
  emit('update:visible', false)
  formRef.value?.resetFields()
}

async function handleSubmit() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitting.value = true
    
    const submitData: Partial<Ticket> = {
      title: formData.title,
      description: formData.description,
      tag_ids: formData.tag_ids,
      is_completed: formData.is_completed
    }
    
    emit('submit', submitData)
  } catch (error) {
    console.error('表单验证失败', error)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
