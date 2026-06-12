# EcoTrace AI 🌍

EcoTrace AI is a gamified, modern sustainability dashboard designed to help users track their energy usage, monitor water consumption, and identify "energy vampires" in their home. It features realistic mock IoT time-series data simulation, real-time power polling, and an engaging "Green Score" to encourage eco-friendly habits.

## 🛠️ Tech Stack

**Frontend:**
- Vue 3 (Composition API & `<script setup>`)
- Vite
- TailwindCSS
- Pinia (State Management)
- Vue Router
- Chart.js & Vue-Chartjs
- Lucide Icons

**Backend:**
- Python 3.11+
- FastAPI
- PostgreSQL (via async asyncpg)
- SQLAlchemy (Async ORM)
- Pydantic
- JWT Authentication

## ✨ Features (Current MVP)

- **Authentication:** Secure user registration and login with JWT bearer tokens.
- **Gamified Dashboard:** Real-time calculation of a "Green Score" based on energy usage and active sustainability challenges.
- **IoT Data Simulation:** A highly sophisticated backend seeder that generates 12 default appliances and over 35,000 rows of realistic, variance-injected time-series data based on time-of-day multipliers and weekend modifiers.
- **Live Power Draw:** A pulsing widget that polls the backend every 5 seconds to display simulated real-time wattage usage.
- **Appliance Breakdown:** Visual identification of high-consumption devices and actionable tips for unplugging "energy vampires."

## 🚀 Getting Started

### 1. Database Setup
Ensure you have PostgreSQL installed and running. Create a database named `ecotrace` with user `postgres` and password `postgres`.

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
1. Open the frontend and create a new account.
2. Navigate to the **Settings** page in the sidebar.
3. Click **Seed Database** to instantly generate 30 days of historical energy and water readings for your dashboard.
4. Navigate back to the **Dashboard** to see the data live!
