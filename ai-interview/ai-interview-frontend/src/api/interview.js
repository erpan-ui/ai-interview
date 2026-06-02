import api from './request'

export function startInterview(data) {
  return api.post('/interviews/start', data)
}

export function submitAnswer(interviewId, answer) {
  return api.post(`/interviews/${interviewId}/answer`, { answer })
}

export async function submitAnswerStream(interviewId, answer, onChunk, onDone) {
  const authStore = (await import('../stores/auth')).useAuthStore()
  const response = await fetch(`/api/v1/interviews/${interviewId}/answer/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authStore.token}`
    },
    body: JSON.stringify({ answer })
  })

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6))
          if (data.type === 'chunk') {
            onChunk(data.content)
          } else if (data.type === 'done') {
            onDone(data)
          } else if (data.type === 'error') {
            throw new Error(data.content)
          }
        } catch (e) {
          if (e.message !== 'Unexpected end of JSON input') throw e
        }
      }
    }
  }
}

export function getReport(interviewId) {
  return api.get(`/interviews/${interviewId}/report`)
}

export function getMessages(interviewId) {
  return api.get(`/interviews/${interviewId}/messages`)
}

export function getInterviews() {
  return api.get('/interviews')
}

export function deleteInterview(interviewId) {
  return api.delete(`/interviews/${interviewId}`)
}
