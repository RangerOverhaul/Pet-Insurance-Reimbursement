<template>
  <div class="view-page">
    <div class="view-header">
      <div>
        <h1>🐶 Mascotas</h1>
        <p class="text-muted text-sm mt-1">{{ auth.isStaff ? "Todas las mascotas registradas en la plataforma" : "Tus mascotas aseguradas" }}</p>
      </div>
      <button v-if="!auth.isStaff" class="btn btn-primary" @click="openCreate">
        + Registrar mascota
      </button>
    </div>

    <!-- Stats bar (staff only) -->
    <div v-if="auth.isStaff" class="stats-row">
      <div class="stat-card">
        <div class="stat-val">{{ pets.length }}</div>
        <div class="stat-label">Total mascotas</div>
      </div>
      <div class="stat-card">
        <div class="stat-val">{{ pets.filter(p => p.is_coverage_active).length }}</div>
        <div class="stat-label">Cobertura activa</div>
      </div>
      <div class="stat-card">
        <div class="stat-val">{{ pets.filter(p => p.species === "DOG").length }}</div>
        <div class="stat-label">Perros</div>
      </div>
      <div class="stat-card">
        <div class="stat-val">{{ pets.filter(p => p.species === "CAT").length }}</div>
        <div class="stat-label">Gatos</div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner" style="width:28px;height:28px;border-width:3px"></div>
    </div>

    <div v-else-if="pets.length === 0" class="empty-state">
      <div class="empty-state-icon">🐾</div>
      <h3>Sin mascotas registradas</h3>
      <p>Registra tu primera mascota para comenzar</p>
      <button v-if="!auth.isStaff" class="btn btn-primary" style="margin-top:16px" @click="openCreate">Registrar mascota</button>
    </div>

    <div v-else class="card">
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Mascota</th>
              <th v-if="auth.isStaff">Dueño</th>
              <th>Especie</th>
              <th>Fecha nacimiento</th>
              <th>Cobertura</th>
              <th>Estado</th>
              <th v-if="!auth.isStaff">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pet in pets" :key="pet.id">
              <td><strong>{{ pet.name }}</strong></td>
              <td v-if="auth.isStaff" class="text-muted">{{ pet.owner_email }}</td>
              <td><span class="badge" :class="'badge-' + pet.species.toLowerCase()">{{ speciesLabel(pet.species) }}</span></td>
              <td class="text-muted font-mono">{{ fmtDate(pet.birth_date) }}</td>
              <td>
                <div class="font-mono text-sm">{{ fmtDate(pet.coverage_start) }} → {{ fmtDate(pet.coverage_end) }}</div>
              </td>
              <td>
                <span class="badge" :class="pet.is_coverage_active ? 'badge-active' : 'badge-expired'">
                  {{ pet.is_coverage_active ? "Activa" : "Vencida" }}
                </span>
              </td>
              <td v-if="!auth.isStaff">
                <div style="display:flex;gap:6px">
                  <button class="btn btn-secondary btn-sm" @click="openEdit(pet)">Editar</button>
                  <button class="btn btn-danger btn-sm" @click="confirmDelete(pet)">Eliminar</button>
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
          <h2>{{ editing ? "Editar mascota" : "Registrar mascota" }}</h2>
          <button class="btn btn-ghost btn-sm" @click="showModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="formError" class="alert alert-error">{{ formError }}</div>
          <div class="form-group">
            <label class="form-label">Nombre</label>
            <input v-model="form.name" class="form-input" placeholder="Nombre de la mascota" required />
          </div>
          <div class="form-group">
            <label class="form-label">Especie</label>
            <select v-model="form.species" class="form-select">
              <option value="DOG">🐕 Perro</option>
              <option value="CAT">🐈 Gato</option>
              <option value="OTHER">🐾 Otro</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Fecha de nacimiento</label>
            <input v-model="form.birth_date" type="date" class="form-input" required />
          </div>
          <div v-if="!editing" class="form-group">
            <label class="form-label">Inicio de cobertura</label>
            <input v-model="form.coverage_start" type="date" class="form-input" required />
            <span class="form-error" style="color:var(--c-text-muted)">La cobertura dura 365 días automáticamente</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showModal = false">Cancelar</button>
          <button class="btn btn-primary" :disabled="saving" @click="save">
            <span v-if="saving" class="spinner" style="width:13px;height:13px"></span>
            {{ saving ? "Guardando..." : "Guardar" }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: Delete confirm -->
    <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
      <div class="modal" style="max-width:380px">
        <div class="modal-header"><h2>Eliminar mascota</h2></div>
        <div class="modal-body">
          <p>¿Estás seguro de eliminar <strong>{{ deleteTarget.name }}</strong>? Esta acción no se puede deshacer.</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="deleteTarget = null">Cancelar</button>
          <button class="btn btn-danger" :disabled="saving" @click="doDelete">
            {{ saving ? "Eliminando..." : "Eliminar" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { petsApi } from "@/api"
import { useAuthStore } from "@/stores/auth"

const auth = useAuthStore()
const pets = ref([])
const loading = ref(true)
const showModal = ref(false)
const editing = ref(null)
const deleteTarget = ref(null)
const saving = ref(false)
const formError = ref("")
const today = new Date().toISOString().split("T")[0]
const form = ref({ name: "", species: "DOG", birth_date: "", coverage_start: today })

async function loadPets() {
  loading.value = true
  try { const { data } = await petsApi.list(); pets.value = data.results || data }
  finally { loading.value = false }
}

function openCreate() {
  editing.value = null
  form.value = { name: "", species: "DOG", birth_date: "", coverage_start: today }
  formError.value = ""
  showModal.value = true
}

function openEdit(pet) {
  editing.value = pet
  form.value = { name: pet.name, species: pet.species, birth_date: pet.birth_date, coverage_start: pet.coverage_start }
  formError.value = ""
  showModal.value = true
}

async function save() {
  saving.value = true
  formError.value = ""
  try {
    if (editing.value) {
      await petsApi.update(editing.value.id, form.value)
    } else {
      await petsApi.create(form.value)
    }
    showModal.value = false
    await loadPets()
  } catch (e) {
    const d = e.response?.data
    formError.value = Object.values(d || {}).flat().join(" ") || "Error al guardar"
  } finally {
    saving.value = false
  }
}

function confirmDelete(pet) { deleteTarget.value = pet }

async function doDelete() {
  saving.value = true
  try {
    await petsApi.destroy(deleteTarget.value.id)
    deleteTarget.value = null
    await loadPets()
  } finally { saving.value = false }
}

const speciesLabel = s => ({ DOG: "Perro", CAT: "Gato", OTHER: "Otro" }[s] || s)
const fmtDate = d => d ? new Date(d + "T00:00:00").toLocaleDateString("es-CO", { day: "2-digit", month: "short", year: "numeric" }) : "-"

onMounted(loadPets)
</script>

<style scoped>
.view-page { padding: 28px 32px; max-width: 1100px; }
.view-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 24px; }
.loading-state { display: flex; justify-content: center; padding: 60px; }
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
.stat-card { background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--c-radius); padding: 16px 20px; }
.stat-val { font-size: 1.8rem; font-weight: 700; letter-spacing: -.04em; color: var(--c-accent); }
.stat-label { font-size: 11px; color: var(--c-text-muted); text-transform: uppercase; letter-spacing: .06em; margin-top: 2px; }
</style>
