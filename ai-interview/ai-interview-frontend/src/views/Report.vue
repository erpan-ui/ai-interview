<template>
  <div class="container">
    <div v-if="loading" class="loading">加载报告中...</div>

    <div v-else-if="report" style="max-width:700px;margin:30px auto">
      <!-- 总分 -->
      <div class="card score-card">
        <div class="score-circle">
          <span class="score-num">{{ data.overall_score }}</span>
          <span class="score-label">/10</span>
        </div>
        <div class="score-info">
          <h2>面试评估报告</h2>
          <p class="hire-rec" v-if="report.hire_recommendation">
            {{ report.hire_recommendation }}
          </p>
        </div>
      </div>

      <!-- 总结 -->
      <div class="card" style="margin-top:16px" v-if="report.summary">
        <h3 style="margin-bottom:10px">📝 总体评价</h3>
        <p style="font-size:14px;line-height:1.8;color:#374151">{{ report.summary }}</p>
      </div>

      <!-- 优势 & 不足 -->
      <div class="two-col" style="margin-top:16px">
        <div class="card" v-if="report.strengths?.length">
          <h3 style="margin-bottom:10px;color:#059669">✅ 优势</h3>
          <ul>
            <li v-for="(s, i) in report.strengths" :key="i">{{ s }}</li>
          </ul>
        </div>
        <div class="card" v-if="report.weaknesses?.length">
          <h3 style="margin-bottom:10px;color:#dc2626">⚠️ 不足</h3>
          <ul>
            <li v-for="(w, i) in report.weaknesses" :key="i">{{ w }}</li>
          </ul>
        </div>
      </div>

      <!-- 建议 -->
      <div class="card" style="margin-top:16px" v-if="report.suggestions?.length">
        <h3 style="margin-bottom:10px">💡 改进建议</h3>
        <ul>
          <li v-for="(s, i) in report.suggestions" :key="i">{{ s }}</li>
        </ul>
      </div>

      <!-- 各题得分 -->
      <div class="card" style="margin-top:16px" v-if="report.question_scores?.length">
        <h3 style="margin-bottom:12px">📊 各题得分</h3>
        <div v-for="(q, i) in report.question_scores" :key="i" class="q-score-item">
          <div class="q-score-header">
            <span class="q-index">Q{{ i + 1 }}</span>
            <span class="q-text">{{ q.question }}</span>
            <span class="q-score" :style="{ color: q.score >= 7 ? '#059669' : q.score >= 5 ? '#d97706' : '#dc2626' }">
              {{ q.score }}
            </span>
          </div>
          <div class="q-bar">
            <div class="q-bar-fill" :style="{ width: (q.score * 10) + '%', background: q.score >= 7 ? '#10b981' : q.score >= 5 ? '#f59e0b' : '#ef4444' }"></div>
          </div>
        </div>
      </div>

      <!-- 操作 -->
      <div style="text-align:center;margin-top:24px;margin-bottom:40px">
        <router-link to="/resume/upload" class="btn-primary" style="display:inline-block;padding:10px 24px;color:white;border-radius:8px;margin-right:12px">
          再来一次
        </router-link>
        <router-link to="/dashboard" class="btn-secondary" style="display:inline-block;padding:10px 24px;border-radius:8px">
          返回首页
        </router-link>
      </div>
    </div>

    <div v-else class="card" style="text-align:center;padding:60px;max-width:500px;margin:60px auto">
      <p>报告加载失败</p>
      <router-link to="/dashboard" style="margin-top:12px;display:inline-block">返回首页</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getReport } from '../api/interview'

const route = useRoute()
const interviewId = route.params.id
const data = ref(null)
const report = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await getReport(interviewId)
    data.value = res
    report.value = res.report || {}
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.loading {
  text-align: center;
  padding: 80px;
  color: #6b7280;
}
.score-card {
  display: flex;
  align-items: center;
  gap: 24px;
}
.score-circle {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.score-num {
  font-size: 32px;
  font-weight: 700;
  color: white;
}
.score-label {
  font-size: 14px;
  color: rgba(255,255,255,0.7);
}
.score-info h2 {
  font-size: 20px;
  margin-bottom: 4px;
}
.hire-rec {
  font-size: 14px;
  color: #6b7280;
  margin-top: 4px;
}
.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
ul {
  list-style: none;
  padding: 0;
}
ul li {
  font-size: 14px;
  line-height: 1.8;
  padding-left: 16px;
  position: relative;
}
ul li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #6b7280;
}
.q-score-item {
  margin-bottom: 14px;
}
.q-score-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
  font-size: 14px;
}
.q-index {
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 12px;
  color: #6b7280;
}
.q-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.q-score {
  font-weight: 700;
  font-size: 16px;
}
.q-bar {
  height: 6px;
  background: #f3f4f6;
  border-radius: 3px;
  overflow: hidden;
}
.q-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}
</style>
