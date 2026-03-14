# 🐾 Pet Insurance Reimbursement Platform — Backend

Django REST Framework API for managing pet insurance claims and reimbursements.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Django 5, Django REST Framework |
| Auth | JWT via `djangorestframework-simplejwt` |
| API Docs | OpenAPI 3.0 via `drf-spectacular` (Swagger UI + ReDoc) |
| Async | Python `threading` (Celery-ready design) |
| Database | SQLite (dev) — swap to PostgreSQL for prod |

---

## Project Structure

```
pet_insurance/        ← Django project config
users/                ← Custom User model, auth, roles
pets/                 ← Pet model, CRUD endpoints
claims/               ← Claim model, workflow, async task
```

---

## Quick Start

```bash
# 1. Create & activate virtualenv
python -m venv venv && source venv/bin/activate

# 2. Install dependencies
pip install django djangorestframework djangorestframework-simplejwt \
            django-cors-headers Pillow drf-spectacular

# 3. Run migrations
python manage.py migrate

# 4. Create a superuser (ADMIN role)
python manage.py createsuperuser

# 5. Start dev server
python manage.py runserver
```

---

## API Endpoints

### Auth
| Method | URL | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Obtain JWT tokens |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| GET/PATCH | `/api/auth/me/` | Current user profile |

### Pets
| Method | URL | Description | Roles |
|---|---|---|---|
| GET | `/api/pets/` | List pets | CUSTOMER (own), SUPPORT/ADMIN (all) |
| POST | `/api/pets/` | Create pet | CUSTOMER |
| GET | `/api/pets/{id}/` | Retrieve pet | Owner or SUPPORT/ADMIN |
| PUT/PATCH | `/api/pets/{id}/` | Update pet | Owner or SUPPORT/ADMIN |
| DELETE | `/api/pets/{id}/` | Delete pet | Owner or SUPPORT/ADMIN |

### Claims
| Method | URL | Description | Roles |
|---|---|---|---|
| GET | `/api/claims/` | List claims | CUSTOMER (own), SUPPORT/ADMIN (all) |
| POST | `/api/claims/` | Submit claim (file upload) | CUSTOMER |
| GET | `/api/claims/{id}/` | Retrieve claim | Owner or SUPPORT/ADMIN |
| PATCH | `/api/claims/{id}/review/` | Approve / Reject | SUPPORT, ADMIN |
| GET | `/api/claims/pending-review/` | All IN_REVIEW claims | SUPPORT, ADMIN |

**Filter claims by status** (SUPPORT/ADMIN):
```
GET /api/claims/?status=IN_REVIEW
```

### API Documentation
| URL | Description |
|---|---|
| `/api/docs/` | Swagger UI |
| `/api/redoc/` | ReDoc |
| `/api/schema/` | Raw OpenAPI JSON/YAML |

---

## Roles & Permissions

| Action | CUSTOMER | SUPPORT | ADMIN |
|---|---|---|---|
| Manage own pets | ✅ | ✅ | ✅ |
| View all pets | ❌ | ✅ | ✅ |
| Submit claims | ✅ | ❌ | ✅ |
| View own claims | ✅ | ✅ | ✅ |
| View all claims | ❌ | ✅ | ✅ |
| Approve/Reject claims | ❌ | ✅ | ✅ |
| Access admin panel | ❌ | ❌ | ✅ |

---

## Claim Workflow

```
POST /api/claims/
        │
        ▼
   PROCESSING  ←── Background thread validates:
        │            • invoice_date within coverage
        │            • date_of_event within coverage
        │
   ┌────┴────┐
   │         │
IN_REVIEW  REJECTED  ← (auto-rejected if validation fails)
   │
   ├── PATCH /api/claims/{id}/review/ {"status": "APPROVED"}
   │        → APPROVED
   │
   └── PATCH /api/claims/{id}/review/ {"status": "REJECTED"}
            → REJECTED
```

### Business Rules Enforced
- `coverage_end = coverage_start + 365 days` (auto-computed)
- `date_of_event` must be within the pet's active coverage period
- `invoice_date` must be within the pet's active coverage period
- Duplicate invoice detection via **SHA-256 file hash**
- Customers can only submit claims for their own pets
- Only `IN_REVIEW` claims can be approved/rejected by support

---

## Running Tests

```bash
python manage.py test users pets claims --verbosity=2
```

**26 tests** covering:
- Auth: register, login, token, me endpoint
- Pets: CRUD, ownership isolation, coverage computation
- Claims: submission, duplicate detection, coverage validation,
          role-based visibility, review workflow, async task trigger

---

## Environment Variables (production)

```env
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgresql://user:pass@host/db
ALLOWED_HOSTS=yourdomain.com
```

---

## Django Admin

Access at `/admin/` with a superuser account. Full management of Users, Pets, and Claims.

---

## Async Processing Notes

The background task (`claims/tasks.py`) uses Python `threading` for simplicity.
In a production setup, replace with **Celery + Redis/RabbitMQ**:

```python
# claims/tasks.py (Celery version)
from celery import shared_task

@shared_task
def process_claim(claim_id: int):
    ...
```

The task logic and state machine remain identical — only the execution mechanism changes.
