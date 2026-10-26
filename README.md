# CivicPulse — Cloud-Based Public Infrastructure Issue Intelligence

CivicPulse is a cloud-hosted platform for reporting, grouping, prioritizing, tracking, and analyzing local public infrastructure issues such as potholes, broken streetlights, water leaks, damaged footpaths, and drainage problems.

Unlike basic complaint CRUD applications, CivicPulse features:
* **Explainable Duplicate-Report Clustering** (geospatial distance threshold $\le 350\text{ m}$ + Jaccard token overlap)
* **Transparent Multi-Factor Priority Scoring** (severity, safety hazards, cluster repetition, time unresolved)
* **Interactive Leaflet Mapping & Hotspots** with non-map tabular fallback
* **SLA Tracking & Workflow Lifecycle** (`Submitted` $\rightarrow$ `Triaged` $\rightarrow$ `Assigned` $\rightarrow$ `In Progress` $\rightarrow$ `Resolved` $\rightarrow$ `Verified`)
* **Asynchronous Queue Worker Pipeline** for background indexing and report generation
* **Private S3 File Storage** with short-lived pre-signed URLs
* **Dual-Mode Operation:** Works zero-cloud out of the box locally, or deploys seamlessly to AWS with EC2, private RDS MySQL, custom VPC, SQS, SNS, and CloudWatch.

---

## 1. Quick Local Setup & Demonstration

### Prerequisites
* Python 3.10+
* Node.js v18+ and npm
* Git

### Step A: Clone & Environment Setup
```bash
git clone <repo-url> CivicPulse
cd CivicPulse
cp .env.example .env
```

### Step B: Backend Setup & Seed Data
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Seed realistic demo issues, categories, and accounts
python -m backend.seeds.seed_data

# Run tests to verify
pytest
```

### Step C: Run Application
Open two terminal windows:

**Terminal 1 (Backend API on port 5000):**
```bash
python backend/wsgi.py
```

**Terminal 2 (Frontend UI on port 5173):**
```bash
cd frontend
npm install
npm run dev
```

Visit **`http://localhost:5173`** in your browser.

---

## 2. Seeded Demo Accounts (for Classroom Evaluation)

| Role | Email | Password | Primary Capabilities |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@civicpulse.local` | `AdminPass123!` | Triage, assignment, duplicate review, exports, analytics |
| **Field Worker** | `fieldworker@civicpulse.local` | `WorkerPass123!` | View assigned tasks, mark in-progress, submit resolution |
| **Citizen Reporter** | `citizen@civicpulse.local` | `CitizenPass123!` | Public submission, pin placement, status tracking |

*Tip: Use the **Role Switcher** in the top navigation bar to switch personas instantly during a demonstration.*

---

## 3. Implemented AWS Architecture (Baseline)

CivicPulse is designed to run its core services on **Amazon EC2** within a **custom Amazon VPC**:
* **Amazon EC2:** Hosts the Flask API backend, compiled React frontend, and background queue worker.
* **Amazon VPC:** Dedicated custom network (`10.0.0.0/16`) isolating public web traffic from the database.
* **Amazon RDS for MySQL:** Private database in two Availability Zones (`db.t4g.micro`, single-AZ, no public IP). Ingress is strictly restricted to the EC2 security group.
* **Amazon S3:** Private bucket with Block Public Access and SSE-AES256 encryption. Files are accessed strictly via short-lived pre-signed URLs.
* **Amazon SQS & DLQ:** Asynchronous job dispatching with dead-letter queue retries.
* **Amazon SNS:** Alert dispatching for critical safety hazards and CloudWatch alarms.
* **AWS Systems Manager Parameter Store:** Secure server-side credential loading.
* **Amazon CloudWatch:** Structured logging and EC2 CPU threshold alerting.

---

## 4. Documentation Reference

* [ARCHITECTURE.md](ARCHITECTURE.md) — Architectural principles, network diagram, and service justification.
* [COSTS.md](COSTS.md) — Pricing estimates, Free Tier limits, and teardown instructions.
* [SECURITY.md](SECURITY.md) — Security groups, IAM policies, and data privacy notices.
* [DEMO_SCRIPT.md](DEMO_SCRIPT.md) — 5–7 minute walkthrough presentation guide.
