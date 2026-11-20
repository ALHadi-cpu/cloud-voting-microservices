# 🗳️ Distributed Microservices Voting Application

A multi-tier, polyglot distributed voting system orchestrated with **Docker & Docker Compose**. Built to demonstrate microservices decoupling, custom multi-stage image builds, private network segmentation, persistent storage volumes, and asynchronous message queuing.

---

## 🏗️ System Architecture

The application implements the **Queue-Worker Pattern** to decouple high-concurrency write operations (vote casting) from relational database persistence:

```text
[ Browser / Voter ]                               [ Browser / Admin ]
        │                                                 │
        ▼ (Port 5000)                                     ▼ (Port 3000)
┌───────────────┐     LPUSH (TCP 6379)     ┌─────────────────────────────┐
│   vote-app    │ ───────────────────────> │            redis            │
│ (Flask / Py3) │                          │     (In-Memory Queue)       │
└───────────────┘                          └─────────────────────────────┘
                                                          │
                                                          │ BRPOP
                                                          ▼
┌───────────────┐     SQL SELECT           ┌─────────────────────────────┐
│  result-app   │ <──────────┐             │           worker            │
│ (Node / Exp)  │            │             │       (Python Daemon)       │
└───────────────┘            │             └─────────────────────────────┘
                             │                            │
                             │ (TCP 5432)                 │ SQL UPSERT
                             │             ┌─────────────────────────────┐
                             └──────────── │          postgres           │
                                           │  (Persistent Volume Store)  │
                                           └─────────────────────────────┘
```

### Key Architectural Decisions
* **Asynchronous Buffering:** `vote` never writes directly to PostgreSQL. Pushing votes to Redis via `LPUSH` ensures low latency under traffic spikes and prevents database lock contention.
* **Polyglot Stack:** Combines **Python (Flask)** for frontend submission, **Python (Psycopg2)** for background stream consumption, and **Node.js (Express)** for real-time result aggregation.
* **Network Segmentation:** `redis` and `db` are isolated on an internal backend network with zero host port exposure, minimizing the attack surface.
* **Data Durability:** PostgreSQL state is backed by a named Docker volume (`db-data`), ensuring vote tallies survive container restarts and recreations.

---

## 🧩 Services Breakdown

| Service | Stack / Image | Role | Exposed Port (`Host:Container`) |
| :--- | :--- | :--- | :--- |
| **`vote`** | Python 3.11 / Flask | Web frontend for casting votes | `5000:5000` |
| **`redis`** | `redis:7-alpine` | In-memory message broker buffering incoming votes | *Internal only (`6379`)* |
| **`worker`** | Python 3.11 / Psycopg2 | Background daemon consuming Redis queue (`BRPOP`) and upserting to DB | *Internal daemon (no ports)* |
| **`db`** | `postgres:15-alpine` | Primary relational database with named persistent volume | *Internal only (`5432`)* |
| **`result`** | Node.js 18 / Express | Real-time dashboard querying and displaying live vote tallies | `3000:3000` |

---

## 🚀 Getting Started

### Prerequisites
* **Docker Engine** `>= 20.10`
* **Docker Compose** `>= 2.0`

### 1. Clone & Launch
```bash
git clone [https://github.com/](https://github.com/)<your-username>/voting-app-project.git
cd voting-app-project

# Build custom images and start all 5 containers in detached mode
docker compose up --build -d
```

### 2. Access the Interfaces
* **Cast Votes:** [http://localhost:5000](http://localhost:5000)
* **Live Results Dashboard:** [http://localhost:3000](http://localhost:3000)

### 3. Verify & Inspect Services
```bash
# Check container health and port mappings
docker compose ps

# Tail worker logs to watch real-time queue consumption
docker compose logs -f worker
```

### 4. Shutdown & Cleanup
```bash
# Stop containers while preserving database volume
docker compose down

# Stop containers AND wipe persistent database volume
docker compose down -v
```

---

## 📁 Project Structure
```text
voting-app-project/
├── vote/                  # Python Flask voting frontend + Dockerfile
├── worker/                # Python background consumer daemon + Dockerfile
├── result/                # Node.js Express live dashboard + Dockerfile
├── docker-compose.yml     # Multi-service orchestration, networks & volumes
└── README.md
```
