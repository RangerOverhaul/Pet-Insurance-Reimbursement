# 🐾 Pet Insurance Reimbursement — Backend

REST API built with **Django 5 + Django REST Framework**.

---

## Stack

| Tool | Usage |
|---|---|
| Django 5 | Main framework |
| Django REST Framework | REST API |
| SimpleJWT | JWT Authentication |
| drf-spectacular | OpenAPI / Swagger documentation |
| SQLite | Database (development) |

---

## Structure
```
backend/
├── pet_insurance/   → Project config (settings, urls)
├── users/           → Custom User model, authentication, roles
├── pets/            → Pet model, CRUD, permissions
├── claims/          → Claim model, status workflow, async task
├── manage.py
├── requirements.txt
├── Dockerfile
└── entrypoint.sh    → Runs migrations and starts the server
```

---

## Main Endpoints

### Auth
| Method | URL | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register (always creates CUSTOMER) |
| POST | `/api/auth/login/` | Login, returns JWT tokens |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| GET | `/api/auth/me/` | Authenticated user profile |

### Pets
| Method | URL | Description |
|---|---|---|
| GET | `/api/pets/` | List pets |
| POST | `/api/pets/` | Create pet |
| GET | `/api/pets/{id}/` | Detail |
| PUT | `/api/pets/{id}/` | Update |
| DELETE | `/api/pets/{id}/` | Delete |

### Claims
| Method | URL | Description |
|---|---|---|
| GET | `/api/claims/` | List claims |
| POST | `/api/claims/` | Submit claim (multipart/form-data) |
| GET | `/api/claims/{id}/` | Detail |
| PATCH | `/api/claims/{id}/review/` | Approve or reject (SUPPORT/ADMIN) |
| GET | `/api/claims/pending-review/` | Review queue (SUPPORT/ADMIN) |

### User Admin
| Method | URL | Description |
|---|---|---|
| GET | `/api/auth/admin/users/` | List users (ADMIN) |
| POST | `/api/auth/admin/users/` | Create user (ADMIN) |
| PUT | `/api/auth/admin/users/{id}/` | Update user (ADMIN) |
| DELETE | `/api/auth/admin/users/{id}/` | Delete user (ADMIN) |

---

## Claim Status Workflow
```
POST /api/claims/
        │
        ▼
   PROCESSING  ← initial status on creation
        │
        │  background thread validates:
        │  • date_of_event within coverage period
        │  • invoice_date within coverage period
        │  • SHA-256 hash to detect duplicate invoices
        │
   ┌────┴────┐
   │         │
IN_REVIEW  REJECTED  ← automatic if validation fails
   │
   ├── APPROVED  ← SUPPORT / ADMIN approves
   └── REJECTED  ← SUPPORT / ADMIN rejects
```

---

## Business Rules

- `coverage_end = coverage_start + 365 days` (auto-calculated on save)
- `date_of_event` and `invoice_date` must fall within the pet's active coverage period
- Duplicate invoices detected via **SHA-256** file hash before saving
- Customers can only manage their own pets and claims
- Only claims with status `IN_REVIEW` can be approved or rejected
- The reviewer's email is recorded on every approval or rejection

---

## Roles & Permissions

| Action | CUSTOMER | SUPPORT | ADMIN |
|---|---|---|---|
| Manage own pets | ✅ | ✅ | ✅ |
| View all pets | ❌ | ✅ | ✅ |
| Submit claims | ✅ | ❌ | ✅ |
| View all claims | ❌ | ✅ | ✅ |
| Approve / Reject claims | ❌ | ✅ | ✅ |
| Manage users | ❌ | ❌ | ✅ |
| Django Admin panel | ❌ | ❌ | ✅ |

---

## Running Tests
```bash
python manage.py test users pets claims --verbosity=2
# 26 tests · 0 failures
```

---

## API Documentation

With the server running:

| Tool | URL |
|---|---|
| Swagger UI | http://localhost:8000/api/docs/ |
| ReDoc | http://localhost:8000/api/redoc/ |
| OpenAPI Schema | http://localhost:8000/api/schema/ |