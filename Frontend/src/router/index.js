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
      { path: 'admin/users', component: () => import('@/views/AdminUsersView.vue'), meta: { adminOnly: true } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  const hasToken = !!localStorage.getItem('access')

  // Si tiene token pero no tiene user cargado, cargarlo primero
  if (hasToken && !auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      auth.logout()
      return '/login'
    }
  }

  // Ruta protegida sin token
  if (to.meta.auth && !hasToken) return '/login'

  // Ruta de guest (login/register) con sesión activa → ir al home
  if (to.meta.guest && hasToken && auth.user) return '/'

  // Ruta solo para staff
  if (to.meta.staffOnly && !auth.isStaff) return '/'

  // Ruta solo para admin
  if (to.meta.adminOnly && !auth.isAdmin) return '/'
})

export default router