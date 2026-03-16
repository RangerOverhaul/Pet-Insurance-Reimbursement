# 🐾 Pet Insurance Reimbursement Platform

Plataforma full stack de reembolso de seguros para mascotas.  
**Backend**: Django REST Framework · **Frontend**: Vue.js 3
```
Pet Insurance Reimbursement/
├── backend/        Django REST Framework API
├── frontend/       Vue.js 3 SPA
├── docker-compose.yml
└── README.md
```

---

## Credenciales de prueba

Ya existe un superusuario (rol **ADMIN**) creado:

| Campo | Valor |
|---|---|
| Email | `nylo@test.com` |
| Contraseña | `UserTest2026*` |

> Si necesitas crear otro superusuario, ver la sección [Crear superusuario](#crear-superusuario).

---

## Opción A — Correr con Docker Compose (recomendado)

### 1. Configurar el proxy del frontend para Docker

En `frontend/vite.config.js` asegúrate de tener:
```js
server: {
  proxy: {
    '/api': {
      target: 'http://backend:8000',
      changeOrigin: true
    }
  }
}
```

### 2. Levantar los servicios
```bash
docker-compose up --build
```

| Servicio | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/api/docs/ |
| Django Admin | http://localhost:8000/admin/ |

### 3. Aplicar migraciones (primera vez)
```bash
docker exec -it <nombre_contenedor_backend> python manage.py migrate
```

Para ver el nombre del contenedor:
```bash
docker ps
```

---

## Opción B — Correr en local (sin Docker)

### 1. Configurar el proxy del frontend para local

En `frontend/vite.config.js` asegúrate de tener:
```js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

### 2. Levantar el backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 3. Levantar el frontend (otra terminal)
```bash
cd frontend
npm install
npm run dev
```

| Servicio | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/api/docs/ |
| Django Admin | http://localhost:8000/admin/ |

---

## Crear superusuario

Si necesitas crear un nuevo usuario ADMIN adicional:

**Con Docker:**
```bash
# Entrar al contenedor del backend
docker exec -it <nombre_contenedor_backend> bash

# Crear superuser
python manage.py createsuperuser
```

O directamente sin entrar al contenedor:
```bash
docker exec -it <nombre_contenedor_backend> python manage.py createsuperuser
```

**En local:**
```bash
cd backend
source venv/bin/activate
python manage.py createsuperuser
```

---

## Roles

| Rol | Capacidades |
|---|---|
| `CUSTOMER` | Registrar mascotas · Enviar reclamos · Ver historial propio |
| `SUPPORT` | Ver todo · Aprobar/Rechazar reclamos · Cola de revisión · CRUD Pets y Claims |
| `ADMIN` | Todo lo anterior + Gestión de usuarios + panel `/admin/` |

> Los usuarios `SUPPORT` y `ADMIN` solo pueden ser creados desde el panel de administración (login como ADMIN → Gestión de Usuarios). El registro público siempre crea un `CUSTOMER`.

---

## Tests
```bash
cd backend
python manage.py test users pets claims --verbosity=2
# 26 tests · 0 failures
```