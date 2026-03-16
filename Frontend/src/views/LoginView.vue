<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-brand">
        <span class="auth-logo">🐾</span>
        <h1>PetCare Insurance</h1>
        <p>Plataforma de reembolso para mascotas</p>
      </div>

      <div v-if="error" class="alert alert-error">{{ error }}</div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label">Correo electrónico</label>
          <input v-model="form.email" type="email" class="form-input" placeholder="tu@email.com" required />
        </div>
        <div class="form-group">
          <label class="form-label">Contraseña</label>
          <input v-model="form.password" type="password" class="form-input" placeholder="••••••••" required />
        </div>
        <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center" :disabled="loading">
          <span v-if="loading" class="spinner" style="width:14px;height:14px"></span>
          <span>{{ loading ? "Ingresando..." : "Iniciar sesión" }}</span>
        </button>
      </form>

      <p class="auth-footer">
        ¿No tienes cuenta? <RouterLink to="/register">Regístrate</RouterLink>
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
const form = ref({ email: "", password: "" })
const loading = ref(false)
const error = ref("")

async function handleLogin() {
  error.value = ""
  loading.value = true
  try {
    await auth.login(form.value.email, form.value.password)
    await router.push("/pets")
  } catch (e) {
    error.value = e.response?.data?.detail || "Credenciales inválidas"
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
.auth-brand h1 { font-size: 1.4rem; color: var(--c-text); }
.auth-brand p { font-size: 12px; color: var(--c-text-muted); margin-top: 4px; }
.auth-footer { text-align: center; margin-top: 20px; font-size: 13px; color: var(--c-text-muted); }
.auth-footer a { color: var(--c-accent); text-decoration: none; font-weight: 500; }
</style>
