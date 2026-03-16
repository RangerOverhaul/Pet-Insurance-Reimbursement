# 🐾 PetCare Insurance Platform

Plataforma full stack de reembolso de seguros para mascotas.

```
pet_insurance_full/
├── backend/        Django REST Framework API
├── frontend/       Vue.js 3 SPA
├── docker-compose.yml
└── README.md
```

---

## Inicio rápido

### Con Docker Compose (recomendado)

```bash
docker-compose up --build
```

- Backend → http://localhost:8000
- Frontend → http://localhost:5173
- Swagger UI → http://localhost:8000/api/docs/

### Manual

```bash
# ── Backend ──
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# ── Frontend ── (otra terminal)
cd frontend
npm install
npm run dev
```

---

## Roles

| Rol | Capacidades |
|---|---|
| `CUSTOMER` | Registrar mascotas · Enviar reclamos · Ver historial propio |
| `SUPPORT` | Ver todo · Aprobar/Rechazar reclamos · Cola de revisión |
| `ADMIN` | Todo lo anterior + panel `/admin/` |

---

## Tests

```bash
cd backend
python manage.py test users pets claims --verbosity=2
# 26 tests · 0 failures
```
