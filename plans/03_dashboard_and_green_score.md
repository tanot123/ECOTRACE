# 03 — Personal Dashboard & Green Score

> **Phase 3** | Estimated Effort: 3–4 days
> **Goal:** Build the central dashboard that displays real-time energy usage, water consumption, CO₂ impact, Green Score progress, and active sustainability challenges.

---

## 1. Objectives

- [ ] Design and implement the main dashboard layout with responsive grid.
- [ ] Build reusable chart components (line, bar, doughnut) for energy/water data.
- [ ] Implement the Green Score calculation engine on the backend.
- [ ] Create the aggregated dashboard API endpoint.
- [ ] Build stat cards for key metrics (CO₂ reduced, water saved, money saved).
- [ ] Add a quick-view of active challenges and energy vampire alerts.

---

## 2. Dashboard Layout

### 2.1 Wireframe Description

```
┌─────────────────────────────────────────────────────────┐
│  SIDEBAR NAV          │        MAIN CONTENT AREA         │
│                       │                                   │
│  🏠 Dashboard (active)│  ┌─────────┬─────────┬─────────┐│
│  📸 Scanner           │  │ Green   │ CO₂     │ Water   ││
│  📅 Scheduler         │  │ Score   │ Reduced │ Saved   ││
│  🏆 Challenges        │  │  78/100 │ 12.4 kg │ 340 L   ││
│  ⚙️ Settings          │  └─────────┴─────────┴─────────┘│
│                       │                                   │
│  ─────────────────    │  ┌──────────────────────────────┐│
│  USER PROFILE CARD    │  │  ENERGY USAGE LINE CHART     ││
│  Name: Jane Doe       │  │  (7-day trend, kWh)          ││
│  Green Score: 78      │  │  ~~~~~~~~~~~~~~~~~~~~~~~~    ││
│  Member since: 2026   │  └──────────────────────────────┘│
│                       │                                   │
│                       │  ┌──────────────┬───────────────┐│
│                       │  │ APPLIANCE    │ ENERGY        ││
│                       │  │ BREAKDOWN    │ VAMPIRES      ││
│                       │  │ (Doughnut)   │ (Alert List)  ││
│                       │  └──────────────┴───────────────┘│
│                       │                                   │
│                       │  ┌──────────────────────────────┐│
│                       │  │  ACTIVE CHALLENGES (3 cards) ││
│                       │  └──────────────────────────────┘│
└───────────────────────┴───────────────────────────────────┘
```

### 2.2 Responsive Behavior

| Breakpoint | Layout Change |
|---|---|
| Desktop (>1024px) | Sidebar visible, 3-column stat grid |
| Tablet (768–1024px) | Sidebar collapses to icons, 2-column stat grid |
| Mobile (<768px) | Bottom nav bar replaces sidebar, single column, swipeable charts |

---

## 3. Dashboard API Endpoint

### 3.1 Aggregated Dashboard Endpoint

**`GET /api/v1/dashboard/summary`**

This single endpoint returns all data needed to render the dashboard in one call, avoiding multiple round trips.

**Response Schema:**
```
DashboardSummary:
  green_score:
    current: float (0-100)
    trend: "up" | "down" | "stable"
    change_from_last_week: float

  impact:
    co2_reduced_kg: float
    water_saved_liters: float
    money_saved_usd: float
    trees_equivalent: float (CO₂ / 21.77 kg per tree/year)

  energy:
    today_kwh: float
    week_total_kwh: float
    month_total_kwh: float
    daily_trend: [ { date: str, kwh: float } ]  # Last 7 days
    by_appliance: [ { name: str, kwh: float, percentage: float } ]

  water:
    today_liters: float
    week_total_liters: float
    daily_trend: [ { date: str, liters: float } ]

  energy_vampires:
    count: int
    devices: [ { name: str, standby_watts: float, yearly_cost: float } ]

  active_challenges:
    count: int
    challenges: [ { id: str, title: str, progress: float, target: float, unit: str } ]
    # Max 3, ordered by closest to completion

  period:
    start: datetime
    end: datetime
    timezone: str
```

### 3.2 Additional Dashboard Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/dashboard/summary` | Full dashboard data (above) |
| GET | `/api/v1/dashboard/energy-history?range=7d\|30d\|90d` | Extended historical data for charts |
| GET | `/api/v1/dashboard/comparison` | Compare current period vs. previous period |

---

## 4. Green Score Engine

### 4.1 What is the Green Score?

A gamified score from **0 to 100** that reflects the household's overall sustainability performance. It updates daily based on multiple weighted factors.

### 4.2 Scoring Algorithm

```
Green Score = Σ (Factor Weight × Factor Score)

Each Factor Score is normalized to 0.0 – 1.0
```

| Factor | Weight | Scoring Logic |
|---|---|---|
| **Energy Efficiency** | 30% | Compare daily kWh to household baseline. Lower = better. Score = max(0, 1 - (actual / baseline)). |
| **Water Conservation** | 20% | Compare daily liters to baseline (avg US household: ~300L/day). |
| **Vampire Elimination** | 15% | Ratio of energy vampires addressed to total vampires detected. |
| **Challenge Completion** | 20% | Ratio of completed challenges to available challenges in the current period. |
| **Scanning Activity** | 10% | Number of items scanned for recycling this week (max 10 scans = 1.0). |
| **Schedule Adherence** | 5% | Ratio of accepted scheduling recommendations followed. |

### 4.3 Baseline Calculation

The **baseline** is established during the user's first week of data:
- Average daily kWh consumption.
- Average daily water liters.
- After 7 days, the baseline is "locked" and used for comparison.
- Baselines can be recalculated monthly to account for seasonal changes.

### 4.4 Backend Implementation (`app/services/green_score_service.py`)

```
class GreenScoreService:
    """
    Methods:
    - calculate_score(user_id) → float
      Fetches all relevant data, computes each factor,
      applies weights, returns 0-100 score.

    - get_factor_breakdown(user_id) → dict
      Returns individual factor scores for UI display.

    - update_daily_score(user_id)
      Called by a daily job (or on dashboard load) to
      recalculate and persist the score.
    """
```

### 4.5 Score Persistence

- Store the current `green_score` on the `users` table for quick access.
- Store daily score snapshots in a `score_history` table for trend charts:
  ```
  SCORE_HISTORY:
    id: UUID
    user_id: UUID FK
    score: float
    factor_breakdown: JSONB
    recorded_date: date
  ```

---

## 5. Chart Components

### 5.1 Component Library

Build these reusable Vue chart wrapper components using `vue-chartjs`:

| Component | Chart Type | Data Source | Usage |
|---|---|---|---|
| `EnergyTrendChart.vue` | Line | `energy.daily_trend` | 7/30/90-day energy usage trend |
| `WaterTrendChart.vue` | Line | `water.daily_trend` | Water usage trend |
| `ApplianceBreakdownChart.vue` | Doughnut | `energy.by_appliance` | Which appliances use the most energy |
| `GreenScoreGauge.vue` | Custom (SVG) | `green_score.current` | Animated gauge/ring showing score |
| `ComparisonBarChart.vue` | Bar | `comparison` endpoint | This week vs. last week |

### 5.2 Chart Design Guidelines

- Use a **consistent color palette** across all charts:
  - Primary: `#10B981` (emerald green — eco theme)
  - Secondary: `#3B82F6` (blue — water)
  - Warning: `#F59E0B` (amber — energy vampires)
  - Danger: `#EF4444` (red — high usage alerts)
  - Neutral: `#6B7280` (gray — baselines)
- **Animations:** Enable Chart.js animations with 800ms duration on initial render.
- **Tooltips:** Show exact values on hover with proper units (kWh, L, $).
- **Responsive:** All charts must resize with their container.
- **Dark mode compatible:** Use CSS variables for chart colors.

### 5.3 Green Score Gauge Component

This is a **custom SVG component** (not Chart.js):
- A circular ring/arc that fills based on the score (0–100).
- Color gradient based on score:
  - 0–30: Red gradient
  - 31–60: Amber gradient
  - 61–80: Light green gradient
  - 81–100: Deep green gradient
- Animated counter that counts up to the current score on load.
- Score label in the center with trend arrow (↑/↓/→).

---

## 6. Stat Cards

### 6.1 StatCard Component

A reusable `StatCard.vue` component with:
- **Icon** (emoji or SVG icon)
- **Label** (e.g., "CO₂ Reduced")
- **Value** (e.g., "12.4 kg")
- **Trend indicator** (up/down arrow + percentage change)
- **Color theme** (matches the metric's color from the palette)

### 6.2 Metrics Calculations

| Metric | Formula | Source |
|---|---|---|
| CO₂ Reduced | `(baseline_kwh - actual_kwh) × 0.417 kg CO₂/kWh` | US EPA grid average emission factor |
| Water Saved | `baseline_liters - actual_liters` | Compared to household baseline |
| Money Saved | `(baseline_kwh - actual_kwh) × local_rate_per_kwh` | Default: $0.12/kWh (configurable) |
| Trees Equivalent | `co2_reduced_kg / 21.77` | Average CO₂ absorbed by one tree per year |

---

## 7. Energy Vampire Alert Section

### 7.1 What It Shows

A panel listing devices detected as "energy vampires" — appliances that consume significant power in standby mode.

### 7.2 Detection Logic (Backend)

An appliance is flagged as an energy vampire if:
- `standby_watts > 5W` **AND**
- `standby_hours_per_day > 16 hours` (i.e., it's mostly on standby)
- Calculate `yearly_vampire_cost = standby_watts × 24 × 365 / 1000 × rate_per_kwh`

### 7.3 UI Display

Each vampire device card shows:
- Device name and icon
- Standby wattage
- Estimated yearly cost of vampire draw
- A suggested action (e.g., "Use a smart power strip" or "Unplug when not in use")
- A "Mark as resolved" button (contributes to Green Score)

---

## 8. Active Challenges Preview

The dashboard shows the **top 3 active challenges** as compact progress cards:
- Challenge title
- Progress bar (current / target)
- Days remaining
- Points reward

This is a preview — full challenge management is in Phase 7.

---

## 9. Frontend Store: Dashboard (`stores/dashboard.ts`)

| State | Type |
|---|---|
| `summary` | `DashboardSummary \| null` |
| `isLoading` | `boolean` |
| `error` | `string \| null` |
| `selectedRange` | `"7d" \| "30d" \| "90d"` |

| Action | Description |
|---|---|
| `fetchSummary()` | GET `/dashboard/summary`, store result |
| `fetchHistory(range)` | GET `/dashboard/energy-history?range=...` |
| `setRange(range)` | Update selected range, refetch history |

---

## 10. Edge Cases

| Scenario | Handling |
|---|---|
| New user with no data | Show onboarding cards instead of empty charts: "Add your first appliance to get started" |
| Baseline not yet established (< 7 days) | Show "Collecting baseline data... X days remaining" with a progress indicator |
| No energy vampires detected | Show a positive message: "No energy vampires found! 🎉" |
| Green Score = 0 | Don't show negative messaging. Show "Let's start improving your score!" |
| API timeout on dashboard load | Show cached data (if available) with a "Last updated X ago" badge |
| Very high energy usage spike | Highlight with a red alert card: "Unusual usage detected" |

---

## 11. Dependencies

| Dependency | Direction |
|---|---|
| **Phase 1** (Setup) | ← Project scaffolding must be complete |
| **Phase 2** (Auth) | ← User must be authenticated to view dashboard |
| **Phase 4** (IoT Data) | ← Energy/water data must be seeded for charts to display |
| **Phase 7** (Challenges) | ← Challenge preview depends on challenge system |

> **Note:** During initial development, use **hardcoded mock data** in the frontend to build the UI before the backend APIs are ready. Replace with real API calls once Phase 4 is complete.

---

> **Next:** Proceed to [04_iot_mock_data_and_energy_tracking.md](./04_iot_mock_data_and_energy_tracking.md) to build the mock IoT data generator and energy tracking system.
