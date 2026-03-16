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

> Las migraciones se aplican automáticamente al iniciar el contenedor.

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
python manage.py makemigrations users 
python manage.py makemigrations pets 
python manage.py makemigrations claims 
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

> El usuario `SUPPORT` solo puede ser creados desde el panel de administración usando un usuario con rol `ADMIN` (login como ADMIN → Gestión de Usuarios) o desde el panel de ADMIN de Django. El registro público siempre crea un `CUSTOMER`.

---

## Tests
```bash
cd backend
python manage.py test users pets claims --verbosity=2
# 26 tests · 0 failures
```