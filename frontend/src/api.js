async function request(method, path, body) {
  const res = await fetch(`/api${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    let detail = res.statusText
    try {
      detail = (await res.json()).detail ?? detail
    } catch {}
    const err = new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
    err.status = res.status
    throw err
  }
  return res.status === 204 ? null : res.json()
}

const actionId = () => crypto.randomUUID?.() ?? `${Date.now()}-${Math.random()}`

export const api = {
  me: () => request('GET', '/auth/me'),
  logout: () => request('POST', '/auth/logout'),
  // yandex, google, or vk / ok / mail (all three go through VK ID)
  loginUrl: (provider = 'yandex', next = '/') =>
    provider === 'yandex' || provider === 'google'
      ? `/api/auth/${provider}/login?next=${encodeURIComponent(next)}`
      : `/api/auth/vk/login?provider=${encodeURIComponent(provider)}&next=${encodeURIComponent(next)}`,
  scenarios: () => request('GET', '/scenarios'),
  create: (cfg) => request('POST', '/sessions', cfg),
  get: (id) => request('GET', `/sessions/${id}`),
  snapshots: (id) => request('GET', `/sessions/${id}/snapshots`),
  start: (id) => request('POST', `/sessions/${id}/clock/start`, { client_action_id: actionId() }),
  pause: (id) => request('POST', `/sessions/${id}/clock/pause`, { client_action_id: actionId() }),
  setAssignments: (id, assignments) =>
    request('PUT', `/sessions/${id}/assignments`, { assignments, client_action_id: actionId() }),
  leveling: (id) => request('POST', `/sessions/${id}/leveling`),
  read: (id, messageId) => request('POST', `/sessions/${id}/messages/${messageId}/read`),
  decide: (id, decisionId, option) =>
    request('POST', `/sessions/${id}/decisions/${decisionId}`, { option, client_action_id: actionId() }),
  stream: (id) => new EventSource(`/api/sessions/${id}/stream`),
}
