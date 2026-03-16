import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login', component: () => import('@/views/LoginView.vue'), meta: { guest: true } },
  { path: '/register', component: () => import('@/views/RegisterView.vue'), meta: { guest: true } },
  {
    path: '/',
    component: () => import('@/views/DashboardLayout.vue'),
    meta: { auth: true },
    children: [
      { path: '', redirect: '/pets' },
      { path: 'pets', component: () => import('@/views/PetsView.vue') },
      { path: 'claims', component: () => import('@/views/ClaimsView.vue') },
      { path: 'review', component: () => import('@/views/ReviewView.vue'), meta: { staffOnly: true } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (to.meta.auth && !auth.isLoggedIn) return '/login'
  if (to.meta.guest && auth.isLoggedIn) return '/'
  if (auth.isLoggedIn && !auth.user) {
    try { await auth.fetchMe() } catch { auth.logout(); return '/login' }
  }
  if (to.meta.staffOnly && !auth.isStaff) return '/'
})

export default router
