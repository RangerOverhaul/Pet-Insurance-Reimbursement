import { defineStore } from 'pinia'
import { authApi } from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    loading: false,
  }),
  getters: {
    isLoggedIn: s => !!localStorage.getItem('access'),
    role: s => s.user?.role || null,
    isCustomer: s => s.user?.role === 'CUSTOMER',
    isSupport: s => s.user?.role === 'SUPPORT',
    isAdmin: s => s.user?.role === 'ADMIN',
    isStaff: s => ['SUPPORT', 'ADMIN'].includes(s.user?.role),
  },
  actions: {
    async login(email, password) {
      const { data } = await authApi.login({ email, password })
      localStorage.setItem('access', data.access)
      localStorage.setItem('refresh', data.refresh)
      await this.fetchMe()
    },
    async fetchMe() {
      const { data } = await authApi.me()
      this.user = data
      document.body.className = 'role-' + data.role.toLowerCase()
    },
    logout() {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      this.user = null
      document.body.className = ''
    },
    async register(payload) {
      await authApi.register(payload)
    },
  },
})
