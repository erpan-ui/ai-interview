<template>
  <div class="admin-layout" v-if="authStore.isLoggedIn">
    <aside class="sidebar">
      <div class="sidebar-logo"><span class="logo-icon">🎯</span><span class="logo-text">智面</span></div>
      <div class="sidebar-subtitle">后台管理</div>
      <nav class="sidebar-nav">
        <router-link to="/" exact-active-class="active">
          <span class="nav-icon">📊</span> 数据概览
        </router-link>
        <router-link to="/users" active-class="active">
          <span class="nav-icon">👥</span> 用户管理
        </router-link>
        <router-link to="/interviews" active-class="active">
          <span class="nav-icon">🎤</span> 面试记录
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <span>{{ authStore.email }}</span>
        <button class="logout-btn" @click="logout">退出登录</button>
      </div>
    </aside>
    <main class="main-content">
      <router-view />
    </main>
  </div>
  <router-view v-else />
</template>

<script setup>
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'
const authStore = useAuthStore()
const router = useRouter()
function logout() { authStore.logout(); router.push('/login') }
</script>

<style scoped>
.admin-layout { display: flex; min-height: 100vh; }

.sidebar {
  width: 230px;
  background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
  color: white;
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0; left: 0; bottom: 0;
  overflow: hidden;
}

.sidebar::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at 30% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
              radial-gradient(ellipse at 70% 80%, rgba(168, 85, 247, 0.1) 0%, transparent 50%);
  animation: auroraFloat 8s ease-in-out infinite;
  pointer-events: none;
}

@keyframes auroraFloat {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  33% { transform: translate(2%, -3%) rotate(1deg); }
  66% { transform: translate(-2%, 2%) rotate(-1deg); }
}

.sidebar-logo {
  font-size: 22px;
  font-weight: 700;
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
}

.logo-icon {
  -webkit-text-fill-color: initial;
}

.logo-text {
  background: linear-gradient(135deg, #a78bfa, #818cf8, #6ee7b7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sidebar-subtitle {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 32px;
  position: relative;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  position: relative;
}

.sidebar-nav a {
  padding: 11px 14px;
  border-radius: 10px;
  color: #94a3b8;
  font-size: 14px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 10px;
}

.sidebar-nav a:hover {
  background: rgba(99, 102, 241, 0.15);
  color: #e0e7ff;
}

.sidebar-nav a.active {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(168, 85, 247, 0.2));
  color: white;
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.2);
}

.nav-icon { font-size: 16px; }

.sidebar-footer {
  font-size: 12px;
  color: #6b7280;
  border-top: 1px solid rgba(99, 102, 241, 0.15);
  padding-top: 16px;
  position: relative;
}

.logout-btn {
  display: block;
  width: 100%;
  margin-top: 10px;
  padding: 8px;
  border-radius: 8px;
  font-size: 13px;
  background: rgba(99, 102, 241, 0.15);
  color: #a5b4fc;
  border: 1px solid rgba(99, 102, 241, 0.2);
  cursor: pointer;
  transition: all 0.3s;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #fca5a5;
  border-color: rgba(239, 68, 68, 0.3);
}

.main-content {
  margin-left: 230px;
  flex: 1;
  padding: 28px;
  background: #f8fafc;
}
</style>
