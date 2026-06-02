import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('admin_token') || '')
  const email = ref(localStorage.getItem('admin_email') || '')

  const isLoggedIn = computed(() => !!token.value)

  function setAuth(data) {
    token.value = data.access_token
    email.value = data.email || ''
    localStorage.setItem('admin_token', data.access_token)
    localStorage.setItem('admin_email', email.value)
  }

  function logout() {
    token.value = ''
    email.value = ''
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_email')
  }

  return { token, email, isLoggedIn, setAuth, logout }
})
