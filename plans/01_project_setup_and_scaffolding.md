# 01 — Project Setup & Scaffolding

> **Phase 1** | Estimated Effort: 2–3 days
> **Goal:** Establish the monorepo structure, scaffold both frontend and backend, configure the database, and ensure both services communicate locally.

---

## 1. Objectives

- [x] Define the monorepo folder structure.
- [ ] Scaffold the Vue 3 + Vite frontend with TypeScript.
- [ ] Scaffold the FastAPI backend with proper project layout.
- [ ] Set up PostgreSQL locally and configure SQLAlchemy + Alembic.
- [ ] Verify end-to-end connectivity (Vue ↔ FastAPI ↔ PostgreSQL).
- [ ] Configure linting, formatting, and environment variable management.

---

## 2. Monorepo Folder Structure

```
ecotrace-ai/
├── frontend/                   # Vue.js SPA
│   ├── public/
│   │   └── favicon.ico
│   ├── src/
│   │   ├── assets/             # Static assets (images, fonts)
│   │   ├── components/         # Reusable Vue components
│   │   │   ├── common/         # Buttons, Cards, Modals
│   │   │   ├── dashboard/      # Dashboard-specific components
│   │   │   ├── scanner/        # Camera/scanning components
│   │   │   └── scheduler/      # Scheduling components
│   │   ├── composables/        # Vue composables (useAuth, useEnergy, etc.)
│   │   ├── layouts/            # App layouts (MainLayout, AuthLayout)
│   │   ├── pages/              # Route-level page components
│   │   │   ├── DashboardPage.vue
│   │   │   ├── ScannerPage.vue
│   │   │   ├── SchedulerPage.vue
│   │   │   ├── ChallengesPage.vue
│   │   │   ├── LoginPage.vue
│   │   │   └── RegisterPage.vue
│   │   ├── router/             # Vue Router configuration
│   │   │   └── index.ts
│   │   ├── stores/             # Pinia stores
│   │   │   ├── auth.ts
│   │   │   ├── energy.ts
│   │   │   ├── scanner.ts
│   │   │   └── dashboard.ts
│   │   ├── services/           # API service layer (Axios)
│   │   │   ├── api.ts          # Base Axios instance
│   │   │   ├── authService.ts
│   │   │   ├── energyService.ts
│   │   │   └── scanService.ts
│   │   ├── types/              # TypeScript interfaces
│   │   │   └── index.ts
│   │   ├── utils/              # Helper functions
│   │   ├── App.vue
│   │   └── main.ts
│   ├── .env.development
│   ├── .env.production
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── eslint.config.js
│
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app entry point
│   │   ├── config.py           # Settings / environment config
│   │   ├── database.py         # SQLAlchemy engine & session
│   │   ├── dependencies.py     # Dependency injection (get_db, get_current_user)
│   │   ├── models/             # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── appliance.py
│   │   │   ├── reading.py
│   │   │   ├── scan.py
│   │   │   ├── schedule.py
│   │   │   └── challenge.py
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── energy.py
│   │   │   ├── scan.py
│   │   │   └── schedule.py
│   │   ├── routers/            # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── energy.py
│   │   │   ├── scan.py
│   │   │   ├── schedule.py
│   │   │   ├── challenges.py
│   │   │   └── dashboard.py
│   │   ├── services/           # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── energy_service.py
│   │   │   ├── gemini_service.py   # Gemini API wrapper
│   │   │   ├── scan_service.py
│   │   │   ├── schedule_service.py
│   │   │   └── challenge_service.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── security.py     # JWT helpers, password hashing
│   │   │   └── rate_limiter.py
│   │   └── seeds/              # Mock data seeders
│   │       ├── __init__.py
│   │       ├── seed_appliances.py
│   │       ├── seed_readings.py
│   │       └── seed_challenges.py
│   ├── alembic/                # Database migrations
│   │   ├── versions/
│   │   ├── env.py
│   │   └── alembic.ini
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   └── test_energy.py
│   ├── .env
│   ├── .env.example
│   ├── requirements.txt
│   ├── Dockerfile              # For Render deployment
│   └── pyproject.toml
│
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI
│
├── .gitignore
├── README.md
└── docker-compose.yml          # Local dev (PostgreSQL + backend)
```

---

## 3. Frontend Scaffolding

### 3.1 Initialize Vue Project

```bash
# From the project root
npx -y create-vite@latest frontend -- --template vue-ts
cd frontend
npm install
```

### 3.2 Install Core Dependencies

| Package | Purpose |
|---|---|
| `vue-router@4` | Client-side routing |
| `pinia` | State management |
| `axios` | HTTP client |
| `chart.js` + `vue-chartjs` | Dashboard charts |
| `@vueuse/core` | Utility composables (useMediaQuery, useLocalStorage) |

### 3.3 Install Dev Dependencies

| Package | Purpose |
|---|---|
| `@vitejs/plugin-vue` | Already included by Vite template |
| `eslint` + `@vue/eslint-config-typescript` | Linting |
| `prettier` | Code formatting |
| `sass` | SCSS support |

### 3.4 Vite Configuration Notes

- Set up a **proxy** in `vite.config.ts` for local development so API calls to `/api` get forwarded to `localhost:8000`. This avoids CORS issues during development.
- Configure **environment variables** with the `VITE_` prefix:
  - `VITE_API_BASE_URL` — Backend API URL.

### 3.5 Axios Base Instance

Create `src/services/api.ts`:
- Set `baseURL` from `import.meta.env.VITE_API_BASE_URL`.
- Add a **request interceptor** to attach the JWT `Authorization: Bearer <token>` header.
- Add a **response interceptor** to handle 401 errors (redirect to login).

---

## 4. Backend Scaffolding

### 4.1 Initialize Python Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install fastapi uvicorn[standard] sqlalchemy[asyncio] alembic psycopg2-binary
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
pip install google-generativeai python-dotenv pydantic-settings
pip install ruff pytest httpx  # Dev tools
pip freeze > requirements.txt
```

### 4.2 FastAPI App Entry Point (`app/main.py`)

The main application file must:
1. Create the FastAPI app instance with metadata (title, description, version).
2. Add `CORSMiddleware` with allowed origins:
   - `http://localhost:5173` (Vite dev server)
   - `https://ecotrace.vercel.app` (production frontend)
3. Include all routers with the `/api/v1` prefix.
4. Add a health-check endpoint at `GET /health`.
5. Optionally run the data seeder on startup (controlled by an env flag).

### 4.3 Configuration (`app/config.py`)

Use `pydantic-settings` `BaseSettings` to load environment variables:

| Variable | Type | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | `str` | — | PostgreSQL connection string |
| `JWT_SECRET_KEY` | `str` | — | Secret for signing JWT tokens |
| `JWT_ALGORITHM` | `str` | `HS256` | JWT algorithm |
| `JWT_EXPIRY_MINUTES` | `int` | `1440` (24h) | Token expiry |
| `GEMINI_API_KEY` | `str` | — | Google AI Studio API key |
| `GEMINI_MODEL` | `str` | `gemini-2.0-flash` | Model to use |
| `CORS_ORIGINS` | `list[str]` | `["http://localhost:5173"]` | Allowed CORS origins |
| `SEED_DATA` | `bool` | `False` | Whether to seed mock data on startup |

### 4.4 Database Setup (`app/database.py`)

- Create the SQLAlchemy **engine** from `DATABASE_URL`.
- Create a **session factory** using `sessionmaker`.
- Define a `get_db` dependency that yields a session and handles cleanup.
- Create a `Base` declarative base for models.

---

## 5. Database Setup

### 5.1 Local PostgreSQL (Docker)

Create `docker-compose.yml`:

```yaml
# Docker Compose to run PostgreSQL locally
# Service: postgres
#   Image: postgres:16-alpine
#   Port: 5432
#   Environment:
#     POSTGRES_DB: ecotrace_dev
#     POSTGRES_USER: ecotrace
#     POSTGRES_PASSWORD: ecotrace_local
#   Volume: pgdata for persistence
```

### 5.2 Alembic Migrations

```bash
cd backend
alembic init alembic
```

- Configure `alembic/env.py` to read `DATABASE_URL` from your config.
- Point `target_metadata` at `Base.metadata` from your models.
- After creating models, generate the initial migration:
  ```bash
  alembic revision --autogenerate -m "initial schema"
  alembic upgrade head
  ```

---

## 6. Verification Checklist

Before moving to Phase 2, confirm:

| Test | Expected Result |
|---|---|
| `cd frontend && npm run dev` | Vite serves on `http://localhost:5173` |
| `cd backend && uvicorn app.main:app --reload` | FastAPI serves on `http://localhost:8000` |
| Visit `http://localhost:8000/docs` | Swagger UI loads with health endpoint |
| Visit `http://localhost:8000/health` | Returns `{"status": "healthy"}` |
| Frontend makes GET to `/api/v1/health` via proxy | Returns 200 OK |
| `alembic upgrade head` | Tables created in PostgreSQL |
| `docker compose up -d` | PostgreSQL container running |

---

## 7. Environment File Templates

### `backend/.env.example`
```
DATABASE_URL=postgresql://ecotrace:ecotrace_local@localhost:5432/ecotrace_dev
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=1440
GEMINI_API_KEY=your-google-ai-studio-api-key
GEMINI_MODEL=gemini-2.0-flash
CORS_ORIGINS=["http://localhost:5173"]
SEED_DATA=true
```

### `frontend/.env.development`
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### `frontend/.env.production`
```
VITE_API_BASE_URL=https://ecotrace-api.onrender.com/api/v1
```

---

## 8. Edge Cases & Gotchas

| Issue | Solution |
|---|---|
| PostgreSQL not running when backend starts | Add retry logic or clear error message in `database.py` |
| Vite proxy not forwarding to backend | Ensure `server.proxy` config matches API prefix exactly |
| `psycopg2` install fails on Windows | Use `psycopg2-binary` instead of `psycopg2` |
| Alembic can't find models | Ensure all model files are imported in `models/__init__.py` |
| Port conflicts (5173 or 8000 already in use) | Configure alternative ports via env variables |

---

> **Next:** Proceed to [02_authentication_and_user_management.md](./02_authentication_and_user_management.md) to implement user registration and JWT authentication.
