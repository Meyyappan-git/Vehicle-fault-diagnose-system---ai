const API_ROOT = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const response = await fetch(`${API_ROOT}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  const body = await response.json()
  if (!response.ok) throw new Error(body.detail || 'The diagnosis service could not complete this request.')
  return body
}

export const getMeta = () => request('/api/meta')
export const getHealth = () => request('/api/health')
export const diagnose = (payload) => request('/api/diagnose', { method: 'POST', body: JSON.stringify(payload) })
export const askAssistant = (question, payload, diagnosis) => request('/api/qa', {
  method: 'POST',
  body: JSON.stringify({ question, payload, diagnosis }),
})
