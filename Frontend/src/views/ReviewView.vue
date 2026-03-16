<template>
  <div class="view-page">
    <div class="view-header">
      <div>
        <h1>🔍 Cola de Revisión</h1>
        <p class="text-muted text-sm mt-1">Reclamos pendientes de aprobación o rechazo</p>
      </div>
      <button class="btn btn-secondary" @click="loadClaims">
        ↻ Actualizar
      </button>
    </div>

    <!-- Stats -->
    <div class="stats-row">
      <div class="stat-card stat-card--purple">
        <div class="stat-val">{{ claims.length }}</div>
        <div class="stat-label">En revisión</div>
      </div>
      <div class="stat-card">
        <div class="stat-val">${{ totalAmount }}</div>
        <div class="stat-label">Monto total</div>
      </div>
      <div class="stat-card">
        <div class="stat-val">{{ uniqueOwners }}</div>
        <div class="stat-label">Clientes distintos</div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner" style="width:28px;height:28px;border-width:3px"></div>
    </div>

    <div v-else-if="claims.length === 0" class="empty-state">
      <div class="empty-state-icon">✅</div>
      <h3>Todo al día</h3>
      <p>No hay reclamos pendientes de revisión en este momento</p>
    </div>

    <div v-else class="claims-grid">
      <div v-for="claim in claims" :key="claim.id" class="claim-card" :class="{ 'claim-card--reviewing': activeClaim?.id === claim.id }">
        <div class="claim-card-header">
          <div class="claim-id font-mono">#{{ claim.id }}</div>
          <span class="badge badge-in_review">En revisión</span>
        </div>

        <div class="claim-meta">
          <div class="meta-item">
            <span class="meta-label">Cliente</span>
            <span class="meta-val">{{ claim.owner_email }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Mascota</span>
            <span class="meta-val">{{ claim.pet_name }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Fecha evento</span>
            <span class="meta-val font-mono">{{ fmtDate(claim.date_of_event) }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Banco</span>
            <span class="meta-val">{{ claim.bank_display }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Cuenta</span>
            <span class="meta-val font-mono">{{ claim.account_number }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Titular</span>
            <span class="meta-val">{{ claim.owner_full_name || '—' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Documento</span>
            <span class="meta-val font-mono">{{ claim.owner_document || '—' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Factura</span>
            <span class="meta-val font-mono">{{ fmtDate(claim.invoice_date) }}</span>
          </div>
          <div class="meta-item meta-item--amount">
            <span class="meta-label">Monto solicitado</span>
            <span class="meta-amount">${{ Number(claim.amount).toLocaleString("es-CO") }}</span>
          </div>
        </div>

        <div v-if="claim.review_notes" class="claim-notes">
          <span class="meta-label">Notas automáticas</span>
          <p>{{ claim.review_notes }}</p>
        </div>

        <!-- Quick review inline -->
        <div v-if="activeClaim?.id === claim.id" class="review-inline">
          <div class="form-group" style="margin-bottom:10px">
            <label class="form-label">Notas de revisión</label>
            <textarea v-model="reviewNotes" class="form-input" rows="2" placeholder="Motivo de aprobación o rechazo..."></textarea>
          </div>
          <div v-if="reviewError" class="alert alert-error" style="padding:8px 12px;font-size:12px">{{ reviewError }}</div>
          <div class="review-actions">
            <button class="btn btn-primary" :disabled="reviewing" @click="doReview(claim.id, 'APPROVED')">
              <span v-if="reviewing && pendingAction === 'APPROVED'" class="spinner" style="width:12px;height:12px"></span>
              ✅ Aprobar
            </button>
            <button class="btn btn-danger" :disabled="reviewing" @click="doReview(claim.id, 'REJECTED')">
              <span v-if="reviewing && pendingAction === 'REJECTED'" class="spinner" style="width:12px;height:12px"></span>
              ❌ Rechazar
            </button>
            <button class="btn btn-ghost btn-sm" @click="activeClaim = null">Cancelar</button>
          </div>
        </div>
        <div v-else class="claim-card-footer">
          <span class="text-muted text-sm font-mono">{{ fmtDatetime(claim.created_at) }}</span>
          <button class="btn btn-primary btn-sm" @click="startReview(claim)">Revisar</button>
        </div>
      </div>
    </div>

    <!-- Toast notification -->
    <Transition name="toast">
      <div v-if="toast" class="toast" :class="'toast--' + toast.type">
        {{ toast.msg }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { claimsApi } from "@/api"

const claims = ref([])
const loading = ref(true)
const activeClaim = ref(null)
const reviewNotes = ref("")
const reviewing = ref(false)
const pendingAction = ref("")
const reviewError = ref("")
const toast = ref(null)

const totalAmount = computed(() => {
  const sum = claims.value.reduce((a, c) => a + parseFloat(c.amount || 0), 0)
  return sum.toLocaleString("es-CO")
})
const uniqueOwners = computed(() => new Set(claims.value.map(c => c.owner_email)).size)

async function loadClaims() {
  loading.value = true
  try {
    const { data } = await claimsApi.pendingReview()
    claims.value = data
  } finally { loading.value = false }
}

function startReview(claim) {
  activeClaim.value = claim
  reviewNotes.value = claim.review_notes || ""
  reviewError.value = ""
}

async function doReview(id, status) {
  reviewing.value = true
  pendingAction.value = status
  reviewError.value = ""
  try {
    await claimsApi.review(id, { status, review_notes: reviewNotes.value })
    claims.value = claims.value.filter(c => c.id !== id)
    activeClaim.value = null
    showToast(status === "APPROVED" ? "Reclamo aprobado exitosamente" : "Reclamo rechazado", status === "APPROVED" ? "success" : "error")
  } catch (e) {
    const d = e.response?.data
    reviewError.value = Object.values(d || {}).flat().join(" ") || "Error al procesar"
  } finally { reviewing.value = false; pendingAction.value = "" }
}

function showToast(msg, type = "success") {
  toast.value = { msg, type }
  setTimeout(() => { toast.value = null }, 3000)
}

const fmtDate = d => d ? new Date(d + "T00:00:00").toLocaleDateString("es-CO", { day: "2-digit", month: "short", year: "numeric" }) : "-"
const fmtDatetime = d => d ? new Date(d).toLocaleString("es-CO", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }) : "-"

onMounted(loadClaims)
</script>

<style scoped>
.view-page { padding: 28px 32px; max-width: 1100px; position: relative; }
.view-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 24px; }
.loading-state { display: flex; justify-content: center; padding: 60px; }

.stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 24px; }
.stat-card { background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--c-radius); padding: 16px 20px; }
.stat-card--purple { border-color: var(--c-accent); background: var(--c-accent-light); }
.stat-card--purple .stat-val { color: var(--c-accent); }
.stat-val { font-size: 1.8rem; font-weight: 700; letter-spacing: -.04em; color: var(--c-accent); }
.stat-label { font-size: 11px; color: var(--c-text-muted); text-transform: uppercase; letter-spacing: .06em; margin-top: 2px; }

.claims-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }

.claim-card { background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--c-radius); padding: 18px; box-shadow: var(--c-shadow); transition: box-shadow .2s, border-color .2s; }
.claim-card:hover { box-shadow: var(--c-shadow-lg); }
.claim-card--reviewing { border-color: var(--c-accent); box-shadow: 0 0 0 3px var(--c-accent-light), var(--c-shadow-lg); }

.claim-card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.claim-id { font-size: 12px; font-weight: 600; color: var(--c-text-muted); }

.claim-meta { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px; }
.meta-item { display: flex; flex-direction: column; gap: 2px; }
.meta-item--amount { grid-column: 1 / -1; padding-top: 10px; border-top: 1px solid var(--c-border); }
.meta-label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: .06em; color: var(--c-text-muted); }
.meta-val { font-size: 12px; font-weight: 500; color: var(--c-text); }
.meta-amount { font-size: 1.3rem; font-weight: 700; letter-spacing: -.03em; color: var(--c-accent); font-family: var(--font-mono); }

.claim-notes { background: var(--c-surface-2); border-radius: 6px; padding: 10px 12px; margin-bottom: 14px; }
.claim-notes .meta-label { margin-bottom: 4px; display: block; }
.claim-notes p { font-size: 12px; color: var(--c-text-muted); line-height: 1.5; }

.review-inline { border-top: 2px dashed var(--c-border); padding-top: 14px; margin-top: 4px; }
.review-actions { display: flex; align-items: center; gap: 8px; }
.review-actions .btn { flex: 1; justify-content: center; }
.review-actions .btn-ghost { flex: 0; }

.claim-card-footer { display: flex; align-items: center; justify-content: space-between; border-top: 1px solid var(--c-border); padding-top: 12px; margin-top: 4px; }

/* Toast */
.toast { position: fixed; bottom: 28px; right: 28px; padding: 12px 20px; border-radius: 10px; font-size: 13px; font-weight: 500; box-shadow: var(--c-shadow-lg); z-index: 200; }
.toast--success { background: var(--c-success); color: #fff; }
.toast--error { background: var(--c-danger); color: #fff; }
.toast-enter-active, .toast-leave-active { transition: all .3s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(12px); }
</style>
