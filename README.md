# KisanSetu: Community-Owned Credit Network for Marginal Farmers

A community-owned financial infrastructure that democratizes agricultural credit through transparent, deterministic agronomic assessment, FPO 3-member peer social collateral, and harvest-synchronized bullet repayment—enabling India's 86 million marginal smallholders (< 2.5 acres) to escape informal money-lending traps without requiring land ownership titles.

---

## Key Highlights & PRD Compliance

1. **Zero Land-Deed Mandate**: Credit assessment based purely on seasonal agronomic cashflow (`Acres × Yield × AGMARKNET Price`), itemized working expenses, and 3-peer FPO social guarantee.
2. **Transparent Underwriting**:
   - `Gross Revenue = Acres × Yield × AGMARKNET Mandi Price`
   - `Net Profit = Gross Revenue - Total Expenses`
   - `Safe Credit Limit = 0.45 × Net Profit` (+15% limit bonus for consistent performers with 100% peer repayment track record)
   - Explainable Credit Score on a strict 0–100 scale with itemized factor rationales.
   - Harvest-Synchronized Single Bullet Amortization (Zero monthly EMI during crop growth; due date aligned with harvest + 30-day marketing buffer).
3. **Multilingual Voice Intake in 11 Languages**: Spoken input with live recording, vernacular voice scenarios, transcript review, and entity auto-fill across Hindi, Marathi, Gujarati, Telugu, Tamil, Kannada, Punjabi, Bengali, Odia, Assamese, and English.
4. **FPO Coordinator Console**: 3-member peer group onboarding, mutual social collateral pledges, field crop verification logs (with GPS & stages), and early warning distress alerts.
5. **Rural Bank & NBFC Console**: Live application queue, RBI Priority Sector Lending (PSL) qualification, underwriting drill-downs, approval/rejection workflows, e-RUPI voucher disbursement, and 30-day AGMARKNET price trend charts.
6. **Data Ownership & Cryptographic Identity**: W3C Decentralized Identifiers (DID), verifiable credit credentials with SHA-256 tamper-evident digital digests, and GDPR/DPDP consent audit trails & data dossier export.

---

## Technology Stack

* **Backend**: FastAPI (Python 3.14 / ASGI)
* **Frontend**: Streamlit multi-role reactive console
* **Database & Ledger**: SQLAlchemy ORM with SQLite (development) / PostgreSQL (production) with cryptographic hash-chain ledger
* **Data Sources**: AGMARKNET daily APMC mandi modal prices, NHB/DES district yield benchmarks, PMFBY insurance registry
* **Validation & Security**: Pydantic v2, W3C Verifiable Credentials

---

## Installation & Setup

### 1. Prerequisites
* Python 3.9 or higher (Python 3.14 supported)
* pip

### 2. Clone and Navigate to the Repository
```bash
git clone <repository_url>
cd 019_02
```

### 3. Set Up Virtual Environment (Optional but recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 5. Set Up Environment Variables
```bash
cp .env.example .env
```

### 6. Seed Demo Data (Creates 2 Peer Groups, 6 Smallholders, Verifications, and Sanctioned Loans)
```bash
python -m backend.seed_data
```

---

## Running the Application

### Option A: Run the FastAPI Backend
Start the backend server on port 8000:
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
* **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Interactive ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### Option B: Run the Streamlit Multi-Role Frontend
In a separate terminal, launch the Streamlit frontend:
```bash
streamlit run frontend_app.py --server.port 8501
```
* **Frontend UI**: [http://localhost:8501](http://localhost:8501)

*(Note: The Streamlit interface automatically connects to the FastAPI backend, and also incorporates a local deterministic fallback engine if the backend is momentarily starting).*

---

## Running the Automated Test Suites

### 1. Comprehensive PRD Test Suite (All Features & Latency Benchmark)
```bash
python -m backend.test_api
```

### 2. Complete 9-Step Farmer End-to-End Journey & Edge Cases
```bash
python test_e2e_journey.py
```

---

## API Endpoints Reference

### 1. Farmers (`/api/v1/farmers`)
* `POST /api/v1/farmers` — Register or update farmer profile (zero land deeds required)
* `GET /api/v1/farmers` — List all registered smallholders
* `GET /api/v1/farmers/{id}` — Fetch specific farmer profile
* `PUT /api/v1/farmers/{id}` — Update farmer profile
* `DELETE /api/v1/farmers/{id}` — Delete farmer

### 2. Agronomic Underwriting (`/api/v1/underwriting`)
* `POST /api/v1/underwriting/calculate` — Deterministic underwriting calculation (< 20ms execution)
* `POST /api/v1/underwriting/submit-application` — Calculate, upsert farmer, persist assessment, and issue W3C Verifiable Credential
* `GET /api/v1/underwriting/farmer/{id}/latest` — Get latest underwriting assessment

### 3. FPO Coordinator & Peer Groups (`/api/v1/fpo`)
* `POST /api/v1/fpo/groups` — Onboard 3-member peer guarantee group with social collateral pledge
* `GET /api/v1/fpo/groups` — List active peer groups, pool limits, and member creditworthiness
* `POST /api/v1/fpo/verifications` — Record field visit crop verification outcome
* `GET /api/v1/fpo/verifications` — List field crop inspection records
* `GET /api/v1/fpo/alerts` — Retrieve early warning alerts for struggling members
* `GET /api/v1/fpo/offline-sync-status` — Mobile offline sync resilience status

### 4. Rural Bank & NBFC Console (`/api/v1/lenders`)
* `GET /api/v1/lenders/dashboard` — Portfolio summary, repayment rate, PSL compliance, 72h SLA
* `GET /api/v1/lenders/applications` — Live application queue with agronomic drill-down
* `POST /api/v1/lenders/applications/{id}/decision` — Sanction or reject application
* `POST /api/v1/lenders/applications/{id}/disburse` — Instant e-RUPI agricultural voucher disbursement

### 5. Agricultural Market Data (`/api/v1/market-data`)
* `GET /api/v1/market-data/mandi-prices` — AGMARKNET daily modal price and 30-day historical trend
* `GET /api/v1/market-data/all-crops` — Benchmark summary for all crops with MSP comparison
* `GET /api/v1/market-data/district-yield` — Official NHB/DES district benchmark yields
* `GET /api/v1/market-data/pmfby` — PMFBY crop insurance registry lookup
* `GET /api/v1/market-data/alerts` — Mandi price surge/dip alerts and harvest countdown reminders

### 6. Multilingual Voice Intake (`/api/v1/voice`)
* `GET /api/v1/voice/languages` — List 11 supported Indian agricultural languages
* `GET /api/v1/voice/sample/{lang_code}` — Get pre-loaded vernacular voice audio scenario
* `POST /api/v1/voice/parse` — Parse spoken/typed transcript into structured form fields
* `POST /api/v1/voice/transcribe-audio` — Ingest recorded audio file and extract agronomic entities

### 7. Decentralized Identity & GDPR (`/api/v1/identity`)
* `GET /api/v1/identity/farmer/{id}/credential` — Export portable W3C Verifiable Credential
* `POST /api/v1/identity/verify-credential` — Cryptographically verify credential authenticity and tamper status
* `POST /api/v1/identity/consent` — Record GDPR / DPDP explicit consent audit trail
* `GET /api/v1/identity/gdpr/export/{id}` — GDPR Article 15/20 complete data dossier export
* `DELETE /api/v1/identity/gdpr/forget/{id}` — GDPR Article 17 Right to Erasure / Anonymization

---

## Project Structure

```
019_02/
├── backend/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entrypoint with all routers
│   ├── config.py                # Environment configuration
│   ├── database.py              # SQLAlchemy engine & SessionLocal
│   ├── models.py                # SQLAlchemy models (Farmer, PeerGroup, CropVerification, CreditAssessment)
│   ├── schemas.py               # Pydantic validation schemas
│   ├── seed_data.py             # Demo data seeder (2 peer groups, 6 farmers, verifications)
│   ├── test_api.py              # Automated test suite for all PRD requirements & SLAs
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── farmers.py           # Farmer CRUD
│   │   ├── underwriting.py      # Agronomic credit calculation & application submission
│   │   ├── fpo.py               # 3-peer guarantee groups, field crop verifications, alerts
│   │   ├── lenders.py           # Rural bank console, sanctioning, e-RUPI disbursement
│   │   ├── market_data.py       # AGMARKNET daily prices, NHB yield benchmarks, PMFBY lookup
│   │   ├── voice_intake.py      # 11-language voice transcription & entity extraction
│   │   └── identity.py          # W3C DID, verifiable credentials, GDPR consent & export
│   └── services/
│       ├── __init__.py
│       ├── agri_data.py         # AGMARKNET APMC catalog, NHB district yields, PMFBY data, alerts
│       ├── underwriting.py      # Deterministic PRD underwriting engine (< 20ms, 0-100 score)
│       ├── voice_nlp.py         # Vernacular speech token parser across 11 languages
│       ├── identity_blockchain.py # W3C DID generator & cryptographic verifiable credential engine
│       └── gdpr_consent.py      # GDPR compliance (consent audit, portable export, erasure)
├── frontend_app.py              # Streamlit multi-role reactive console (11 languages)
├── test_e2e_journey.py          # End-to-end 9-step verification script with edge cases
├── PRD_FEATURE_AUDIT.md         # Full PRD checklist audit matrix
├── SYSTEM_ARCHITECTURE_AND_SCALING.md # 10k voice calls, 99.5% uptime, 5M farmers scaling blueprint
├── .env.example                 # Environment variables template
├── farmer_finance.db            # SQLite database with seeded demo data
└── README.md                    # Project documentation
```
