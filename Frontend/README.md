# 🐾 PetCare Insurance — Frontend (Vue.js 3)

SPA built with **Vue 3 + Vite + Pinia + Vue Router**.

---

## Quick Start
```bash
npm install
npm run dev
```

---

## ⚠️ Proxy Configuration by Environment

The key file is `vite.config.js`. You must adjust the `target` depending on how you are running the project:

### Running locally (without Docker)
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

### Running with Docker Compose
```js
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://backend:8000',  // service name defined in docker-compose.yml
      changeOrigin: true
    }
  }
}
```

> The name `backend` matches the service defined in `docker-compose.yml`. If you rename it there, update this value accordingly.

---

## Structure
```
src/
├── api/          → Axios services (auth, pets, claims, users)
├── assets/       → Global CSS + role-based design tokens
├── router/       → Vue Router with role-based guards
├── stores/       → Pinia: auth store with role getters
└── views/
    ├── LoginView.vue        → JWT login
    ├── RegisterView.vue     → Registration (always creates CUSTOMER)
    ├── DashboardLayout.vue  → Sidebar + main layout
    ├── PetsView.vue         → Pet CRUD
    ├── ClaimsView.vue       → Claims + file upload
    ├── ReviewView.vue       → Review queue (SUPPORT / ADMIN)
    └── AdminUsersView.vue   → User management (ADMIN only)
```

---

## UI Differences by Role

### CUSTOMER (teal sidebar)
- Views and manages only their own pets
- Submits claims with file attachment
- Tracks the history and status of their own claims

### SUPPORT (dark purple sidebar)
- Staff mode announcement bar at the top
- Views **all** pets and claims
- Access to the Review Queue with a pending badge
- Can approve or reject claims in `IN_REVIEW` status

### ADMIN (dark purple sidebar + Admin section)
- Everything SUPPORT can do
- Exclusive **User Management** menu
- Full user CRUD: create CUSTOMER, SUPPORT or ADMIN accounts
- Activate / deactivate accounts

---

## Production Build
```bash
npm run build
# Output in /dist
```