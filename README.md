# 🗳️ Distributed Microservices Voting Application
A multi-tier, distributed voting system built using **Docker & Docker Compose**. Designed to demonstrate microservices decoupling, custom container image builds, private container networking, persistent storage volumes, and asynchronous queuing.
---
## 🏗️ Architecture Overview
The system uses the **Queue-Worker Pattern** to separate write-heavy voting transactions from persistent storage:

  

[ Browser / User ]
│
▼ (Port 5000)
┌──────────────┐       LPUSH (TCP 6379)       ┌──────────────┐
│   vote-app   │ ───────────────────────────> │    redis     │
│ (Flask/Py3)  │                              │ (Queue/Cache)│
└──────────────┘                              └──────────────┘
│
│ BRPOP
▼
┌──────────────┐        SQL SELECT            ┌──────────────┐
│  result-app  │ <─────────────────────────── │    worker    │
│ (Node.js/Exp)│           (Port 5432)        │(Python Daemon)
└──────────────┘                              └──────────────┘
▲                                             │
│ (Port 3000)                                 │ SQL UPSERT
│                                             ▼
[ Browser / Admin ]                           ┌──────────────┐
│   postgres   │
│  (Database)  │
└──────────────┘


  
---
## 🧩 Services Breakdown
| Service | Technology | Role | Port (Host:Container) |
|---|---|---|---|
| **vote** | Python 3.11 / Flask | Web interface for casting votes | `5000:5000` |
| **redis** | `redis:7-alpine` | In-memory message queue buffering votes | *Internal only (`6379`)* |
| **worker** | Python 3.11 / Psycopg2 | Background daemon consuming votes & writing to DB | *Internal daemon* |
| **db** | `postgres:15-alpine` | Relational database with persistent volume | *Internal only (`5432`)* |
| **result** | Node.js 18 / Express | Live dashboard displaying vote tallies | `3000:3000` |
---
## 🚀 Getting Started
### Prerequisites
- Docker Engine `>= 20.10`
- Docker Compose `>= 2.0`
### Quick Start
Clone the repository and run:
```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/voting-app-project.git
cd voting-app-project
# 2. Build and launch all services
docker compose up --build -d
