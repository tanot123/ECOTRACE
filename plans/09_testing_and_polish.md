# 09 — Testing & Polish

> **Phase 9** | Estimated Effort: 2–3 days
> **Goal:** Establish a comprehensive testing strategy, fix remaining bugs, polish the UI/UX, handle edge cases, and ensure the MVP is demo-ready.

---

## 1. Objectives

- [ ] Write unit tests for backend services (auth, green score, energy, challenges).
- [ ] Write integration tests for API endpoints.
- [ ] Set up frontend component testing (optional for MVP, but recommended).
- [ ] Perform end-to-end manual testing of all user flows.
- [ ] Polish the UI with animations, loading states, and error boundaries.
- [ ] Optimize performance (bundle size, API response times, image compression).
- [ ] Conduct a security review.

---

## 2. Testing Strategy Overview

```mermaid
pyramid
    title Testing Pyramid
    "E2E Tests (Manual)" : 10
    "Integration Tests (API)" : 30
    "Unit Tests (Services)" : 60
```

| Layer | Tool | Coverage Target | Focus |
|---|---|---|---|
| Unit Tests | `pytest` | 70%+ of services | Business logic, score calculation, data validation |
| Integration Tests | `pytest` + `httpx` (async) | All API endpoints | Request/response contracts, auth flows, error handling |
| Frontend Tests | `vitest` + `@vue/test-utils` | Critical components | Chart rendering, form validation, store logic |
| E2E Tests | Manual (MVP) | All user flows | Registration → Dashboard → Scanner → Scheduler → Challenges |

---

## 3. Backend Unit Tests

### 3.1 Test Configuration (`tests/conftest.py`)

```
# Fixtures to set up:
# - test_db: Create a temporary test database (SQLite in-memory for speed)
# - test_client: AsyncClient(app) for API testing
# - test_user: Pre-created user with hashed password
# - test_token: Valid JWT for the test_user
# - seeded_appliances: User with 12 default appliances
# - seeded_readings: User with 30 days of energy readings
```

### 3.2 Auth Service Tests (`tests/test_auth.py`)

| Test | Assertion |
|---|---|
| `test_hash_password` | Hashed password is not plaintext, is bcrypt format |
| `test_verify_password_correct` | `verify_password(plain, hash) == True` |
| `test_verify_password_wrong` | `verify_password(wrong, hash) == False` |
| `test_create_token` | Token is valid JWT, contains `sub` and `exp` claims |
| `test_decode_token_valid` | Returns correct `sub` value |
| `test_decode_token_expired` | Raises `ExpiredSignatureError` |
| `test_decode_token_invalid` | Raises `JWTError` |

### 3.3 Green Score Service Tests (`tests/test_green_score.py`)

| Test | Assertion |
|---|---|
| `test_score_range` | Score is always between 0 and 100 |
| `test_perfect_score` | All factors at maximum → score = 100 |
| `test_zero_score` | All factors at minimum → score ≥ 0 |
| `test_energy_factor_below_baseline` | Lower usage → higher score |
| `test_energy_factor_above_baseline` | Higher usage → lower score |
| `test_challenge_factor` | 3/5 challenges completed → factor = 0.6 |
| `test_scan_factor_capped` | 15 scans → factor = 1.0 (capped at 10) |
| `test_weights_sum_to_one` | All factor weights sum to 1.0 |
| `test_new_user_score` | New user with no data → reasonable default (not 0) |

### 3.4 Energy Service Tests (`tests/test_energy.py`)

| Test | Assertion |
|---|---|
| `test_daily_aggregation` | Sum of readings matches expected daily total |
| `test_vampire_detection` | Devices with standby > 5W flagged |
| `test_vampire_yearly_cost` | Cost calculation matches formula |
| `test_appliance_breakdown` | Percentages sum to 100% |
| `test_realtime_returns_latest` | Returns most recent readings |
| `test_date_range_filtering` | Only readings within range returned |

### 3.5 Challenge Service Tests (`tests/test_challenges.py`)

| Test | Assertion |
|---|---|
| `test_assign_challenge` | Creates UserChallenge with correct data |
| `test_max_active_limit` | 4th challenge assignment raises error |
| `test_progress_evaluation_energy` | Correct % calculated from readings |
| `test_progress_evaluation_scans` | Count matches actual scans |
| `test_challenge_completion` | Status set to "completed", points awarded |
| `test_challenge_expiry` | Expired challenge marked as "expired" |
| `test_cooldown_period` | Completed challenge can't be re-assigned within 14 days |

---

## 4. Backend Integration Tests

### 4.1 Auth API Tests (`tests/test_api_auth.py`)

| Test | HTTP Call | Expected |
|---|---|---|
| Register success | `POST /auth/register` | 201, token in response |
| Register duplicate email | `POST /auth/register` | 409 |
| Register invalid email | `POST /auth/register` | 422 |
| Login success | `POST /auth/login` | 200, token in response |
| Login wrong password | `POST /auth/login` | 401 |
| Get profile (authenticated) | `GET /users/me` + Bearer token | 200, user data |
| Get profile (no token) | `GET /users/me` | 401 |
| Get profile (expired token) | `GET /users/me` + expired token | 401 |

### 4.2 Energy API Tests (`tests/test_api_energy.py`)

| Test | HTTP Call | Expected |
|---|---|---|
| List appliances | `GET /energy/appliances` | 200, array of appliances |
| Create appliance | `POST /energy/appliances` | 201, appliance data |
| Get readings (7 days) | `GET /energy/readings?range=7d` | 200, array with correct date range |
| Get vampires | `GET /energy/vampires` | 200, only vampire devices |
| Unauthorized access | `GET /energy/appliances` (no token) | 401 |
| User isolation | User A can't see User B's appliances | 404 or empty array |

### 4.3 Scan API Tests (`tests/test_api_scan.py`)

| Test | HTTP Call | Expected |
|---|---|---|
| Scan with valid image | `POST /scan/analyze` + image | 200, analysis result |
| Scan with too-large image | `POST /scan/analyze` + 10MB file | 413 |
| Scan with invalid file type | `POST /scan/analyze` + .txt file | 400 |
| Scan history | `GET /scan/history` | 200, array of past scans |
| Rate limiting | 20 scans in 1 minute | 429 after limit |

### 4.4 Dashboard API Tests (`tests/test_api_dashboard.py`)

| Test | HTTP Call | Expected |
|---|---|---|
| Full dashboard summary | `GET /dashboard/summary` | 200, all sections populated |
| Dashboard with no data | `GET /dashboard/summary` (new user) | 200, zeros/empty arrays (no crash) |

---

## 5. Frontend Testing

### 5.1 Setup: Vitest + Vue Test Utils

```
# Install:
npm install -D vitest @vue/test-utils jsdom @testing-library/vue
```

### 5.2 Component Tests (Priority)

| Component | Test | Assertion |
|---|---|---|
| `StatCard.vue` | Renders with props | Displays label, value, trend correctly |
| `GreenScoreGauge.vue` | Renders score | Shows correct score, correct color band |
| `ChallengeCard.vue` | Active state | Shows progress bar, time remaining |
| `ChallengeCard.vue` | Completed state | Shows checkmark, points earned |
| `ScanResultCard.vue` | Recyclable item | Shows green badge, recycling instructions |
| `ScanResultCard.vue` | Non-recyclable item | Shows red badge, alternative disposal |

### 5.3 Store Tests (Pinia)

| Store | Test | Assertion |
|---|---|---|
| `auth.ts` | Login stores token | `authStore.token` is set, `isAuthenticated` is true |
| `auth.ts` | Logout clears state | `authStore.token` is null, user is null |
| `dashboard.ts` | Fetch populates state | `dashboardStore.summary` is not null |

---

## 6. End-to-End Manual Testing

### 6.1 Critical User Flows

Test each flow completely in the deployed production environment:

**Flow 1: New User Onboarding**
```
1. Open app → see login page
2. Click "Register" → fill form → submit
3. Redirected to dashboard
4. Dashboard shows onboarding state (no data yet)
5. Mock data is seeded → refresh → see dashboard with data
```

**Flow 2: Dashboard Exploration**
```
1. Login → see dashboard
2. Verify Green Score gauge renders
3. Verify stat cards show correct values
4. Click different time ranges (7d, 30d)
5. Verify charts update
6. Check energy vampire alerts display
7. Check active challenges preview
```

**Flow 3: Receipt Scanning**
```
1. Navigate to Scanner page
2. Select "Receipt" scan type
3. Upload a photo of a grocery receipt
4. Wait for analysis (loading state visible)
5. See itemized recycling results
6. Check scan appears in history
```

**Flow 4: Smart Scheduling**
```
1. Navigate to Scheduler page
2. See grid forecast timeline
3. See appliance recommendations
4. Accept a recommendation
5. Verify it moves to "Accepted" section
6. Check it reflects on dashboard
```

**Flow 5: Challenges**
```
1. Navigate to Challenges page
2. See available challenges
3. Start a challenge
4. Check progress updates on dashboard
5. Complete a challenge (may require time or data manipulation for testing)
6. Verify points awarded
```

### 6.2 Cross-Browser Testing

| Browser | Minimum Version | Test Focus |
|---|---|---|
| Chrome | 100+ | Primary development browser |
| Firefox | 100+ | CSS compatibility, camera API |
| Safari (iOS) | 15+ | Mobile camera, PWA behavior |
| Edge | 100+ | General compatibility |

### 6.3 Mobile Responsiveness Testing

| Device Size | Test |
|---|---|
| iPhone SE (375px) | Layout doesn't overflow, navigation works |
| iPhone 14 (390px) | Charts resize, cards stack vertically |
| iPad (768px) | 2-column layout activates |
| Desktop (1440px) | Sidebar + 3-column grid |

---

## 7. UI/UX Polish

### 7.1 Loading States

Every API-dependent view must have:
- **Skeleton loaders** for initial data fetch (not just spinners).
- **Inline loading** for actions (button shows spinner while submitting).
- **Optimistic updates** where possible (mark challenge as accepted immediately, rollback on error).

### 7.2 Error States

- **Network error:** Full-page error with retry button.
- **API error (500):** Toast notification with error message.
- **Validation error (422):** Field-level error messages.
- **Not found (404):** Custom 404 page.
- **Rate limited (429):** Toast with "Try again in X seconds."

### 7.3 Empty States

Every list/grid must have a designed empty state:
- Dashboard with no data → onboarding wizard.
- No scan history → "Scan your first item!" with illustration.
- No active challenges → "Start a challenge to boost your Green Score!"
- No scheduling recommendations → "Add appliances to get smart schedules."

### 7.4 Animations & Transitions

| Element | Animation |
|---|---|
| Page transitions | Fade (200ms) via Vue `<Transition>` |
| Chart data updates | Chart.js built-in animations (800ms) |
| Green Score gauge | Count-up animation on load (1.5s) |
| Stat cards | Staggered fade-in on dashboard load |
| Challenge completion | Confetti/celebration animation |
| Toast notifications | Slide-in from top-right, auto-dismiss (5s) |
| Skeleton loaders | Shimmer effect |
| Card hover | Subtle scale(1.02) + shadow increase |

### 7.5 Accessibility (A11y)

| Requirement | Implementation |
|---|---|
| Keyboard navigation | All interactive elements focusable |
| Color contrast | Minimum 4.5:1 ratio (WCAG AA) |
| Screen reader | ARIA labels on icons, charts, gauges |
| Focus indicators | Visible focus rings on all controls |
| Alt text | All images have descriptive alt text |
| Form labels | All inputs have associated `<label>` elements |

---

## 8. Performance Optimization

### 8.1 Frontend

| Optimization | Implementation |
|---|---|
| Code splitting | Vue Router lazy loading (`() => import('...')`) |
| Bundle analysis | `npx vite-bundle-visualizer` — identify large deps |
| Image optimization | Compress all static images, use WebP format |
| API caching | Cache dashboard data in Pinia for 5 minutes |
| Debounce | Debounce search inputs, scan submissions |
| Font loading | `font-display: swap` to prevent FOIT |

### 8.2 Backend

| Optimization | Implementation |
|---|---|
| Database indexes | On `user_id`, `recorded_at`, `appliance_id` |
| Query optimization | Use eager loading for relationships, avoid N+1 |
| Response compression | Enable GZip middleware in FastAPI |
| Gemini response caching | Cache scan/schedule results (see Phase 5/6) |
| Pagination | All list endpoints paginated (default 20, max 100) |
| Connection pooling | SQLAlchemy pool settings: `pool_size=5, max_overflow=10` |

---

## 9. Security Review Checklist

| Item | Status | Notes |
|---|---|---|
| No API keys in source code | ☐ | Grep for key patterns |
| `.env` files in `.gitignore` | ☐ | Verify |
| JWT secret is strong (256-bit) | ☐ | Verify key length |
| Passwords hashed with bcrypt | ☐ | Never stored plain |
| SQL injection prevention | ☐ | Using ORM (SQLAlchemy), no raw SQL |
| XSS prevention | ☐ | Vue auto-escapes, no `v-html` with user input |
| CORS properly configured | ☐ | Only production origin allowed |
| Rate limiting on auth endpoints | ☐ | 5 attempts/min/IP |
| Rate limiting on Gemini endpoints | ☐ | Matches free tier limits |
| Input validation on all endpoints | ☐ | Pydantic schemas |
| File upload validation | ☐ | Check MIME type, max size, extension |
| HTTPS enforced | ☐ | Vercel + Render default to HTTPS |
| No sensitive data in error responses | ☐ | Generic errors in production |
| Content-Security-Policy header | ☐ | Set in `vercel.json` |

---

## 10. Demo Preparation

### 10.1 Demo Script

Prepare a scripted demo flow:
1. **Open app** → Show the landing/login page design.
2. **Register/Login** → Show the auth flow.
3. **Dashboard overview** → Walk through Green Score, stat cards, charts.
4. **Energy vampires** → Show detected vampires with yearly cost.
5. **Scanner demo** → Scan a real receipt or product packaging live.
6. **Scheduler** → Show the timeline and AI recommendations.
7. **Challenges** → Start and show progress on a challenge.
8. **Mobile view** → Show responsive design on a phone.

### 10.2 Demo Data

- Pre-seed the demo account with 30 days of realistic data.
- Ensure some challenges are partially complete (for visual progress bars).
- Have a few scan results in history.
- Have scheduling recommendations ready.

### 10.3 Fallback Plan

- If Gemini API is down: Show cached/pre-computed scan results.
- If Render is cold-starting: Have screenshots/screen recording ready.
- If camera doesn't work in demo: Have pre-captured images ready to upload.

---

## 11. Known Limitations (MVP)

Document these transparently:

| Limitation | Why | Post-MVP Plan |
|---|---|---|
| IoT data is mocked | No real hardware | Integrate with Home Assistant, SmartThings APIs |
| Single household only | MVP scope | Add multi-household, family member support |
| No push notifications | Complexity | Add via Firebase Cloud Messaging |
| No real-time updates | Uses polling | Implement WebSocket or SSE |
| English only | MVP scope | Add i18n with vue-i18n |
| No data export | MVP scope | Add CSV/PDF export |
| Render cold starts | Free tier | Upgrade to paid plan |
| No offline support | MVP scope | Add PWA with service worker |

---

## 12. Post-MVP Roadmap (Future Phases)

| Phase | Feature | Priority |
|---|---|---|
| 10 | Real IoT integration (Home Assistant / SmartThings) | High |
| 11 | Multi-language support (i18n) | Medium |
| 12 | Community & social features (compare with neighbors) | Medium |
| 13 | Push notifications & reminders | Medium |
| 14 | PWA / offline mode | Low |
| 15 | Data export & reporting (monthly PDF reports) | Low |
| 16 | Smart home automation triggers (IFTTT integration) | Low |
| 17 | Carbon offset marketplace integration | Stretch |

---

> **You've reached the end of the planning documents.** 🎉
> 
> Return to [00_general_thinking_and_architecture.md](./00_general_thinking_and_architecture.md) for the full overview, then begin coding with Phase 1.
