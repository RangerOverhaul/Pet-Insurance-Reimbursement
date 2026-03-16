<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-brand">
        <span class="auth-logo">🐾</span>
        <h1>Crear cuenta</h1>
        <p>Únete a PetCare Insurance</p>
      </div>

      <div v-if="error" class="alert alert-error">{{ error }}</div>
      <div v-if="success" class="alert alert-success">{{ success }}</div>

      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label class="form-label">Correo electrónico</label>
          <input v-model="form.email" type="email" class="form-input" placeholder="tu@email.com" required />
        </div>
        <div class="form-group">
          <label class="form-label">Contraseña</label>
          <input v-model="form.password" type="password" class="form-input" placeholder="Mínimo 8 caracteres" required />
        </div>
        <div class="form-group">
          <label class="form-label">Confirmar contraseña</label>
          <input v-model="form.password2" type="password" class="form-input" placeholder="Repite tu contraseña" required />
        </div>
        <!-- ← el select de rol fue eliminado -->
        <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center" :disabled="loading">
          <span v-if="loading" class="spinner" style="width:14px;height:14px"></span>
          <span>{{ loading ? "Registrando..." : "Crear cuenta" }}</span>
        </button>
      </form>

      <p class="auth-footer">
        ¿Ya tienes cuenta? <RouterLink to="/login">Inicia sesión</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"

const router = useRouter()
const auth = useAuthStore()
const form = ref({ email: "", password: "", password2: "" })  // ← sin role
const loading = ref(false)
const error = ref("")
const success = ref("")

async function handleRegister() {
  error.value = ""
  if (form.value.password !== form.value.password2) {
    error.value = "Las contraseñas no coinciden"
    return
  }
  loading.value = true
  try {
    await auth.register(form.value)
    success.value = "¡Cuenta creada! Iniciando sesión..."
    await auth.login(form.value.email, form.value.password)
    router.push("/")
  } catch (e) {
    const d = e.response?.data
    error.value = d?.email?.[0] || d?.password?.[0] || d?.detail || "Error al registrar"
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: var(--c-bg); padding: 20px; }
.auth-card { background: var(--c-surface); border: 1px solid var(--c-border); border-radius: 16px; padding: 40px; width: 100%; max-width: 400px; box-shadow: var(--c-shadow-lg); }
.auth-brand { text-align: center; margin-bottom: 28px; }
.auth-logo { font-size: 2.2rem; display: block; margin-bottom: 8px; }
.auth-brand h1 { font-size: 1.4rem; }
.auth-brand p { font-size: 12px; color: var(--c-text-muted); margin-top: 4px; }
.auth-footer { text-align: center; margin-top: 20px; font-size: 13px; color: var(--c-text-muted); }
.auth-footer a { color: var(--c-accent); text-decoration: none; font-weight: 500; }
</style>