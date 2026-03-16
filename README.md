# 🐾 Pet Insurance Reimbursement Platform

Full stack platform for pet insurance reimbursements.  
**Backend**: Django REST Framework · **Frontend**: Vue.js 3
```
Pet Insurance Reimbursement/
├── backend/        Django REST Framework API
├── frontend/       Vue.js 3 SPA
├── docker-compose.yml
└── README.md
```
---

## Option A — Run with Docker Compose (recommended)

### 1. Configure the frontend proxy for Docker

In `frontend/vite.config.js` make sure you have:
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

### 2. Start the services
```bash
docker-compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/api/docs/ |
| Django Admin | http://localhost:8000/admin/ |

> Migrations run automatically when the container starts.

To check the container name:
```bash
docker ps
```

---

## Option B — Run locally (without Docker)

### 1. Configure the frontend proxy for local

In `frontend/vite.config.js` make sure you have:
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

### 2. Start the backend
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

### 3. Start the frontend (another terminal)
```bash
cd frontend
npm install
npm run dev
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/api/docs/ |
| Django Admin | http://localhost:8000/admin/ |

---

## Create Superuser

**With Docker:**
```bash
# Enter the backend container
docker exec -it <backend_container_name> bash

# Create superuser
python manage.py createsuperuser
```

Or directly without entering the container:
```bash
docker exec -it <backend_container_name> python manage.py createsuperuser
```

**Locally:**
```bash
cd backend
source venv/bin/activate
python manage.py createsuperuser
```

---

## Roles

| Role | Capabilities |
|---|---|
| `CUSTOMER` | Register pets · Submit claims · View own history |
| `SUPPORT` | View everything · Approve/Reject claims · Review queue · CRUD Pets and Claims |
| `ADMIN` | Everything above + User management + `/admin/` panel |

> `SUPPORT` users can only be created from the admin panel by an `ADMIN` user (login as ADMIN → User Management) or from the Django admin panel. Public registration always creates a `CUSTOMER`.

---

## Tests
```bash
cd backend
python manage.py test users pets claims --verbosity=2
# 26 tests · 0 failures
```

## Additional documentation

- [README del Backend](./backend/README.md) — modelos, endpoints, tests, reglas de negocio
- [README del Frontend](./frontend/README.md) — configuración del proxy, estructura, diferencias por rol