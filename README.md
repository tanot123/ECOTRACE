# EcoTrace AI 🌍💻

EcoTrace AI is a gamified, modern sustainability dashboard designed to help users track their energy usage, monitor water consumption, and identify "energy vampires" in their home. It features realistic mock IoT time-series data simulation, real-time power polling, and an engaging "Green Score" to encourage eco-friendly habits.

---

## 🛠️ Tech Stack

### Frontend
- **Framework:** Vue 3 (Composition API & `<script setup>`)
- **Language:** TypeScript
- **Build Tool:** Vite
- **Styling:** TailwindCSS (v4) & PostCSS
- **State Management:** Pinia
- **Routing:** Vue Router
- **Visualization:** Chart.js & `vue-chartjs`
- **Utility Libraries:** `@vueuse/core` & Axios
- **Iconography:** Lucide Icons (`lucide-vue-next`)

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL (via async `asyncpg`)
- **ORM:** SQLAlchemy (Async ORM)
- **Validation:** Pydantic
- **Security:** JWT Authentication

---

## 📂 Project Structure

```
ECOTRACE/
├── docker-compose.yml  # PostgreSQL container config
├── backend/            # Python FastAPI backend service
│   ├── app/            # Application logic (routers, models, schemas)
│   ├── alembic/        # DB migration scripts
│   └── requirements.txt
└── frontend/           # Vue 3 frontend client
    ├── src/
    │   ├── assets/     # Images & static assets
    │   ├── components/ # Reusable UI components (challenges, dashboard, scanner, schedule, layout)
    │   ├── pages/      # Router view pages (Dashboard, Challenges, Scanner, Scheduler, Login/Register, Settings)
    │   ├── router/     # Route configuration & guards
    │   ├── services/   # API integration layer
    │   ├── stores/     # Pinia state stores (auth, dashboard)
    │   ├── App.vue     # Application root
    │   └── main.ts     # Main entry point
    └── package.json
```

---

## ✨ Features (Current MVP)

- **Secure Authentication:** User registration and login protected by JWT bearer tokens.
- **Gamified Dashboard:** Real-time calculation of a "Green Score" based on energy usage and active sustainability challenges.
- **IoT Data Simulation:** A backend seeder that generates 12 default appliances and over 35,000 rows of realistic, variance-injected time-series data based on time-of-day multipliers and weekend modifiers.
- **Live Power Draw:** A pulsing widget that polls the backend every 5 seconds to display simulated real-time wattage usage.
- **Energy Vampire Scanner:** A utility to scan household appliances, identifying standby ("vampire") power draw and offering optimization recommendations.
- **Smart Scheduler:** An interactive scheduler calendar allowing users to queue heavy appliance operations during off-peak hours.
- **Eco Challenges:** Daily and weekly quests (e.g. "Unplug Everything", "Off-Peak Only") designed to help users earn points and build eco-friendly habits.

---

## 🚀 Getting Started

### 1. Database Setup (Docker Compose)
The easiest way to set up the database is to use the provided Docker Compose file, which spins up a PostgreSQL container matching the default configuration:

```bash
# Start the database container
docker-compose up -d
```

This runs PostgreSQL on port `5433` with the database `ecotrace_dev` and user credentials as configured in the backend's `.env` file.

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
uvicorn app.main:app --reload
```
The FastAPI documentation will be available at `http://localhost:8000/docs`.

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run the dev server
npm run dev
```
The Vue application will be available at `http://localhost:5173`.

### 4. Seeding Data
1. Open the frontend browser at `http://localhost:5173` and create a new account.
2. Navigate to the **Settings** page in the sidebar.
3. Click **Seed Database** to instantly generate 30 days of historical energy and water readings for your dashboard.
4. Navigate back to the **Dashboard** to see the data live!
