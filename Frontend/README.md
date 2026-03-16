# 🐾 PetCare Insurance — Frontend (Vue.js)

Aplicación SPA construida con **Vue 3 + Vite + Pinia + Vue Router**.

## Stack

| Herramienta | Versión |
|---|---|
| Vue 3 | ^3.4 |
| Vue Router | ^4.3 |
| Pinia | ^2.1 |
| Axios | ^1.6 |
| Vite | ^5.0 |

---

## Inicio rápido

```bash
# Instalar dependencias
npm install

# Levantar servidor de desarrollo (requiere backend en :8000)
npm run dev

# Build para producción
npm run build
```

> El proxy de Vite redirige `/api/*` → `http://localhost:8000` automáticamente en desarrollo.

---

## Estructura

```
src/
├── api/          → Servicios axios (auth, pets, claims)
├── assets/       → CSS global + tokens de diseño
├── router/       → Vue Router con guards por rol
├── stores/       → Pinia: auth store con getters de rol
└── views/
    ├── LoginView.vue        → Login con JWT
    ├── RegisterView.vue     → Registro
    ├── DashboardLayout.vue  → Sidebar + layout principal
    ├── PetsView.vue         → CRUD mascotas
    ├── ClaimsView.vue       → Reclamos + envío de factura
    └── ReviewView.vue       → Cola de revisión (solo SUPPORT/ADMIN)
```

---

## Diferencias de interfaz por rol

### CUSTOMER (teal)
- Sidebar en **blanco con acento teal**
- Ve solo sus mascotas y puede crear/editar/eliminar
- Puede enviar reclamos con archivo adjunto
- Ve el historial de sus reclamos y su estado actual

### SUPPORT / ADMIN (violeta oscuro)
- Sidebar con **fondo violeta oscuro** `#1e1b4b`
- Barra de anuncio de modo staff en la parte superior
- Ve **todas** las mascotas con stats de resumen (totales, activas, perros/gatos)
- Ve **todos** los reclamos con filtro por estado
- Accede a la **Cola de Revisión** (menú exclusivo con badge de pendientes)
- Puede aprobar o rechazar reclamos directamente desde las tarjetas

---

## Flujo de autenticación

1. Login → obtiene `access` + `refresh` → guarda en `localStorage`
2. Axios interceptor adjunta `Authorization: Bearer <token>` en cada request
3. Si el token expira (401) → intenta refresh automático
4. Si el refresh falla → redirige a `/login`
5. Al cargar → `fetchMe()` aplica clase CSS al `body` para el tema del rol

---

## Variables de diseño (CSS)

El archivo `src/assets/main.css` define tokens compartidos:

```css
/* Default (CUSTOMER) */
--c-accent: #0d9488;       /* teal */

/* Override automático para SUPPORT/ADMIN */
body.role-support, body.role-admin {
  --c-accent: #7c3aed;     /* violeta */
}
```

La clase `role-{lowercase}` se aplica al `<body>` después del login según el rol.
