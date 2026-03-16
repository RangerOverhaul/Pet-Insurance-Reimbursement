<template>
  <div class="layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="'sidebar--' + roleClass">
      <div class="sidebar-top">
        <div class="sidebar-brand">
          <span class="sidebar-logo">🐾</span>
          <div>
            <div class="sidebar-title">PetCare</div>
            <div class="sidebar-sub">Insurance</div>
          </div>
        </div>

        <nav class="sidebar-nav">
          <RouterLink to="/pets" class="nav-link">
            <span class="nav-icon">🐶</span>
            <span>{{ auth.isStaff ? "Todas las Mascotas" : "Mis Mascotas" }}</span>
          </RouterLink>
          <RouterLink to="/claims" class="nav-link">
            <span class="nav-icon">📋</span>
            <span>{{ auth.isStaff ? "Todos los Reclamos" : "Mis Reclamos" }}</span>
          </RouterLink>
          <RouterLink v-if="auth.isStaff" to="/review" class="nav-link nav-link--staff">
            <span class="nav-icon">🔍</span>
            <span>Cola de Revisión</span>
            <span v-if="pendingCount > 0" class="nav-badge">{{ pendingCount }}</span>
          </RouterLink>

          <!-- Separador y sección Admin -->
          <div v-if="auth.isAdmin" class="nav-separator">Admin</div>
          <RouterLink v-if="auth.isAdmin" to="/admin/users" class="nav-link nav-link--admin">
            <span class="nav-icon">👥</span>
            <span>Gestión de Usuarios</span>
          </RouterLink>
        </nav>
      </div>

      <div class="sidebar-bottom">
        <div class="user-card">
          <div class="user-avatar">{{ avatarLetter }}</div>
          <div class="user-info">
            <div class="user-email">{{ auth.user?.email }}</div>
            <div class="user-role-badge" :class="'role-' + roleClass">{{ auth.user?.role }}</div>
          </div>
        </div>
        <button class="btn btn-ghost btn-sm" style="width:100%;justify-content:center;margin-top:8px" @click="handleLogout">
          Cerrar sesión
        </button>
      </div>
    </aside>

    <!-- Main content -->
    <main class="main-content">
      <!-- Staff announcement bar -->
      <div v-if="auth.isStaff" class="staff-bar">
        <span class="staff-bar-icon">🛡️</span>
        <span>Modo <strong>{{ auth.user?.role }}</strong> — acceso completo al panel de gestión</span>
      </div>

      <RouterView v-slot="{ Component }">
        <Transition name="page" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter, RouterLink, RouterView } from "vue-router"
import { useAuthStore } from "@/stores/auth"
import { claimsApi } from "@/api"

const router = useRouter()
const auth = useAuthStore()
const pendingCount = ref(0)

const roleClass = computed(() => (auth.user?.role || "CUSTOMER").toLowerCase())
const avatarLetter = computed(() => (auth.user?.email || "?")[0].toUpperCase())

async function fetchPending() {
  if (auth.isStaff) {
    try {
      const { data } = await claimsApi.pendingReview()
      pendingCount.value = data.length
    } catch {}
  }
}

onMounted(fetchPending)

function handleLogout() {
  auth.logout()
  router.push("/login")
}
</script>

<style scoped>
.layout { display: flex; height: 100vh; overflow: hidden; }

/* ── Sidebar ── */
.sidebar { width: var(--c-sidebar-w); flex-shrink: 0; display: flex; flex-direction: column; justify-content: space-between; border-right: 1px solid var(--c-border); background: var(--c-surface); overflow-y: auto; transition: background .3s; }
.sidebar--customer { background: #ffffff; }
.sidebar--support, .sidebar--admin { background: #1e1b4b; border-right-color: #312e81; }
.sidebar--support .sidebar-title, .sidebar--admin .sidebar-title { color: #e0e7ff; }
.sidebar--support .sidebar-sub, .sidebar--admin .sidebar-sub { color: #a5b4fc; }
.sidebar--support .sidebar-nav a, .sidebar--admin .sidebar-nav a { color: #c7d2fe; }
.sidebar--support .sidebar-nav a:hover, .sidebar--admin .sidebar-nav a:hover { background: rgba(255,255,255,.08); color: #fff; }
.sidebar--support .sidebar-nav a.router-link-active, .sidebar--admin .sidebar-nav a.router-link-active { background: rgba(255,255,255,.12); color: #fff; }
.sidebar--support .user-email, .sidebar--admin .user-email { color: #c7d2fe; }
.sidebar--support .btn-ghost, .sidebar--admin .btn-ghost { color: #a5b4fc; }
.sidebar--support .btn-ghost:hover, .sidebar--admin .btn-ghost:hover { background: rgba(255,255,255,.1); color: #fff; }

.sidebar-top { padding: 20px 14px 0; }
.sidebar-bottom { padding: 12px 14px 20px; border-top: 1px solid var(--c-border); }
.sidebar--support .sidebar-bottom, .sidebar--admin .sidebar-bottom { border-top-color: #312e81; }

.sidebar-brand { display: flex; align-items: center; gap: 10px; padding: 0 6px 20px; }
.sidebar-logo { font-size: 1.6rem; }
.sidebar-title { font-size: 15px; font-weight: 700; letter-spacing: -.02em; color: var(--c-text); }
.sidebar-sub { font-size: 10px; text-transform: uppercase; letter-spacing: .1em; color: var(--c-text-muted); }

.sidebar-nav { display: flex; flex-direction: column; gap: 2px; }
.nav-link { display: flex; align-items: center; gap: 10px; padding: 9px 10px; border-radius: 8px; text-decoration: none; font-size: 13px; font-weight: 500; color: var(--c-text-muted); transition: all .15s; position: relative; }
.nav-link:hover { background: var(--c-surface-2); color: var(--c-text); }
.nav-link.router-link-active { background: var(--c-accent-light); color: var(--c-accent); }
.nav-icon { font-size: 1rem; width: 20px; text-align: center; }
.nav-badge { margin-left: auto; background: var(--c-danger); color: #fff; border-radius: 99px; padding: 1px 7px; font-size: 10px; font-weight: 700; }

.user-card { display: flex; align-items: center; gap: 10px; padding: 10px 6px; }
.user-avatar { width: 32px; height: 32px; border-radius: 50%; background: var(--c-accent); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; flex-shrink: 0; }
.user-email { font-size: 12px; color: var(--c-text-muted); font-weight: 500; max-width: 140px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.user-role-badge { font-size: 9px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; margin-top: 2px; padding: 1px 6px; border-radius: 4px; display: inline-block; }
.role-customer { background: var(--c-accent-light); color: var(--c-accent); }
.role-support, .role-admin { background: #ede9fe; color: #7c3aed; }

/* ── Main ── */
.main-content { flex: 1; overflow-y: auto; display: flex; flex-direction: column; }
.staff-bar { background: linear-gradient(90deg, #1e1b4b 0%, #312e81 100%); color: #c7d2fe; padding: 8px 24px; font-size: 12px; display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.staff-bar strong { color: #e0e7ff; }
.staff-bar-icon { font-size: 1rem; }

.nav-separator {
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .12em;
  color: #6366f1;
  padding: 14px 10px 4px;
  opacity: .7;
}
.nav-link--admin {
  border: 1px dashed rgba(255,255,255,.15);
}
.nav-link--admin.router-link-active {
  background: rgba(255,255,255,.15);
  border-color: transparent;
}
</style>
