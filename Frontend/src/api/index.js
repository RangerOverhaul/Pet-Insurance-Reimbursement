import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('access')
  if (token) cfg.headers.Authorization = 'Bearer ' + token
  return cfg
})

api.interceptors.response.use(
  res => res,
  async err => {
    const original = err.config
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem('refresh')
      if (refresh) {
        try {
          const { data } = await axios.post('/api/auth/token/refresh/', { refresh })
          localStorage.setItem('access', data.access)
          original.headers.Authorization = 'Bearer ' + data.access
          return api(original)
        } catch {
          localStorage.removeItem('access')
          localStorage.removeItem('refresh')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(err)
  }
)

export default api

export const authApi = {
  register: d => api.post('/auth/register/', d),
  login: d => api.post('/auth/login/', d),
  me: () => api.get('/auth/me/'),
}

export const petsApi = {
  list: () => api.get('/pets/'),
  create: d => api.post('/pets/', d),
  update: (id, d) => api.put('/pets/' + id + '/', d),
  destroy: id => api.delete('/pets/' + id + '/'),
}

export const claimsApi = {
  list: (params) => api.get('/claims/', { params }),
  create: d => api.post('/claims/', d, { headers: { 'Content-Type': 'multipart/form-data' } }),
  get: id => api.get('/claims/' + id + '/'),
  review: (id, d) => api.patch('/claims/' + id + '/review/', d),
  pendingReview: () => api.get('/claims/pending-review/'),
}
