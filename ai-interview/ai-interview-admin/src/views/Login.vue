<template>
  <div class="login-page">
    <div class="login-card">
      <h2>🎯 智面后台</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>邮箱</label>
          <input v-model="email" type="email" placeholder="admin@ai-interview.com" required />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input v-model="password" type="password" placeholder="默认: ai-interview&admin" required />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" class="btn-glow" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { authApi } from '../api'

const router = useRouter()
const authStore = useAuthStore()
const email = ref('admin@ai-interview.com')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''; loading.value = true
  try {
    const data = await authApi.login(email.value, password.value)
    authStore.setAuth({ ...data, email: email.value })
    router.push('/')
  } catch (e) { error.value = e.message }
  finally { loading.value = false }
}
</script>

<style scoped>
.login-page { display: flex; align-items: center; justify-content: center; min-height: 100vh; background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%); }
.login-card { width: 400px; background: white; border-radius: 16px; padding: 40px 36px; text-align: center; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }
.login-card h2 { font-size: 24px; color: #4f46e5; margin-bottom: 28px; }
.form-group { margin-bottom: 18px; text-align: left; }
.form-group label { display: block; margin-bottom: 6px; font-size: 14px; font-weight: 500; color: #374151; }
.form-group input { width: 100%; padding: 11px 14px; border: 1px solid #e5e7eb; border-radius: 10px; font-size: 14px; outline: none; transition: all 0.3s; background: #f9fafb; }
.form-group input:focus { border-color: #4f46e5; box-shadow: 0 0 0 3px rgba(79,70,229,0.1); background: white; }
.error { color: #ef4444; font-size: 13px; margin-bottom: 12px; }
.btn-glow { width: 100%; padding: 12px; border: none; border-radius: 10px; font-size: 15px; font-weight: 600; color: white; background: linear-gradient(135deg, #4f46e5, #7c3aed, #6366f1); background-size: 200% 200%; animation: gradientShift 3s ease infinite; cursor: pointer; transition: all 0.3s; box-shadow: 0 4px 15px rgba(79,70,229,0.4); }
.btn-glow:hover { transform: translateY(-1px); box-shadow: 0 6px 25px rgba(79,70,229,0.5); }
.btn-glow:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
@keyframes gradientShift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
</style>
