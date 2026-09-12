# KisanSetu: System Architecture, High-Availability & Scaling Blueprint (2026–2028)

## 1. System Overview & Technology Stack

KisanSetu is a community-owned, deterministic financial infrastructure designed to underwrite marginal smallholder farmers (< 2.5 acres) without requiring land ownership deeds.

* **Backend**: FastAPI (Python 3.14 / ASGI) with modular routers for Underwriting, FPO Coordination, Rural Lenders, Agricultural Market Data, Multilingual Voice, and Cryptographic Identity.
* **Frontend**: Streamlit multi-role reactive application supporting 11 Indian languages (Hindi, Marathi, Gujarati, Telugu, Tamil, Kannada, Punjabi, Bengali, Odia, Assamese, English).
* **Database & Ledger**: SQLAlchemy ORM with SQLite (prototype/development) / PostgreSQL (production) with an append-only cryptographic SHA-256 hash-chain ledger for tamper-evident credit credentials.
* **Agro-Data Feeds**: AGMARKNET daily APMC mandi modal prices, NHB/DES district yield benchmarks, and PMFBY crop insurance verification.

---

## 2. High-Throughput Voice Architecture (10,000+ Daily Voice Interactions)

To service marginal farmers with low literacy across diverse linguistic zones, the platform handles spoken vernacular intake at scale.

```
+------------------------------------------------------------------------------------+
|                               VOICE INGESTION PIPELINE                             |
+------------------------------------------------------------------------------------+
                                      │
                         [Farmer Voice / IVR / WebRTC]
                                      │
                                      ▼
                        +───────────────────────────+
                        |   Cloudflare / NGINX Edge |  (TLS 1.3, Rate-Limiting, DDoS)
                        +───────────────────────────+
                                      │
                                      ▼
                        +───────────────────────────+
                        |    FastAPI Voice Gateway  |  (Chunked upload, audio validation)
                        +───────────────────────────+
                                      │
                                      ▼
                        +───────────────────────────+
                        |    Redis Queue / RabbitMQ |  (Asynchronous ingestion buffer)
                        +───────────────────────────+
                                      │
                   ┌──────────────────┴──────────────────┐
                   ▼                                     ▼
      +───────────────────────────+        +───────────────────────────+
      |  ASR Worker Pool (GPU)    |        |  ASR Worker Pool (CPU/ONNX)|
      |  Conformer / Whisper-Large|        |  Whisper-Small / Citrinet |
      |  (Hindi, Marathi, Telugu) |        |  (Realtime streaming)     |
      +───────────────────────────+        +───────────────────────────+
                   │                                     │
                   └──────────────────┬──────────────────┘
                                      ▼
                        +───────────────────────────+
                        | Agronomic Entity Parser   |  (Regex + Fine-tuned NER)
                        | Extracts Name, Crop, Acre |  (Yield, Costs, Guarantors)
                        +───────────────────────────+
                                      │
                                      ▼
                        +───────────────────────────+
                        |  Farmer Review & Confirm  |  (WebSocket / Streamlit state)
                        +───────────────────────────+
```

### Capacity & Latency Analysis for 10,000+ Daily Calls:
* **Call Volume**: 10,000 daily voice interactions ≈ 0.12 calls/sec average, with a 5x peak factor = 0.6 to 1.2 concurrent streams during morning/evening farmer intake windows.
* **Audio Duration**: Average utterance is 15–25 seconds (approx. 400 KB at 16 kHz mono Opus).
* **Worker Sizing**: A single 4-core CPU instance with ONNX-quantized Conformer transcribes a 15-second clip in 450ms. A 4-worker pool comfortably handles up to 40,000 daily voice interactions with sub-second response times.
* **Fallback Strategy**: In intermittent rural 2G/3G connectivity, audio is recorded locally in Web Audio / IndexedDB and uploaded when network signal recovers, backed by a typed vernacular fallback.

---

## 3. High Availability Architecture for 99.5% Uptime

99.5% uptime allows a maximum downtime of ~7.2 minutes per day (or 43.8 hours annually).

```
                                [Internet Traffic]
                                        │
                                        ▼
                        +───────────────────────────────+
                        | Geo-Distributed Anycast DNS   |
                        | (Cloudflare / AWS Route 53)   |
                        +───────────────────────────────+
                                        │
                                        ▼
                        +───────────────────────────────+
                        | Application Load Balancer(ALB)|
                        | Health Checks & SSL Offload   |
                        +───────────────────────────────+
                                        │
                   ┌────────────────────┴────────────────────┐
                   ▼                                         ▼
+───────────────────────────────────────+ +───────────────────────────────────────+
|         Availability Zone A           | |         Availability Zone B           |
|  +─────────────────────────────────+  | |  +─────────────────────────────────+  |
|  | FastAPI Pods (Autoscaling 2-10) |  | |  | FastAPI Pods (Autoscaling 2-10) |  |
|  +─────────────────────────────────+  | |  +─────────────────────────────────+  |
|  | Streamlit UI Service Instances  |  | |  | Streamlit UI Service Instances  |  |
|  +─────────────────────────────────+  | |  +─────────────────────────────────+  |
+───────────────────────────────────────+ +───────────────────────────────────────+
                   │                                         │
                   └────────────────────┬────────────────────┘
                                        ▼
                        +───────────────────────────────+
                        | Multi-AZ Amazon RDS PostgreSQL|
                        | (Primary Read/Write + Replica)|
                        +───────────────────────────────+
                                        │
                                        ▼
                        +───────────────────────────────+
                        | Redis Sentinel Cache Cluster  |
                        | (Mandi Price Caching, Sessions|
                        +───────────────────────────────+
```

### Key Resiliency Measures:
1. **Zero-Downtime Rolling Deployments**: Kubernetes Blue/Green deployments with pre-stop hooks and graceful ASGI connection draining.
2. **Circuit Breakers for External Feeds**: AGMARKNET and PMFBY feeds utilize exponential backoff and cached district market snapshots. If external government APIs experience downtime, the underwriting engine continues operating on validated 24-hour cache without blocking farmers.
3. **Database Failover**: PostgreSQL Multi-AZ synchronous replication with automatic sub-60-second failover.
4. **Data Durability**: Point-in-time recovery (PITR) with continuous WAL archiving and daily cross-region snapshots.

---

## 4. Scaling Toward 5 Million Marginal Farmers by 2028

India possesses ~86 million marginal smallholders (< 2.5 acres). Serving 5 million farmers represents ~5.8% market penetration across high-density agricultural states (Maharashtra, Madhya Pradesh, Gujarat, Karnataka, Punjab, Andhra Pradesh, Telangana).

```
                                5 MILLION FARMERS
                                        │
         ┌──────────────────────────────┼──────────────────────────────┐
         ▼                              ▼                              ▼
  State Shard 1                  State Shard 2                  State Shard N
 (Maharashtra & MP)             (Gujarat & Karnataka)          (Punjab & AP)
  ~1.8M Farmers                  ~1.5M Farmers                  ~1.7M Farmers
         │                              │                              │
  [PostgreSQL Shard]             [PostgreSQL Shard]             [PostgreSQL Shard]
```

### Architectural Evolution Roadmap:

| Dimension | Hackathon Prototype (2026) | Regional Pilot (2027: 250k Farmers) | National Scale (2028: 5M Farmers) |
| :--- | :--- | :--- | :--- |
| **Active Borrowers** | Single Village Pools (54 Seed Farmers) | 250,000 Across 50 FPOs | 5,000,000 Across 1,200 FPOs |
| **Database Tier** | SQLite with local transactions | PostgreSQL 16 with Read Replicas | Citus / CockroachDB Sharded by District & FPO |
| **Underwriting Execution** | In-process Python service (< 20ms) | Asynchronous Task Workers (Celery) | Rust-compiled Underwriting Microservice (< 2ms) |
| **Voice Processing** | Local ASR / Conformer Pipeline | GPU-accelerated Triton Inference Cluster | Edge-quantized on-device ASR + Cloud Conformer |
| **Market Data** | Daily APMC Snapshot & Fallback | Hourly AGMARKNET Kafka Ingestion | Real-time APMC e-NAM Streaming Pipeline |
| **Identity & Blockchain** | Local SHA-256 Hash Chain Ledger | Polygon ID / Hyperledger Indy Testnet | Production Sovereign Decentralized ID (W3C DID) |
| **Storage Requirements** | ~50 MB SQLite DB | ~120 GB PostgreSQL + S3 Docs | ~2.4 TB Compressed Structured Dossiers |

### Cost per Farmer Projection (2028 Scale):
* Cloud compute & database infrastructure: ₹1.80 ($0.02) per farmer per harvest season.
* Voice ASR processing: ₹0.90 per intake session.
* Total operational IT cost: **< ₹3.50 per farmer per season**, well within the 0.25% administrative fee permitted under priority sector agricultural lending operations.

---

## 5. Security & Regulatory Compliance

1. **Aadhaar & PII Masking**: Mobile numbers and identity credentials are cryptographically hashed using SHA-256 before ledger anchoring.
2. **Zero-Land-Deed Compliance**: The system mathematically forbids demanding 7/12 extract or title deeds, deriving working capital credit limits purely from seasonal cashflow margins (`0.45 × Net Profit`) and 3-peer social collateral.
3. **GDPR / DPDP Compliance**:
   - Explicit consent tracking for underwriting, FPO sharing, and mandi price alerts.
   - Machine-readable Article 15/20 data dossier export.
   - Article 17 Right to Erasure / Anonymization endpoint.
