<template>
  <div class="container">
    <div class="page-header">
      <h1>📋 面试记录</h1>
      <router-link to="/resume/upload" class="btn-primary" style="display:inline-block;padding:10px 24px;color:white;border-radius:8px">
        + 开始新面试
      </router-link>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="interviews.length === 0" class="empty card">
      <p style="font-size:48px;margin-bottom:12px">🎯</p>
      <p>还没有面试记录</p>
      <p style="color:#6b7280;font-size:14px;margin-top:8px">上传简历开始你的第一次 AI 模拟面试</p>
    </div>

    <div v-else class="interview-list">
      <div v-for="item in interviews" :key="item.interview_id" class="card interview-item">
        <div class="item-header">
          <span class="position">{{ item.target_position }}</span>
          <span :class="['status', item.status]">{{ item.status === 'completed' ? '已完成' : '进行中' }}</span>
        </div>
        <div class="item-meta">
          <span>难度：{{ difficultyMap[item.difficulty] || item.difficulty }}</span>
          <span>题数：{{ item.total_questions }}</span>
          <span v-if="item.overall_score">得分：{{ item.overall_score }}</span>
          <span>{{ formatDate(item.created_at) }}</span>
        </div>
        <div class="item-actions">
          <router-link v-if="item.status === 'in_progress'" :to="`/interview/${item.interview_id}`" class="btn-primary" style="padding:6px 16px;font-size:13px;color:white;display:inline-block;border-radius:6px">
            继续面试
          </router-link>
          <router-link v-else :to="`/interview/${item.interview_id}/report`" class="btn-secondary" style="padding:6px 16px;font-size:13px;display:inline-block;border-radius:6px">
            查看报告
          </router-link>
          <button class="btn-danger" style="padding:6px 16px;font-size:13px;border-radius:6px" @click="handleDelete(item.interview_id)">
            删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getInterviews, deleteInterview } from '../api/interview'

const interviews = ref([])
const loading = ref(true)
const difficultyMap = { easy: '简单', medium: '中等', hard: '困难' }

function formatDate(str) {
  if (!str) return ''
  return new Date(str).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

onMounted(async () => {
  try {
    const data = await getInterviews()
    interviews.value = data.items || []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

async function handleDelete(interviewId) {
  if (!confirm('确定要删除这条面试记录吗？删除后无法恢复。')) return
  try {
    await deleteInterview(interviewId)
    interviews.value = interviews.value.filter(i => i.interview_id !== interviewId)
  } catch (e) {
    alert('删除失败: ' + e.message)
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 0;
}
.page-header h1 {
  font-size: 22px;
}
.loading, .empty {
  text-align: center;
  padding: 60px 20px;
}
.interview-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.interview-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.position {
  font-weight: 600;
  font-size: 16px;
}
.status {
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 12px;
}
.status.completed {
  background: #d1fae5;
  color: #065f46;
}
.status.in_progress {
  background: #fef3c7;
  color: #92400e;
}
.item-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #6b7280;
}
.item-actions {
  display: flex;
  gap: 8px;
}
.btn-danger {
  background: #ef4444;
  color: white;
}
.btn-danger:hover {
  background: #dc2626;
}
</style>
