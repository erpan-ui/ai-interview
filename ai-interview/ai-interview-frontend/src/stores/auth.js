import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const refreshToken = ref(localStorage.getItem('refreshToken') || '')
  const userEmail = ref(localStorage.getItem('userEmail') || '')
  const userId = ref(localStorage.getItem('userId') || '')
  const userName = ref(localStorage.getItem('userName') || '')
  const userAvatar = ref(localStorage.getItem('userAvatar') || '')

  const isLoggedIn = computed(() => !!token.value)

  function setAuth(data) {
    token.value = data.access_token
    refreshToken.value = data.refresh_token
    userEmail.value = data.user?.email || ''
    userId.value = data.user?.id || ''
    const u = data.user || {}
    userName.value = ((u.last_name || '') + (u.first_name || '')).trim() || u.email || ''
    const avatar = u.avatar || ''
    if (avatar && !avatar.startsWith('http')) {
      userAvatar.value = avatar
    } else {
      userAvatar.value = avatar
    }
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('refreshToken', data.refresh_token)
    localStorage.setItem('userEmail', userEmail.value)
    localStorage.setItem('userId', userId.value)
    localStorage.setItem('userName', userName.value)
    localStorage.setItem('userAvatar', userAvatar.value)
  }

  function setUserInfo(info) {
    userName.value = ((info.last_name || '') + (info.first_name || '')).trim() || info.email || ''
    // 头像路径：直接使用相对路径，Vite proxy 会自动转发
    const avatar = info.avatar || ''
    if (avatar && !avatar.startsWith('http')) {
      userAvatar.value = avatar
    } else {
      userAvatar.value = avatar
    }
    localStorage.setItem('userName', userName.value)
    localStorage.setItem('userAvatar', userAvatar.value)
  }

  function logout() {
    token.value = ''
    refreshToken.value = ''
    userEmail.value = ''
    userId.value = ''
    userName.value = ''
    userAvatar.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userEmail')
    localStorage.removeItem('userId')
    localStorage.removeItem('userName')
    localStorage.removeItem('userAvatar')
  }

  return { token, refreshToken, userEmail, userId, userName, userAvatar, isLoggedIn, setAuth, setUserInfo, logout }
})
