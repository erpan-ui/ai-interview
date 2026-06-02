import api from './request'

export function getProfile() {
  return api.get('/auth/me')
}

export function updateProfile(data) {
  return api.put('/auth/me', data)
}

export function uploadAvatar(file) {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/auth/me/avatar', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function changePassword(oldPassword, newPassword) {
  return api.post('/auth/me/change-password', {
    old_password: oldPassword,
    new_password: newPassword
  })
}
