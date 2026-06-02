<template>
  <div id="app">
    <nav class="navbar" v-if="authStore.token">
      <div class="nav-content">
        <router-link to="/dashboard" class="nav-logo">🎯 智面</router-link>
        <div class="nav-links">
          <router-link to="/dashboard">面试记录</router-link>
          <router-link to="/resume/upload">上传简历</router-link>
          <router-link to="/profile" class="nav-user-link">
            <img v-if="authStore.userAvatar && !avatarError" :src="authStore.userAvatar" class="nav-avatar" alt="avatar" @error="avatarError = true" />
            <span v-else class="nav-avatar-placeholder">👤</span>
            <span>{{ authStore.userName || '个人中心' }}</span>
          </router-link>
          <button class="btn-secondary" @click="logout" style="padding:6px 14px;font-size:13px">退出</button>
        </div>
      </div>
    </nav>
    <router-view />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'
import { getProfile } from './api/user'

const authStore = useAuthStore()
const router = useRouter()
const avatarError = ref(false)

onMounted(async () => {
  if (authStore.token) {
    try {
      const data = await getProfile()
      authStore.setUserInfo(data)
      avatarError.value = false
    } catch (e) {
      // 忽略
    }
  }
})

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 0 20px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.nav-content {
  max-width: 960px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
}
.nav-logo {
  font-size: 18px;
  font-weight: 700;
  color: #4f46e5;
}
.nav-links {
  display: flex;
  align-items: center;
  gap: 20px;
  font-size: 14px;
}
.nav-links a.router-link-active {
  color: #4f46e5;
  font-weight: 600;
}
.nav-user {
  color: #6b7280;
  font-size: 13px;
}
.nav-user-link {
  color: #6b7280;
  font-size: 13px;
  transition: color 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}
.nav-user-link:hover {
  color: #4f46e5;
}
.nav-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
}
.nav-avatar-placeholder {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}
</style>
