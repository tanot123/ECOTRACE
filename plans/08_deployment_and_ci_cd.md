# 08 — Deployment & CI/CD

> **Phase 8** | Estimated Effort: 1–2 days
> **Goal:** Deploy the frontend to Vercel, the backend to Render, configure CI/CD with GitHub Actions, and ensure all environment variables, CORS, and database connections are production-ready.

---

## 1. Objectives

- [ ] Deploy the Vue.js frontend to Vercel.
- [ ] Deploy the FastAPI backend to Render.
- [ ] Provision a PostgreSQL database on Render.
- [ ] Configure all environment variables in production.
- [ ] Set up CORS for production origins.
- [ ] Create a GitHub Actions CI pipeline.
- [ ] Verify end-to-end production connectivity.

---

## 2. Deployment Architecture

```mermaid
graph TB
    subgraph "GitHub Repository"
        GH["ecotrace-ai repo"]
        GH --> |"push to main"| V["Vercel Auto-Deploy"]
        GH --> |"push to main"| R["Render Auto-Deploy"]
        GH --> |"push to any branch"| GA["GitHub Actions CI"]
    end

    subgraph "Vercel (Frontend)"
        V --> VB["Build: npm run build"]
        VB --> VD["Serve: dist/ (static)"]
        VD --> VU["https://ecotrace.vercel.app"]
    end

    subgraph "Render (Backend)"
        R --> RB["Build: pip install -r requirements.txt"]
        RB --> RS["Start: uvicorn app.main:app"]
        RS --> RU["https://ecotrace-api.onrender.com"]
        RP["PostgreSQL Instance"] --> RS
    end

    subgraph "External"
        GEMINI["Google AI Studio API"]
    end

    VU -->|"API calls"| RU
    RS -->|"AI calls"| GEMINI
```

---

## 3. GitHub Student Developer Pack Benefits

The GitHub Student Developer Pack provides:

| Service | Benefit | How We Use It |
|---|---|---|
| **GitHub** | Unlimited private repos, Copilot access | Source control, CI/CD |
| **Vercel** | Hobby plan (free) | Frontend hosting |
| **Render** | Credits or free tier | Backend + PostgreSQL hosting |
| **Namecheap** | Free `.me` domain (1 year) | Custom domain (optional) |

---

## 4. Frontend Deployment (Vercel)

### 4.1 Step-by-Step

1. **Connect Repository:**
   - Go to [vercel.com](https://vercel.com) → Sign in with GitHub.
   - Click "New Project" → Import your `ecotrace-ai` repo.
   - Set **Root Directory** to `frontend` (since it's a monorepo).

2. **Build Configuration:**
   | Setting | Value |
   |---|---|
   | Framework Preset | Vite |
   | Build Command | `npm run build` |
   | Output Directory | `dist` |
   | Install Command | `npm install` |
   | Node.js Version | 18.x or 20.x |

3. **Environment Variables (Vercel Dashboard → Settings → Environment Variables):**
   | Variable | Value | Environment |
   |---|---|---|
   | `VITE_API_BASE_URL` | `https://ecotrace-api.onrender.com/api/v1` | Production |
   | `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | Preview/Development |

4. **Custom Domain (Optional):**
   - Vercel Dashboard → Settings → Domains.
   - Add `ecotrace.me` (if using Namecheap from Student Pack).
   - Vercel provides SSL automatically.

### 4.2 Vercel Configuration File (`frontend/vercel.json`)

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" }
      ]
    }
  ]
}
```

**Why the rewrite?** Vue Router uses client-side routing. Without this rewrite, refreshing a page like `/dashboard` would return a 404. The rewrite sends all routes to `index.html` where Vue Router handles them.

---

## 5. Backend Deployment (Render)

### 5.1 Step-by-Step

1. **Create a Web Service:**
   - Go to [render.com](https://render.com) → Sign in with GitHub.
   - New → Web Service → Connect your repo.
   - Set **Root Directory** to `backend`.

2. **Build & Start Configuration:**
   | Setting | Value |
   |---|---|
   | Runtime | Python 3 |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
   | Plan | Free (or Starter with Student credits) |
   | Auto-Deploy | Yes (on push to `main`) |

3. **Environment Variables (Render Dashboard → Service → Environment):**
   | Variable | Value |
   |---|---|
   | `DATABASE_URL` | (auto from Render PostgreSQL) |
   | `JWT_SECRET_KEY` | (generate a strong random key) |
   | `GEMINI_API_KEY` | (from Google AI Studio) |
   | `GEMINI_MODEL` | `gemini-2.0-flash` |
   | `CORS_ORIGINS` | `["https://ecotrace.vercel.app"]` |
   | `SEED_DATA` | `true` (first deploy), then `false` |
   | `PYTHON_VERSION` | `3.11.9` |

### 5.2 PostgreSQL on Render

1. **Create Database:**
   - Render Dashboard → New → PostgreSQL.
   - Name: `ecotrace-db`.
   - Plan: Free (256 MB, 90-day expiry — renew before expiry).
   - Region: Same as your Web Service.

2. **Connect to Web Service:**
   - Render auto-provides `DATABASE_URL` as an environment variable.
   - Format: `postgresql://user:pass@host:5432/ecotrace_db`

3. **Run Migrations on Deploy:**
   Add to build command:
   ```
   pip install -r requirements.txt && alembic upgrade head
   ```

### 5.3 Render Free Tier Considerations

| Limitation | Impact | Mitigation |
|---|---|---|
| Service spins down after 15 min inactivity | First request has 30s+ cold start | Add a loading screen, consider an uptime ping service |
| 256 MB database | Limited storage | Implement data retention (30 days) |
| 750 free hours/month | Sufficient for one service | Monitor usage |
| Database expires after 90 days | Data loss if not renewed | Set a calendar reminder |

### 5.4 Handling Cold Starts

The Render free tier spins down idle services. To improve UX:

1. **Frontend:** Show a "Waking up the server..." loading animation on the first API call.
2. **Health Check Ping:** Use a free uptime monitoring service (e.g., UptimeRobot) to ping `https://ecotrace-api.onrender.com/health` every 14 minutes — this prevents spin-down.
3. **Backend:** Optimize startup time — lazy-load heavy dependencies, minimize initialization work.

---

## 6. CORS Production Configuration

### 6.1 FastAPI CORS Setup

```
# In app/main.py — Production CORS settings:

Allowed Origins:
  - https://ecotrace.vercel.app
  - https://ecotrace.me (if custom domain)

Allowed Methods:
  - GET, POST, PUT, DELETE, OPTIONS

Allowed Headers:
  - Content-Type, Authorization, X-Requested-With

Allow Credentials: True
Max Age: 600 seconds (cache preflight for 10 min)
```

### 6.2 Common CORS Deployment Issues

| Issue | Symptom | Fix |
|---|---|---|
| Forgot to add Vercel URL to origins | All API calls fail with CORS error | Add exact production URL to `CORS_ORIGINS` |
| Trailing slash mismatch | `https://ecotrace.vercel.app/` ≠ `https://ecotrace.vercel.app` | Strip trailing slashes in comparison |
| Vercel preview URLs not in CORS | Preview deployments can't reach API | Add `*.vercel.app` for preview or use a wildcard only in staging |
| OPTIONS preflight not handled | PUT/DELETE requests fail | Ensure `OPTIONS` is in allowed methods |

---

## 7. GitHub Actions CI/CD

### 7.1 Workflow File: `.github/workflows/ci.yml`

```yaml
# Triggers: push to main, pull requests to main
# Jobs:
#
# 1. backend-lint-test:
#    - Python 3.11
#    - Install dependencies
#    - Run ruff (linter)
#    - Run pytest
#    - Services: postgres (for integration tests)
#
# 2. frontend-lint-build:
#    - Node.js 20
#    - npm ci
#    - Run eslint
#    - Run npm run build (catch build errors)
#    - Optionally run vitest
#
# Both jobs run in parallel.
# Deployment is handled by Vercel & Render auto-deploy, not by this CI.
```

### 7.2 CI Pipeline Flow

```mermaid
flowchart LR
    A["Push to<br/>any branch"] --> B["GitHub Actions<br/>Triggered"]
    B --> C["Backend Job"]
    B --> D["Frontend Job"]

    C --> C1["Install Python deps"]
    C1 --> C2["Ruff lint check"]
    C2 --> C3["Pytest (unit + integration)"]
    C3 --> C4["✅ / ❌"]

    D --> D1["npm ci"]
    D1 --> D2["ESLint check"]
    D2 --> D3["TypeScript type check"]
    D3 --> D4["npm run build"]
    D4 --> D5["✅ / ❌"]

    C4 & D5 --> E{"All pass?"}
    E -->|Yes| F["✅ PR can be merged"]
    E -->|No| G["❌ Fix required"]
```

### 7.3 Branch Protection Rules

Configure on GitHub (Settings → Branches → Branch protection rules → `main`):
- ✅ Require a pull request before merging.
- ✅ Require status checks to pass (select the CI jobs).
- ✅ Require branches to be up to date before merging.
- Optional: Require 1 reviewer (if working with a team).

---

## 8. Generating Secure Keys

### 8.1 JWT Secret Key

```bash
# Generate a cryptographically secure 256-bit key:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 8.2 Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click "Get API key" → "Create API key".
4. Copy the key → paste into Render environment variables.
5. **Never commit this key to Git.**

---

## 9. Pre-Deployment Checklist

### 9.1 Backend Checklist

| Item | Status |
|---|---|
| All environment variables set on Render | ☐ |
| `DATABASE_URL` points to Render PostgreSQL | ☐ |
| Alembic migrations run in build command | ☐ |
| CORS origins include Vercel production URL | ☐ |
| `DEBUG=false` in production config | ☐ |
| Health endpoint returns 200 | ☐ |
| No API keys in source code | ☐ |
| `requirements.txt` is up to date | ☐ |
| `.env` is in `.gitignore` | ☐ |

### 9.2 Frontend Checklist

| Item | Status |
|---|---|
| `VITE_API_BASE_URL` set on Vercel | ☐ |
| `vercel.json` has SPA rewrite rule | ☐ |
| `npm run build` succeeds locally | ☐ |
| No hardcoded `localhost` URLs in production code | ☐ |
| Environment variables use `import.meta.env.VITE_*` prefix | ☐ |
| Favicon and meta tags are set | ☐ |
| Loading/error states for slow API responses | ☐ |

### 9.3 Post-Deployment Verification

| Test | Expected Result |
|---|---|
| Visit Vercel URL | Vue app loads, login page visible |
| Visit Render URL `/health` | Returns `{"status": "healthy"}` |
| Visit Render URL `/docs` | Swagger UI loads |
| Register a new user from Vercel frontend | 201 response, redirects to dashboard |
| Login and view dashboard | Data loads (or shows onboarding if no data) |
| Scanner page loads camera | Permission prompt appears |
| Check browser console for CORS errors | No CORS errors |
| Check browser console for mixed content warnings | No HTTP-over-HTTPS warnings |

---

## 10. Monitoring & Logging

### 10.1 Render Logging

- Render provides built-in log streaming (Dashboard → Service → Logs).
- Add structured logging in FastAPI using Python's `logging` module.
- Log: API calls, errors, Gemini API latency, auth failures.

### 10.2 Error Tracking (Post-MVP)

Consider integrating **Sentry** (free tier) for error tracking:
- Backend: `sentry-sdk[fastapi]`
- Frontend: `@sentry/vue`

### 10.3 Uptime Monitoring

Set up a free uptime monitor:
- Use [UptimeRobot](https://uptimerobot.com) (free: 50 monitors, 5-min intervals).
- Monitor: `https://ecotrace-api.onrender.com/health`
- Benefit: Also prevents Render free tier spin-down.

---

## 11. Rollback Strategy

| Scenario | Action |
|---|---|
| Backend deploy breaks API | Render: Rollback to previous deploy in Dashboard → Deploys |
| Frontend deploy has UI bug | Vercel: Rollback to previous deployment in Dashboard → Deployments |
| Database migration breaks schema | `alembic downgrade -1` (requires SSH or Render Shell) |
| Environment variable misconfigured | Update in Render/Vercel Dashboard, redeploy |

---

## 12. Dependencies

| Dependency | Direction |
|---|---|
| **Phase 1–7** (All features) | ← Code must be functional before deploying |
| GitHub account | ← Repository hosting |
| Vercel account | ← Frontend hosting |
| Render account | ← Backend + DB hosting |
| Google AI Studio account | ← Gemini API key |

> **Note:** While this is listed as Phase 8, you can (and should) set up the deployment pipeline early — even in Phase 1 — with a minimal "Hello World" app. This validates the infrastructure before feature code is added.

---

> **Next:** Proceed to [09_testing_and_polish.md](./09_testing_and_polish.md) for the testing strategy and final MVP polish.
