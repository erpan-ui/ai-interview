<template>
  <div class="container">
    <div class="card" style="max-width:600px;margin:40px auto">
      <h2 style="margin-bottom:20px">📄 上传简历 & 开始面试</h2>

      <!-- Step 1: 上传简历 -->
      <div v-if="step === 1">
        <div class="form-group">
          <label>上传简历 (PDF)</label>
          <div class="upload-area" @click="$refs.fileInput.click()" @dragover.prevent @drop.prevent="onDrop">
            <input ref="fileInput" type="file" accept=".pdf" @change="onFileChange" hidden />
            <p v-if="!file" style="color:#6b7280">点击或拖拽上传 PDF 简历</p>
            <p v-else>📎 {{ file.name }}</p>
          </div>
        </div>
        <div class="form-group">
          <label>目标岗位</label>
          <input v-model="targetPosition" placeholder="例如：Python后端开发工程师" />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button class="btn-primary" style="width:100%" @click="handleUpload" :disabled="!file || uploading">
          {{ uploading ? '上传中...' : '上传并解析简历' }}
        </button>
      </div>

      <!-- Step 1.5: 解析动画 -->
      <div v-if="step === 'parsing'" class="parsing-stage">
        <div class="parsing-icon">🔍</div>
        <h3>{{ parsingTitle }}</h3>
        <div class="progress-bar-wrapper">
          <div class="progress-bar" :style="{ width: progress + '%' }"></div>
        </div>
        <p class="progress-text">{{ progress }}%</p>
        <div class="tips-area">
          <transition name="tip-fade" mode="out-in">
            <p class="tip-text" :key="currentTip">💡 {{ currentTip }}</p>
          </transition>
        </div>
      </div>

      <!-- Step 2: 解析结果 + 简历分析 + 面试配置 -->
      <div v-if="step === 2">
        <div class="parsed-info card" style="background:#f9fafb;margin-bottom:20px">
          <h3 style="margin-bottom:12px">✅ 简历解析完成</h3>
          <div v-if="parsedContent">
            <p v-if="parsedContent.name"><strong>姓名：</strong>{{ parsedContent.name }}</p>
            <p v-if="parsedContent.education"><strong>学历：</strong>{{ parsedContent.education }}</p>
            <p v-if="parsedContent.skills?.length"><strong>技能：</strong>{{ parsedContent.skills.join('、') }}</p>
            <p v-if="parsedContent.summary"><strong>概述：</strong>{{ parsedContent.summary }}</p>
          </div>
        </div>

        <!-- 简历分析报告 -->
        <div v-if="analysis" class="card analysis-card" style="margin-bottom:20px">
          <h3 style="margin-bottom:14px">📊 简历分析报告</h3>
          <div class="analysis-score" v-if="analysis.overall_score">
            <div class="score-badge" :style="{ background: scoreColor(analysis.overall_score) }">
              {{ analysis.overall_score }}
            </div>
            <span class="score-text">简历综合评分</span>
          </div>
          <p v-if="analysis.summary" class="analysis-summary">{{ analysis.summary }}</p>
          <div class="analysis-section" v-if="analysis.keyword_match?.length">
            <h4>🎯 匹配技能</h4>
            <div class="tag-list">
              <span v-for="k in analysis.keyword_match" :key="k" class="tag tag-green">{{ k }}</span>
            </div>
          </div>
          <div class="analysis-section" v-if="analysis.missing_keywords?.length">
            <h4>⚠️ 缺少技能</h4>
            <div class="tag-list">
              <span v-for="k in analysis.missing_keywords" :key="k" class="tag tag-red">{{ k }}</span>
            </div>
          </div>
          <div class="analysis-two-col">
            <div v-if="analysis.strengths?.length">
              <h4 style="color:#059669;margin-bottom:8px">✅ 优势</h4>
              <ul><li v-for="(s, i) in analysis.strengths" :key="i">{{ s }}</li></ul>
            </div>
            <div v-if="analysis.weaknesses?.length">
              <h4 style="color:#dc2626;margin-bottom:8px">❌ 不足</h4>
              <ul><li v-for="(w, i) in analysis.weaknesses" :key="i">{{ w }}</li></ul>
            </div>
          </div>
          <div class="analysis-section" v-if="analysis.suggestions?.length">
            <h4>💡 改进建议</h4>
            <ul><li v-for="(s, i) in analysis.suggestions" :key="i">{{ s }}</li></ul>
          </div>
        </div>

        <div class="form-group">
          <label>面试难度</label>
          <select v-model="difficulty">
            <option value="easy">简单 - 基础知识</option>
            <option value="medium">中等 - 技术深度</option>
            <option value="hard">困难 - 系统设计</option>
          </select>
        </div>
        <div class="form-group">
          <label>题目数量</label>
          <select v-model.number="totalQuestions">
            <option :value="3">3 题（快速模式）</option>
            <option :value="5">5 题（标准模式）</option>
            <option :value="8">8 题（深度模式）</option>
          </select>
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button class="btn-primary" style="width:100%" @click="handleStart" :disabled="starting">
          {{ starting ? '生成面试题中...' : '🚀 开始面试' }}
        </button>
      </div>

      <!-- Step 3: 面试准备动画 -->
      <div v-if="step === 'starting'" class="parsing-stage">
        <div class="ai-face-anim">
          <svg viewBox="0 0 80 80" width="80" height="80">
            <circle cx="40" cy="40" r="38" fill="white" stroke="#4f46e5" stroke-width="2"/>
            <ellipse cx="28" cy="36" rx="5" ry="6" fill="#1e1e1e">
              <animate attributeName="ry" values="6;1;6" dur="2s" repeatCount="indefinite"/>
            </ellipse>
            <ellipse cx="52" cy="36" rx="5" ry="6" fill="#1e1e1e">
              <animate attributeName="ry" values="6;1;6" dur="2s" repeatCount="indefinite"/>
            </ellipse>
            <path d="M30 52 Q40 60 50 52" stroke="#1e1e1e" stroke-width="2" fill="none" stroke-linecap="round"/>
          </svg>
        </div>
        <h3>{{ startingTitle }}</h3>
        <div class="progress-bar-wrapper">
          <div class="progress-bar" :style="{ width: startProgress + '%' }"></div>
        </div>
        <p class="progress-text">{{ startProgress }}%</p>
        <div class="tips-area">
          <transition name="tip-fade" mode="out-in">
            <p class="tip-text" :key="startTip">💡 {{ startTip }}</p>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { uploadResume, getResume } from '../api/resume'
import { startInterview } from '../api/interview'

const router = useRouter()
const step = ref(1)
const file = ref(null)
const targetPosition = ref('Python后端开发工程师')
const difficulty = ref('medium')
const totalQuestions = ref(5)
const uploading = ref(false)
const starting = ref(false)
const error = ref('')
const resumeId = ref(null)
const parsedContent = ref(null)
const analysis = ref(null)

// 解析动画相关
const progress = ref(0)
const parsingTitle = ref('正在上传简历...')
const currentTip = ref('')
let tipTimer = null
let progressTimer = null

const tips = [
  '面试前深呼吸，保持自信和冷静',
  '回答问题时用 STAR 法则：情境、任务、行动、结果',
  '不会的问题坦诚说不会，展示学习意愿比硬编更好',
  '准备好自我介绍，控制在1-2分钟',
  '技术面试中，思路比答案更重要',
  '项目经验要突出你的贡献和技术选型理由',
  '遇到算法题先理清思路再写代码',
  '面试官问"还有什么问题"时，准备2-3个有深度的问题',
  '简历上写的每个技术点都要能展开讲',
  '注意沟通表达，逻辑清晰比语速快更重要',
  '了解目标公司的业务和技术栈，展示你的诚意',
  '手撕代码时先写伪代码，再逐步实现',
  '系统设计题从需求分析开始，逐步细化',
  '准备几个你在项目中解决的难题案例',
  '面试结束后及时复盘，记录不足之处'
]

function startTipRotation() {
  currentTip.value = tips[Math.floor(Math.random() * tips.length)]
  tipTimer = setInterval(() => {
    let next
    do { next = tips[Math.floor(Math.random() * tips.length)] } while (next === currentTip.value)
    currentTip.value = next
  }, 3000)
}

function startProgressAnimation() {
  progress.value = 0
  const stages = [
    { target: 15, speed: 200, title: '正在上传简历...' },
    { target: 35, speed: 300, title: '正在提取文本内容...' },
    { target: 60, speed: 400, title: 'AI 正在解析简历...' },
    { target: 80, speed: 500, title: 'AI 正在分析简历质量...' },
    { target: 92, speed: 800, title: '即将完成...' }
  ]
  let stageIdx = 0

  function tick() {
    if (stageIdx >= stages.length) return
    const stage = stages[stageIdx]
    if (progress.value < stage.target) {
      progress.value++
      parsingTitle.value = stage.title
      progressTimer = setTimeout(tick, stage.speed)
    } else {
      stageIdx++
      tick()
    }
  }
  tick()
}

function stopAnimations() {
  if (tipTimer) { clearInterval(tipTimer); tipTimer = null }
  if (progressTimer) { clearTimeout(progressTimer); progressTimer = null }
}

onUnmounted(() => {
  stopAnimations()
  stopStartingAnimation()
})

function onFileChange(e) { file.value = e.target.files[0] }
function onDrop(e) {
  const f = e.dataTransfer.files[0]
  if (f && f.name.endsWith('.pdf')) file.value = f
}

async function handleUpload() {
  error.value = ''
  uploading.value = true
  try {
    // 切换到解析动画
    step.value = 'parsing'
    startTipRotation()
    startProgressAnimation()

    const data = await uploadResume(file.value, targetPosition.value)
    resumeId.value = data.resume_id

    // 轮询等待解析完成
    let retries = 0
    while (retries < 30) {
      await new Promise(r => setTimeout(r, 2000))
      const detail = await getResume(resumeId.value)
      if (detail.status === 'completed') {
        parsedContent.value = detail.parsed_content
        analysis.value = detail.analysis
        // 完成动画
        progress.value = 100
        parsingTitle.value = '解析完成！'
        await new Promise(r => setTimeout(r, 600))
        stopAnimations()
        step.value = 2
        return
      }
      if (detail.status === 'failed') {
        throw new Error('简历解析失败，请重试')
      }
      retries++
    }
    throw new Error('解析超时，请重试')
  } catch (e) {
    stopAnimations()
    error.value = e.message
    step.value = 1
  } finally {
    uploading.value = false
  }
}

function scoreColor(score) {
  if (score >= 7) return '#10b981'
  if (score >= 5) return '#f59e0b'
  return '#ef4444'
}

// 面试准备动画
const startProgress = ref(0)
const startingTitle = ref('AI 面试即将开始，请做好准备')
const startTip = ref('')
let startTipTimer = null
let startProgressTimer = null

const startTips = [
  '深呼吸，保持冷静自信 💪',
  '回答时尽量结合你的项目经验',
  '思路比答案更重要，先理清再作答',
  '不会的问题坦诚说不会，展示学习意愿',
  '自我介绍控制在1-2分钟',
  '注意条理清晰，分点作答效果更好'
]

function startStartingAnimation() {
  startProgress.value = 0
  startTip.value = startTips[0]
  let tipIdx = 0
  startTipTimer = setInterval(() => {
    tipIdx = (tipIdx + 1) % startTips.length
    startTip.value = startTips[tipIdx]
  }, 2000)

  const stages = [
    { target: 30, speed: 150, title: 'AI 面试即将开始，请做好准备' },
    { target: 60, speed: 200, title: 'AI 正在生成面试题目...' },
    { target: 85, speed: 350, title: '正在根据你的简历定制题目...' },
    { target: 95, speed: 600, title: '即将开始...' }
  ]
  let stageIdx = 0

  function tick() {
    if (stageIdx >= stages.length) return
    const stage = stages[stageIdx]
    if (startProgress.value < stage.target) {
      startProgress.value++
      startingTitle.value = stage.title
      startProgressTimer = setTimeout(tick, stage.speed)
    } else {
      stageIdx++
      tick()
    }
  }
  tick()
}

function stopStartingAnimation() {
  if (startTipTimer) { clearInterval(startTipTimer); startTipTimer = null }
  if (startProgressTimer) { clearTimeout(startProgressTimer); startProgressTimer = null }
}

async function handleStart() {
  error.value = ''
  starting.value = true
  step.value = 'starting'
  startStartingAnimation()

  try {
    const data = await startInterview({
      resume_id: resumeId.value,
      target_position: targetPosition.value,
      difficulty: difficulty.value,
      total_questions: totalQuestions.value
    })
    // 完成动画
    startProgress.value = 100
    startingTitle.value = '面试准备完成！'
    stopStartingAnimation()
    await new Promise(r => setTimeout(r, 800))
    router.push(`/interview/${data.interview_id}`)
  } catch (e) {
    stopStartingAnimation()
    error.value = e.message
    step.value = 2
  } finally {
    starting.value = false
  }
}
</script>

<style scoped>
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-size: 14px; font-weight: 500; color: #374151; }
.upload-area {
  border: 2px dashed #d1d5db; border-radius: 8px; padding: 40px;
  text-align: center; cursor: pointer; transition: border-color 0.2s;
}
.upload-area:hover { border-color: #4f46e5; }
.error { color: #ef4444; font-size: 13px; margin-bottom: 12px; }
.parsed-info p { font-size: 14px; margin-bottom: 6px; line-height: 1.6; }

/* 解析动画 */
.parsing-stage { text-align: center; padding: 30px 0; }
.parsing-icon { font-size: 48px; margin-bottom: 16px; animation: pulse 1.5s ease-in-out infinite; }
.ai-face-anim { margin-bottom: 16px; animation: faceFloat 2s ease-in-out infinite; }
@keyframes faceFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}
@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.15); opacity: 0.7; }
}
.parsing-stage h3 { font-size: 16px; color: #374151; margin-bottom: 20px; }
.progress-bar-wrapper {
  width: 100%; height: 8px; background: #e5e7eb; border-radius: 4px; overflow: hidden; margin-bottom: 8px;
}
.progress-bar {
  height: 100%; border-radius: 4px; transition: width 0.3s ease;
  background: linear-gradient(90deg, #4f46e5, #7c3aed, #a78bfa);
  background-size: 200% 100%;
  animation: shimmer 2s linear infinite;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
.progress-text { font-size: 13px; color: #6b7280; margin-bottom: 24px; }
.tips-area {
  min-height: 50px; display: flex; align-items: center; justify-content: center;
  background: #f9fafb; border-radius: 10px; padding: 14px 20px;
}
.tip-text { font-size: 13px; color: #4b5563; line-height: 1.6; margin: 0; }
.tip-fade-enter-active, .tip-fade-leave-active { transition: all 0.4s ease; }
.tip-fade-enter-from { opacity: 0; transform: translateY(8px); }
.tip-fade-leave-to { opacity: 0; transform: translateY(-8px); }

/* 分析报告 */
.analysis-card { border: 1px solid #e5e7eb; }
.analysis-score { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
.score-badge {
  width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center;
  justify-content: center; color: white; font-size: 18px; font-weight: 700;
}
.score-text { font-size: 14px; color: #6b7280; }
.analysis-summary {
  font-size: 14px; line-height: 1.8; color: #374151; margin-bottom: 16px;
  padding: 10px 14px; background: #f9fafb; border-radius: 8px;
}
.analysis-section { margin-bottom: 14px; }
.analysis-section h4 { font-size: 14px; margin-bottom: 8px; color: #374151; }
.tag-list { display: flex; flex-wrap: wrap; gap: 8px; }
.tag { padding: 3px 10px; border-radius: 12px; font-size: 12px; }
.tag-green { background: #d1fae5; color: #065f46; }
.tag-red { background: #fee2e2; color: #991b1b; }
.analysis-two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 14px; }
.analysis-two-col ul, .analysis-section ul { list-style: none; padding: 0; }
.analysis-two-col li, .analysis-section li {
  font-size: 13px; line-height: 1.8; padding-left: 14px; position: relative;
}
.analysis-two-col li::before, .analysis-section li::before {
  content: '•'; position: absolute; left: 0; color: #9ca3af;
}
</style>
