<template>
  <div class="view-page">
    <div class="view-header">
      <div>
        <h1>📋 Reclamos</h1>
        <p class="text-muted text-sm mt-1">{{ auth.isStaff ? "Gestión completa de todos los reclamos" : "Historial de tus solicitudes de reembolso" }}</p>
      </div>
      <div style="display:flex;gap:10px;align-items:center">
        <select v-if="auth.isStaff" v-model="statusFilter" class="form-select" style="width:160px" @change="loadClaims">
          <option value="">Todos los estados</option>
          <option value="SUBMITTED">Enviado</option>
          <option value="PROCESSING">Procesando</option>
          <option value="IN_REVIEW">En revisión</option>
          <option value="APPROVED">Aprobado</option>
          <option value="REJECTED">Rechazado</option>
        </select>
        <button v-if="!auth.isStaff" class="btn btn-primary" @click="openCreate">
          + Nuevo reclamo
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state"><div class="spinner" style="width:28px;height:28px;border-width:3px"></div></div>

    <div v-else-if="claims.length === 0" class="empty-state">
      <div class="empty-state-icon">📄</div>
      <h3>Sin reclamos</h3>
      <p>{{ auth.isStaff ? "No hay reclamos con ese filtro" : "Aún no has enviado ningún reclamo" }}</p>
      <button v-if="!auth.isStaff" class="btn btn-primary" style="margin-top:16px" @click="openCreate">Crear reclamo</button>
    </div>

    <div v-else class="card">
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th v-if="auth.isStaff">Cliente</th>
              <th>Mascota</th>
              <th>Monto</th>
              <th>Fecha evento</th>
              <th>Estado</th>
              <th>Notas</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="claim in claims" :key="claim.id">
              <td class="font-mono text-muted text-sm">#{{ claim.id }}</td>
              <td v-if="auth.isStaff" class="text-muted text-sm">{{ claim.owner_email }}</td>
              <td><strong>{{ claim.pet_name }}</strong></td>
              <td class="font-mono"><strong>${{ Number(claim.amount).toLocaleString("es-CO") }}</strong></td>
              <td class="font-mono text-muted text-sm">{{ fmtDate(claim.date_of_event) }}</td>
              <td><span class="badge" :class="'badge-' + claim.status.toLowerCase().replace('_', '_')">{{ statusLabel(claim.status) }}</span></td>
              <td>
                <span v-if="claim.review_notes" class="text-muted text-sm" style="max-width:180px;display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" :title="claim.review_notes">
                  {{ claim.review_notes }}
                </span>
                <span v-else class="text-muted text-sm">—</span>
              </td>
              <td>
                <button class="btn btn-secondary btn-sm" @click="viewDetail(claim)">Ver</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal: Create Claim -->
    <div v-if="showCreate" class="modal-overlay" @click.self="showCreate = false">
      <div class="modal">
        <div class="modal-header">
          <h2>Nuevo reclamo</h2>
          <button class="btn btn-ghost btn-sm" @click="showCreate = false">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="formError" class="alert alert-error">{{ formError }}</div>
          <div v-if="formSuccess" class="alert alert-success">{{ formSuccess }}</div>

          <div class="form-group">
            <label class="form-label">Mascota</label>
            <select v-model="newClaim.pet" class="form-select" required>
              <option value="">Selecciona una mascota</option>
              <option v-for="p in myPets" :key="p.id" :value="p.id">{{ p.name }} ({{ speciesLabel(p.species) }})</option>
            </select>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
            <div class="form-group">
              <label class="form-label">Fecha del evento</label>
              <input v-model="newClaim.date_of_event" type="date" class="form-input" required />
            </div>
            <div class="form-group">
              <label class="form-label">Fecha de la factura</label>
              <input v-model="newClaim.invoice_date" type="date" class="form-input" required />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Monto ($)</label>
            <input v-model="newClaim.amount" type="number" step="0.01" min="0" class="form-input" placeholder="0.00" required />
          </div>
          <div class="form-group">
            <label class="form-label">Factura (PDF / imagen)</label>
            <input type="file" accept=".pdf,.jpg,.jpeg,.png" class="form-input" @change="onFile" required />
            <span class="form-error" style="color:var(--c-text-muted)">Se verificará que no sea una factura duplicada</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showCreate = false">Cancelar</button>
          <button class="btn btn-primary" :disabled="saving" @click="submitClaim">
            <span v-if="saving" class="spinner" style="width:13px;height:13px"></span>
            {{ saving ? "Enviando..." : "Enviar reclamo" }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: Detail -->
    <div v-if="detail" class="modal-overlay" @click.self="detail = null">
      <div class="modal">
        <div class="modal-header">
          <h2>Reclamo #{{ detail.id }}</h2>
          <button class="btn btn-ghost btn-sm" @click="detail = null">✕</button>
        </div>
        <div class="modal-body">
          <div class="detail-grid">
            <div class="detail-row"><span>Mascota</span><strong>{{ detail.pet_name }}</strong></div>
            <div v-if="auth.isStaff" class="detail-row"><span>Cliente</span><strong>{{ detail.owner_email }}</strong></div>
            <div class="detail-row"><span>Monto</span><strong class="font-mono">${{ Number(detail.amount).toLocaleString("es-CO") }}</strong></div>
            <div class="detail-row"><span>Fecha evento</span><span class="font-mono">{{ fmtDate(detail.date_of_event) }}</span></div>
            <div class="detail-row"><span>Fecha factura</span><span class="font-mono">{{ fmtDate(detail.invoice_date) }}</span></div>
            <div class="detail-row"><span>Estado</span><span class="badge" :class="'badge-' + detail.status.toLowerCase()">{{ statusLabel(detail.status) }}</span></div>
            <div class="detail-row"><span>Creado</span><span class="font-mono text-sm text-muted">{{ fmtDatetime(detail.created_at) }}</span></div>
            <div v-if="detail.review_notes" class="detail-row detail-row--full"><span>Notas</span><span>{{ detail.review_notes }}</span></div>
          </div>

          <!-- Staff review actions -->
          <div v-if="auth.isStaff && detail.status === 'IN_REVIEW'" class="review-section">
            <h3>Acción de revisión</h3>
            <div class="form-group" style="margin-top:12px">
              <label class="form-label">Notas de revisión</label>
              <textarea v-model="reviewNotes" class="form-input" rows="2" placeholder="Comentario opcional..."></textarea>
            </div>
            <div v-if="reviewError" class="alert alert-error">{{ reviewError }}</div>
            <div style="display:flex;gap:10px;margin-top:4px">
              <button class="btn btn-primary" style="flex:1;justify-content:center" :disabled="reviewing" @click="doReview('APPROVED')">
                ✅ Aprobar
              </button>
              <button class="btn btn-danger" style="flex:1;justify-content:center" :disabled="reviewing" @click="doReview('REJECTED')">
                ❌ Rechazar
              </button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="detail = null">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { claimsApi, petsApi } from "@/api"
import { useAuthStore } from "@/stores/auth"

const auth = useAuthStore()
const claims = ref([])
const myPets = ref([])
const loading = ref(true)
const showCreate = ref(false)
const detail = ref(null)
const statusFilter = ref("")
const saving = ref(false)
const reviewing = ref(false)
const formError = ref("")
const formSuccess = ref("")
const reviewError = ref("")
const reviewNotes = ref("")
const newClaim = ref({ pet: "", date_of_event: "", invoice_date: "", amount: "", invoice: null })

async function loadClaims() {
  loading.value = true
  try {
    const params = statusFilter.value ? { status: statusFilter.value } : {}
    const { data } = await claimsApi.list(params)
    claims.value = data.results || data
  } finally { loading.value = false }
}

async function loadPets() {
  const { data } = await petsApi.list()
  myPets.value = (data.results || data).filter(p => p.is_coverage_active)
}

function openCreate() {
  newClaim.value = { pet: "", date_of_event: "", invoice_date: "", amount: "", invoice: null }
  formError.value = ""
  formSuccess.value = ""
  showCreate.value = true
  loadPets()
}

function onFile(e) { newClaim.value.invoice = e.target.files[0] }

async function submitClaim() {
  if (!newClaim.value.invoice) { formError.value = "Debes adjuntar la factura"; return }
  saving.value = true
  formError.value = ""
  formSuccess.value = ""
  try {
    const fd = new FormData()
    Object.entries(newClaim.value).forEach(([k, v]) => { if (v) fd.append(k, v) })
    await claimsApi.create(fd)
    formSuccess.value = "Reclamo enviado exitosamente. Será procesado en breve."
    await loadClaims()
    setTimeout(() => { showCreate.value = false }, 1500)
  } catch (e) {
    const d = e.response?.data
    formError.value = Object.values(d || {}).flat().join(" ") || "Error al enviar"
  } finally { saving.value = false }
}

function viewDetail(claim) {
  detail.value = { ...claim }
  reviewNotes.value = ""
  reviewError.value = ""
}

async function doReview(status) {
  reviewing.value = true
  reviewError.value = ""
  try {
    await claimsApi.review(detail.value.id, { status, review_notes: reviewNotes.value })
    detail.value.status = status
    detail.value.review_notes = reviewNotes.value
    await loadClaims()
  } catch (e) {
    const d = e.response?.data
    reviewError.value = Object.values(d || {}).flat().join(" ") || "Error al revisar"
  } finally { reviewing.value = false }
}

const statusLabel = s => ({
  SUBMITTED: "Enviado", PROCESSING: "Procesando", IN_REVIEW: "En revisión",
  APPROVED: "Aprobado", REJECTED: "Rechazado"
}[s] || s)
const speciesLabel = s => ({ DOG: "Perro", CAT: "Gato", OTHER: "Otro" }[s] || s)
const fmtDate = d => d ? new Date(d + "T00:00:00").toLocaleDateString("es-CO", { day: "2-digit", month: "short", year: "numeric" }) : "-"
const fmtDatetime = d => d ? new Date(d).toLocaleString("es-CO", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }) : "-"

onMounted(loadClaims)
</script>

<style scoped>
.view-page { padding: 28px 32px; max-width: 1100px; }
.view-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 24px; }
.loading-state { display: flex; justify-content: center; padding: 60px; }
.detail-grid { display: flex; flex-direction: column; gap: 0; border: 1px solid var(--c-border); border-radius: 8px; overflow: hidden; }
.detail-row { display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; border-bottom: 1px solid var(--c-border); font-size: 13px; }
.detail-row:last-child { border-bottom: none; }
.detail-row--full { flex-direction: column; align-items: flex-start; gap: 4px; }
.detail-row > span:first-child { font-size: 11px; text-transform: uppercase; letter-spacing: .05em; color: var(--c-text-muted); font-weight: 600; }
.review-section { margin-top: 20px; padding-top: 20px; border-top: 2px dashed var(--c-border); }
.review-section h3 { font-size: 13px; text-transform: uppercase; letter-spacing: .06em; color: var(--c-text-muted); margin-bottom: 4px; }
</style>
