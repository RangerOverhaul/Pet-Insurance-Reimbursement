# 🐾 PetCare Insurance — Frontend (Vue.js 3)

SPA construida con **Vue 3 + Vite + Pinia + Vue Router**.

---

## Inicio rápido
```bash
npm install
npm run dev
```

---

## ⚠️ Configuración del proxy según entorno

El archivo clave es `vite.config.js`. Debes ajustar el `target` según cómo estés corriendo el proyecto:

### Corriendo en local (sin Docker)
```js
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

### Corriendo con Docker Compose
```js
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://backend:8000',  // nombre del servicio en docker-compose
      changeOrigin: true
    }
  }
}
```

> El nombre `backend` corresponde al servicio definido en `docker-compose.yml`. Si lo cambias allí, actualiza este valor también.

---

## Estructura
```
src/
├── api/          → Servicios axios (auth, pets, claims, users)
├── assets/       → CSS global + tokens de diseño por rol
├── router/       → Vue Router con guards por rol
├── stores/       → Pinia: auth store con getters de rol
└── views/
    ├── LoginView.vue        → Login con JWT
    ├── RegisterView.vue     → Registro (siempre crea CUSTOMER)
    ├── DashboardLayout.vue  → Sidebar + layout principal
    ├── PetsView.vue         → CRUD mascotas
    ├── ClaimsView.vue       → Reclamos + envío de factura
    ├── ReviewView.vue       → Cola de revisión (SUPPORT / ADMIN)
    └── AdminUsersView.vue   → Gestión de usuarios (solo ADMIN)
```

---

## Diferencias de interfaz por rol

### CUSTOMER (sidebar teal)
- Ve y gestiona solo sus propias mascotas
- Envía reclamos con archivo adjunto
- Consulta el historial y estado de sus reclamos

### SUPPORT (sidebar violeta oscuro)
- Barra de anuncio de modo staff
- Ve **todas** las mascotas y reclamos
- Accede a la Cola de Revisión con badge de pendientes
- Puede aprobar o rechazar reclamos en `IN_REVIEW`

### ADMIN (sidebar violeta oscuro + sección Admin)
- Todo lo de SUPPORT
- Menú exclusivo **Gestión de Usuarios**
- CRUD completo de usuarios: crear CUSTOMER, SUPPORT o ADMIN
- Activar / desactivar cuentas

---

## Build para producción
```bash
npm run build
# Salida en /dist
```