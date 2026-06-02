import api from './request'

export function uploadResume(file, targetPosition) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('target_position', targetPosition)
  return api.post('/resumes/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000
  })
}

export function getResume(resumeId) {
  return api.get(`/resumes/${resumeId}`)
}

export function getResumes() {
  return api.get('/resumes')
}
