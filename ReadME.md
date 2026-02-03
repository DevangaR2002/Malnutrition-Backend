# Malnutrition Backend (FastAPI) – Run Guide

This guide explains how to set up the **PostgreSQL database**, configure the **.env**, create a **virtual environment**, install dependencies, and run the **FastAPI backend**.

---

## ✅ Prerequisites

Make sure you have the following installed:

- **Python 3.10+**
- **PostgreSQL 14+**
- **pip** (comes with Python)

Optional (recommended):
- **pgAdmin** or any PostgreSQL GUI

---

## 1) 🗄️ Database Setup (PostgreSQL)

### 1.1 Create Database

Open PostgreSQL terminal (`psql`) and run:

```sql
CREATE DATABASE malnutrition_db;
````

(Optional) Verify:

```sql
\l
```

---

### 1.2 Create Table Schema

Connect to the database:

```sql
\c malnutrition_db
```

Create the table:

```sql
CREATE TABLE IF NOT EXISTS public.predictions (
  id SERIAL PRIMARY KEY,
  age_months INTEGER NOT NULL,
  gender VARCHAR(10) NOT NULL,
  mother_education VARCHAR(50) NOT NULL,
  household_wealth_index VARCHAR(20) NOT NULL,
  height_cm DOUBLE PRECISION NOT NULL,
  weight_kg DOUBLE PRECISION NOT NULL,
  has_diarrhea BOOLEAN DEFAULT FALSE,
  has_malaria BOOLEAN DEFAULT FALSE,
  has_tb BOOLEAN DEFAULT FALSE,
  prediction INTEGER NOT NULL,
  risk_probability DOUBLE PRECISION NOT NULL,
  risk_level VARCHAR(20) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Verify table:

```sql
\dt
\d predictions
```

✅ You should see the `predictions` table.

---

## 2) 🔐 Create `.env` File

Inside the **backend root folder** (same level as `requirements.txt`), create a file named:

```
.env
```

Paste this content:

```env
# Database Configuration
DATABASE_URL=postgresql://<YOUR_POSTGRES_USERNAME>:<YOUR_POSTGRESQL_PASSWORD>@localhost:5432/malnutrition_db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# ML Model Paths
MODEL_PATH=ml_models/best_ensemble_model.pkl
SCALER_PATH=ml_models/scaler.pkl
```

✅ Make sure these files exist:

* `ml_models/best_ensemble_model.pkl`
* `ml_models/scaler.pkl`

> If your PostgreSQL username/password differs, update `DATABASE_URL`.

---

## 3) 🐍 Create Virtual Environment

From the backend root directory:

```bash
python -m venv venv
```

---

## 4) ▶️ Activate Virtual Environment & Install Dependencies

### Windows (PowerShell)

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 5) 🚀 Run the Backend

Run FastAPI using Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Once running, open:

* API: `http://localhost:8000`
* Swagger Docs: `http://localhost:8000/docs`
* ReDoc: `http://localhost:8000/redoc`

---

## ✅ Quick Troubleshooting

### Database connection issues

* Confirm PostgreSQL is running
* Check `.env` credentials
* Ensure database exists: `malnutrition_db`

### Table not found

Run schema creation again (`CREATE TABLE ...`).

### Missing ML model files

Ensure the files exist under:

```
ml_models/
  best_ensemble_model.pkl
  scaler.pkl
```

---

## 📂 Project Structure (Backend)

```
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── routes/
│   ├── schemas/
│   └── services/
├── ml_models/
│   ├── best_ensemble_model.pkl
│   └── scaler.pkl
├── requirements.txt
└── .env
```

```
```
