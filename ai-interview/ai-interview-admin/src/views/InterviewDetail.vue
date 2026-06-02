<template>
  <div>
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
      <router-link to="/interviews" style="color:#6b7280;font-size:14px">← 返回列表</router-link>
      <h1 style="font-size:20px">面试详情 #{{ interviewId }}</h1>
    </div>

    <div v-if="loading" style="text-align:center;padding:60px;color:#6b7280">加载中...</div>

    <template v-else-if="detail">
      <!-- 基本信息 -->
      <div class="card" style="margin-bottom:16px">
        <div class="info-grid">
          <div><span class="info-label">目标岗位</span><span>{{ detail.target_position }}</span></div>
          <div><span class="info-label">难度</span><span>{{ diffMap[detail.difficulty] || detail.difficulty }}</span></div>
          <div><span class="info-label">题数</span><span>{{ detail.total_questions }}</span></div>
          <div><span class="info-label">综合得分</span><span style="font-weight:700;color:#4f46e5">{{ detail.overall_score || '-' }}</span></div>
          <div><span class="info-label">状态</span><span :class="['badge', detail.status === 'completed' ? 'badge-green' : 'badge-yellow']">{{ detail.status === 'completed' ? '已完成' : '进行中' }}</span></div>
        </div>
      </div>

      <!-- 报告 -->
      <div class="card" style="margin-bottom:16px" v-if="detail.report?.summary">
        <h3 style="margin-bottom:12px">📝 评估报告</h3>
        <p style="font-size:14px;line-height:1.8;margin-bottom:12px">{{ detail.report.summary }}</p>
        <div class="report-cols" v-if="detail.report.strengths || detail.report.weaknesses">
          <div v-if="detail.report.strengths?.length">
            <h4 style="color:#059669;margin-bottom:6px">优势</h4>
            <ul><li v-for="s in detail.report.strengths" :key="s">{{ s }}</li></ul>
          </div>
          <div v-if="detail.report.weaknesses?.length">
            <h4 style="color:#dc2626;margin-bottom:6px">不足</h4>
            <ul><li v-for="w in detail.report.weaknesses" :key="w">{{ w }}</li></ul>
          </div>
        </div>
      </div>

      <!-- 对话记录 -->
      <div class="card">
        <h3 style="margin-bottom:16px">💬 对话记录</h3>
        <div v-for="m in detail.messages" :key="m.id" :class="['msg', m.role]">
          <div class="msg-role">{{ m.role === 'interviewer' ? '🤖 面试官' : '👤 候选人' }}</div>
          <div class="msg-content">{{ m.content }}</div>
          <div v-if="m.score" class="msg-score">
            评分: {{ m.score }}/10
            <span v-if="m.feedback"> | {{ m.feedback }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { interviewApi } from '../api'

const route = useRoute()
const interviewId = route.params.id
const detail = ref(null)
const loading = ref(true)
const diffMap = { easy: '简单', medium: '中等', hard: '困难' }

onMounted(async () => {
  try {
    detail.value = await interviewApi.detail(interviewId)
  } catch (e) { console.error(e) }
  finally { loading.value = false }
})
</script>

<style scoped>
.info-grid { display: flex; gap: 32px; flex-wrap: wrap; }
.info-grid > div { display: flex; flex-direction: column; gap: 4px; }
.info-label { font-size: 12px; color: #6b7280; }
.report-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.report-cols ul { list-style: none; padding: 0; }
.report-cols li { font-size: 13px; line-height: 1.8; padding-left: 14px; position: relative; }
.report-cols li::before { content: '•'; position: absolute; left: 0; color: #9ca3af; }
.msg { margin-bottom: 16px; padding: 12px; border-radius: 8px; }
.msg.interviewer { background: #f9fafb; }
.msg.candidate { background: #eef2ff; }
.msg-role { font-size: 12px; font-weight: 600; color: #6b7280; margin-bottom: 6px; }
.msg-content { font-size: 14px; line-height: 1.7; }
.msg-score { margin-top: 8px; font-size: 12px; color: #4f46e5; font-weight: 500; }
</style>
