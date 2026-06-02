import api from './request'

export function register(data) {
  return api.post('/auth/register', data)
}

export function login(email, password) {
  return api.post('/auth/login', { email, password })
}

export function getMe() {
  return api.get('/auth/me')
}
