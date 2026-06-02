import api from './request'

export const authApi = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  me: () => api.get('/auth/me')
}

export const userApi = {
  list: (params) => api.get('/users', { params }),
  stats: () => api.get('/users/stats'),
  toggleActive: (id) => api.put(`/users/${id}/toggle-active`)
}

export const interviewApi = {
  list: (params) => api.get('/interviews', { params }),
  detail: (id) => api.get(`/interviews/${id}`),
  delete: (id) => api.delete(`/interviews/${id}`)
}
