# MalnutriAid AI

MalnutriAid AI is a full-stack, machine learning-powered clinical diagnostic platform designed to predict, monitor, and analyze childhood malnutrition risk in real-time. It provides healthcare workers with an intuitive interface to log patient anthropometrics, instantly receive AI-driven risk assessments, and contribute to continuous model improvement (MLOps).

## System Architecture

The platform operates on a decoupled client-server architecture:

- **Frontend (Client):** A modern, responsive web application built with **React** and **Next.js**. It features a glassmorphic UI, dynamic Chart.js analytics dashboards, secure JWT storage, and Role-Based Access Control (RBAC).
- **Backend (API Engine):** A high-performance REST API built with **FastAPI** (Python). It securely handles user authentication, orchestrates the Machine Learning preprocessing pipelines, serves XGBoost inference requests, and manages data persistence.
- **Database:** A relational **PostgreSQL** database managed via SQLAlchemy. It strictly enforces referential integrity between registered clinicians, clinical predictions, and physician feedback overrides.

---

## How the Machine Learning Works

The core of MalnutriAid AI is a sophisticated prediction pipeline designed for clinical resilience.

### 1. Robust Preprocessing

Before an assessment touches the ML model, the backend automatically sanitizes the payload:

- **Missing Data Imputation:** If incomplete data is submitted (e.g., missing Height or Weight), the backend dynamically imputes the values referencing the **WHO median growth standard curve** for the child's exact age profile.
- **Anomaly Clamping:** Impossible biological outliers (e.g., 500kg weight) are mathematically clamped to maximum/minimum physiological limits (e.g., capping age at 60 months) to prevent model crashes or wild statistical skews.
- **WHO Constraints:** Strict biological bounds actively block clinically impossible combinations on the frontend (e.g., a 2-month-old weighing 40kg).

### 2. 3-Tier Ensembled Risk Classification

The system utilizes an XGBoost ensemble trained on malnutrition datasets. Rather than a simple binary output, the engine natively routes predictions into three distinct severity tiers:

- **Low Risk (< 50% probability):** Standard growth trajectory.
- **Moderate Risk (50% - 79% probability):** Early warning for growth faltering or borderline wasting, triggering preventative care recommendations.
- **Severe Malnutrition (80%+ probability):** Critical alert functionally equivalent to SAM (Severe Acute Malnutrition) criteria, requiring immediate intervention.

### 3. Continuous MLOps Feedback Loop

MalnutriAid AI learns from its experts. After receiving a prediction, clinicians can actively submit a **Feedback Override** if they disagree with the AI's classification. These securely logged disputes (including text justifications) are aggregated in the Admin Dashboard and can be exported as an anonymized CSV dataset to retrain and tune the model's blindspots in the future.

---

## Key Features

- **RBAC Admin Dashboard:** System administrators have exclusive access to a privileged dashboard to monitor top-level API throughput, revoke/grant database access to clinical staff in real-time, and review MLOps feedback disputes.
- **Clinical Analytics Dashboard:** Authorized users can view beautiful, responsive Chart.js visual analytics breaking down their regional demographics by Age Bins, Gender Vulnerability, and longitudinal timeline trends.
- **Scoped Histories:** Clinical profiles are cryptographically isolated. Healthcare workers only see the diagnostic histories of the assessments _they_ natively processed under their JWT session.
- **Research Data Export:** A zero-footprint memory stream allows clinicians to securely download all anonymized prediction and feedback data as a CSV straight from the PostgreSQL database directly to their local browser.

---

## How to Start the Project from Scratch

If you are cloning this repository on a new machine, follow these precise steps to boot the entire system natively.

### 1. Prerequisites

Ensure you have the following installed on your machine:

- **Python 3.10+**
- **Node.js 18+**
- **PostgreSQL 14+** (Running locally on port 5432)

### 2. Configure the Database

1. Open PostgreSQL (via pgAdmin or psql). Ensure a completely clean slate database container:

```sql
DROP DATABASE IF EXISTS malnutrition_db;
CREATE DATABASE malnutrition_db;
```

2. Navigate into the `backend/` folder, create a new file named `.env`, and securely set your local PostgreSQL database password:

```env
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@localhost:5432/malnutrition_db"
```

### 3. Start the Backend (FastAPI ML Engine)

Open a new terminal and navigate into the `backend` directory to boot the Python API:

```bash
cd backend

# Create and activate a pristine virtual environment
python -m venv .venv

# Activate the venv
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
# source .venv/bin/activate

# Install the Machine Learning and Server libraries
pip install -r requirements.txt

# Boot the API server
uvicorn app.main:app --reload
```

_The backend should now be running securely at `http://localhost:8000`_

### 4. Start the Frontend (Next.js Dashboard)

Open a **second, separate terminal window** and navigate into the `frontend` directory:

```bash
cd frontend

# Install all React dependencies
npm install

# Start the frontend development server
npm run dev
```

### 5. Access the System

1. Open your browser and navigate to **`http://localhost:3000`**
2. Click **"Sign Up"** to register your first clinical account.
3. **To access the Admin Panel:** Leave your web browser, return to your active Python terminal, open a new tab, and run `python migrate_admin.py` to upgrade your specific account's privileges natively in the database!
