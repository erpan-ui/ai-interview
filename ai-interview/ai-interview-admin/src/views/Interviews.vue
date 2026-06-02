<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
      <h1 style="font-size:20px">🎤 面试记录</h1>
      <select v-model="statusFilter" @change="page = 1; loadInterviews()" style="width:140px">
        <option value="">全部状态</option>
        <option value="in_progress">进行中</option>
        <option value="completed">已完成</option>
      </select>
    </div>

    <div class="card">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>用户</th>
            <th>目标岗位</th>
            <th>难度</th>
            <th>题数</th>
            <th>得分</th>
            <th>状态</th>
            <th>时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="i in interviews" :key="i.id">
            <td>{{ i.id }}</td>
            <td>{{ i.user_email }}</td>
            <td>{{ i.target_position }}</td>
            <td>{{ diffMap[i.difficulty] || i.difficulty }}</td>
            <td>{{ i.total_questions }}</td>
            <td>
              <span v-if="i.overall_score" :style="{ color: i.overall_score >= 7 ? '#059669' : i.overall_score >= 5 ? '#d97706' : '#dc2626', fontWeight: 600 }">
                {{ i.overall_score }}
              </span>
              <span v-else style="color:#9ca3af">-</span>
            </td>
            <td><span :class="['badge', i.status === 'completed' ? 'badge-green' : 'badge-yellow']">{{ i.status === 'completed' ? '已完成' : '进行中' }}</span></td>
            <td>{{ formatDate(i.created_at) }}</td>
            <td>
              <router-link :to="`/interviews/${i.id}`" class="btn-primary btn-sm" style="color:white;display:inline-block">详情</router-link>
              <button class="btn-danger btn-sm" style="margin-left:6px" @click="handleDelete(i.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="pagination" v-if="total > perPage">
        <button class="btn-sm" :disabled="page <= 1" @click="page--; loadInterviews()">上一页</button>
        <span>{{ page }} / {{ Math.ceil(total / perPage) }}</span>
        <button class="btn-sm" :disabled="page >= Math.ceil(total / perPage)" @click="page++; loadInterviews()">下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { interviewApi } from '../api'

const interviews = ref([])
const total = ref(0)
const page = ref(1)
const perPage = 20
const statusFilter = ref('')
const diffMap = { easy: '简单', medium: '中等', hard: '困难' }

function formatDate(str) {
  if (!str) return ''
  return new Date(str).toLocaleString('zh-CN')
}

async function loadInterviews() {
  try {
    const data = await interviewApi.list({ page: page.value, per_page: perPage, status: statusFilter.value || undefined })
    interviews.value = data.items
    total.value = data.total
  } catch (e) { console.error(e) }
}

async function handleDelete(id) {
  if (!confirm('确定要删除这条面试记录吗？')) return
  try {
    await interviewApi.delete(id)
    await loadInterviews()
  } catch (e) { alert('删除失败: ' + e.message) }
}

onMounted(loadInterviews)
</script>

<style scoped>
.pagination { display: flex; align-items: center; justify-content: center; gap: 16px; padding: 16px 0 0; font-size: 13px; color: #6b7280; }
</style>
