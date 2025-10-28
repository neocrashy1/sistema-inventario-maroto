const API_BASE = '/api/v1'

// token management
let token = typeof localStorage !== 'undefined' ? localStorage.getItem('access_token') : null
export function setToken(t) {
  token = t
  if (typeof localStorage !== 'undefined') localStorage.setItem('access_token', t)
}
export function getToken() { return token }

function makeHeaders(extra = {}) {
  return { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...extra }
}

export async function apiGet(path, opts = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: makeHeaders(opts.headers),
    ...opts
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function apiPost(path, body, opts = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: makeHeaders(opts.headers),
    body: JSON.stringify(body),
    ...opts
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function login({ username, password }) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  })
  if (!res.ok) throw new Error(`Login falhou: HTTP ${res.status}`)
  const data = await res.json()
  if (data?.access_token) setToken(data.access_token)
  return data
}