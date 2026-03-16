<template>
  <div class="view-page">
    <div class="view-header">
      <div>
        <h1>👥 Gestión de Usuarios</h1>
        <p class="text-muted text-sm mt-1">Administración completa de cuentas — solo visible para ADMIN</p>
      </div>
      <button class="btn btn-primary" @click="openCreate">+ Nuevo usuario</button>
    </div>

    <!-- Stats -->
    <div class="stats-row">
      <div class="stat-card" v-for="s in stats" :key="s.label">
        <div class="stat-val">{{ s.val }}</div>
        <div class="stat-label">{{ s.label }}</div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner" style="width:28px;height:28px;border-width:3px"></div>
    </div>

    <div v-else class="card">
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Email</th>
              <th>Rol</th>
              <th>Estado</th>
              <th>Registro</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td class="font-mono text-muted text-sm">{{ u.id }}</td>
              <td>
                <div style="display:flex;align-items:center;gap:8px">
                  <div class="user-dot" :class="'dot-' + u.role.toLowerCase()">
                    {{ u.email[0].toUpperCase() }}
                  </div>
                  <span>{{ u.email }}</span>
                  <span v-if="u.id === currentUserId" class="self-badge">tú</span>
                </div>
              </td>
              <td>
                <span class="badge" :class="roleBadgeClass(u.role)">{{ u.role }}</span>
              </td>
              <td>
                <span class="badge" :class="u.is_active ? 'badge-active' : 'badge-expired'">
                  {{ u.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="font-mono text-muted text-sm">{{ fmtDate(u.date_joined) }}</td>
              <td>
                <div style="display:flex;gap:6px">
                  <button class="btn btn-secondary btn-sm" @click="openEdit(u)">Editar</button>
                  <button
                    class="btn btn-danger btn-sm"
                    :disabled="u.id === currentUserId"
                    @click="confirmDelete(u)"
                  >Eliminar</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal: Create / Edit -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ editing ? 'Editar usuario' : 'Nuevo usuario' }}</h2>
          <button class="btn btn-ghost btn-sm" @click="showModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="formError" class="alert alert-error">{{ formError }}</div>

          <div class="form-group">
            <label class="form-label">Correo electrónico</label>
            <input v-model="form.email" type="email" class="form-input" placeholder="usuario@email.com" required />
          </div>
          <div class="form-group">
            <label class="form-label">Rol</label>
            <select v-model="form.role" class="form-select">
              <option value="CUSTOMER">CUSTOMER — Cliente</option>
              <option value="SUPPORT">SUPPORT — Equipo de soporte</option>
              <option value="ADMIN">ADMIN — Administrador</option>
            </select>
          </div>
          <div class="section-divider">Datos personales</div>
          <div class="form-group">
            <label class="form-label">Nombre completo</label>
            <input v-model="form.full_name" class="form-input" placeholder="Nombre y apellidos" />
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
            <div class="form-group">
              <label class="form-label">Número de documento</label>
              <input v-model="form.document_number" class="form-input" placeholder="Ej: 1234567890" />
            </div>
            <div class="form-group">
              <label class="form-label">Teléfono</label>
              <input v-model="form.phone_number" class="form-input" placeholder="Ej: 3001234567" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">{{ editing ? 'Nueva contraseña (dejar vacío para no cambiar)' : 'Contraseña' }}</label>
            <input v-model="form.password" type="password" class="form-input" :placeholder="editing ? 'Sin cambios' : 'Mínimo 8 caracteres'" :required="!editing" />
          </div>
          <div v-if="editing" class="form-group">
            <label class="form-label">Estado</label>
            <select v-model="form.is_active" class="form-select">
              <option :value="true">Activo</option>
              <option :value="false">Inactivo</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showModal = false">Cancelar</button>
          <button class="btn btn-primary" :disabled="saving" @click="save">
            <span v-if="saving" class="spinner" style="width:13px;height:13px"></span>
            {{ saving ? 'Guardando...' : 'Guardar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: Delete confirm -->
    <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
      <div class="modal" style="max-width:380px">
        <div class="modal-header"><h2>Eliminar usuario</h2></div>
        <div class="modal-body">
          <p>¿Eliminar la cuenta de <strong>{{ deleteTarget.email }}</strong>?</p>
          <p class="text-muted text-sm mt-2">Esta acción eliminará también sus mascotas y reclamos asociados.</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="deleteTarget = null">Cancelar</button>
          <button class="btn btn-danger" :disabled="saving" @click="doDelete">
            {{ saving ? 'Eliminando...' : 'Eliminar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toast" class="toast" :class="'toast--' + toast.type">{{ toast.msg }}</div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usersApi } from '@/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const users = ref([])
const loading = ref(true)
const showModal = ref(false)
const editing = ref(null)
const deleteTarget = ref(null)
const saving = ref(false)
const formError = ref('')
const toast = ref(null)
const currentUserId = computed(() => auth.user?.id)

const form = ref({ email: '', role: 'SUPPORT', password: '', is_active: true, full_name: '', document_number: '', phone_number: '' })

const stats = computed(() => [
  { label: 'Total usuarios', val: users.value.length },
  { label: 'Clientes',       val: users.value.filter(u => u.role === 'CUSTOMER').length },
  { label: 'Soporte',        val: users.value.filter(u => u.role === 'SUPPORT').length },
  { label: 'Admins',         val: users.value.filter(u => u.role === 'ADMIN').length },
])

async function loadUsers() {
  loading.value = true
  try {
    const { data } = await usersApi.list()
    users.value = data.results || data
  } finally { loading.value = false }
}

function openCreate() {
  editing.value = null
  form.value = { email: '', role: 'SUPPORT', password: '', is_active: true, full_name: '', document_number: '', phone_number: '' }
  formError.value = ''
  showModal.value = true
}

function openEdit(u) {
  editing.value = u
  form.value = {
    email: u.email, role: u.role, password: '', is_active: u.is_active,
    full_name: u.full_name || '', document_number: u.document_number || '', phone_number: u.phone_number || ''
  }
  formError.value = ''
  showModal.value = true
}

async function save() {
  saving.value = true
  formError.value = ''
  try {
    const payload = { ...form.value }
    if (!payload.password) delete payload.password
    if (editing.value) {
      await usersApi.update(editing.value.id, payload)
      showToast('Usuario actualizado', 'success')
    } else {
      await usersApi.create(payload)
      showToast('Usuario creado', 'success')
    }
    showModal.value = false
    await loadUsers()
  } catch (e) {
    const d = e.response?.data
    formError.value = Object.values(d || {}).flat().join(' ') || 'Error al guardar'
  } finally { saving.value = false }
}

function confirmDelete(u) { deleteTarget.value = u }

async function doDelete() {
  saving.value = true
  try {
    await usersApi.destroy(deleteTarget.value.id)
    deleteTarget.value = null
    showToast('Usuario eliminado', 'error')
    await loadUsers()
  } finally { saving.value = false }
}

function showToast(msg, type = 'success') {
  toast.value = { msg, type }
  setTimeout(() => { toast.value = null }, 3000)
}

const roleBadgeClass = r => ({ CUSTOMER: 'badge-approved', SUPPORT: 'badge-in_review', ADMIN: 'badge-processing' }[r])
const fmtDate = d => d ? new Date(d).toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' }) : '-'

onMounted(loadUsers)
</script>

<style scoped>
.view-page { padding: 28px 32px; max-width: 1000px; position: relative; }
.view-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 24px; gap: 16px; }
.loading-state { display: flex; justify-content: center; padding: 60px; }
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
.stat-card { background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--c-radius); padding: 16px 20px; }
.stat-val { font-size: 1.8rem; font-weight: 700; letter-spacing: -.04em; color: var(--c-accent); }
.stat-label { font-size: 11px; color: var(--c-text-muted); text-transform: uppercase; letter-spacing: .06em; margin-top: 2px; }
.user-dot { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; flex-shrink: 0; }
.dot-customer { background: var(--c-accent-light); color: var(--c-accent); }
.dot-support  { background: #ede9fe; color: #7c3aed; }
.dot-admin    { background: #fef9ee; color: #b45309; }
.self-badge { font-size: 10px; background: var(--c-surface-2); color: var(--c-text-muted); padding: 1px 7px; border-radius: 99px; border: 1px solid var(--c-border); }
.toast { position: fixed; bottom: 28px; right: 28px; padding: 12px 20px; border-radius: 10px; font-size: 13px; font-weight: 500; box-shadow: var(--c-shadow-lg); z-index: 200; }
.toast--success { background: var(--c-success); color: #fff; }
.toast--error { background: var(--c-danger); color: #fff; }
.toast-enter-active, .toast-leave-active { transition: all .3s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(12px); }
</style>