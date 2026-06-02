import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import router from '../router'

const api = axios.create({ baseURL: '/api/v1/backoffice', timeout: 30000 })

api.interceptors.request.use(config => {
  const authStore = useAuthStore()
  if (authStore.token) config.headers.Authorization = `Bearer ${authStore.token}`
  return config
})

api.interceptors.response.use(
  res => {
    const data = res.data
    if (data.code === 200) return data.data
    return Promise.reject(new Error(data.message || '请求失败'))
  },
  err => {
    if (err.response?.status === 403 || err.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      router.push('/login')
    }
    const data = err.response?.data
    let msg = data?.message || err.message || '网络错误'
    if (data?.detail) {
      msg = Array.isArray(data.detail) ? data.detail.map(d => d.msg).join('; ') : data.detail
    }
    return Promise.reject(new Error(msg))
  }
)

export default api
