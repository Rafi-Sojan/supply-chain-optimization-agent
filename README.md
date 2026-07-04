# Supply Chain Optimization Platform

A full-stack decision support platform for supply chain planning and logistics
optimization. The application combines a React dashboard, FastAPI services,
CSV-based datasets, supplier scoring, inventory planning, demand forecasting,
and a constraint-based warehouse allocation engine.

The project is designed to demonstrate backend engineering, optimization
modeling, data validation, and dashboard-driven decision support. It is not
positioned as a chatbot-first project; the main focus is the optimization and
business logic behind supply chain decisions.

## Architecture

```text
React Dashboard
      |
FastAPI REST API
      |
CSV Data Layer + SQLAlchemy Models
      |
Business Services
  - Forecasting
  - Inventory Planning
  - Supplier Ranking
      |
Optimization Engine
  - OR-Tools solver
  - deterministic fallback
      |
Route Planning Layer
  - Dijkstra shortest path
  - A* heuristic search
      |
Scenario Simulation + Recommendation Layer
```

## Core Features

### Demand Forecasting

Forecasts demand using historical product-region demand records. The current
implementation favors simple, explainable methods such as linear trend and
moving average forecasting, plus scikit-learn Linear Regression and Random
Forest models, and XGBoost regression with basic backtesting metrics.

### Inventory Planning

Generates practical inventory metrics:

- Available inventory
- Safety stock
- Reorder point
- Recommended reorder quantity
- Stockout risk
- Overstock risk

### Supplier Ranking

Scores suppliers using a weighted model based on:

- Unit cost
- Reliability
- Lead time
- Capacity
- Quality score
- Past delay rate

### Warehouse Allocation Optimization

Solves the transportation-style allocation problem:

- Minimize total shipping cost
- Satisfy customer demand when inventory allows
- Respect warehouse inventory limits
- Prevent negative shipment quantities
- Support disabled warehouses during scenario simulations

When demand cannot be fully satisfied, the system reports unmet demand instead
of hiding the infeasibility.

### Route Planning

Computes shortest delivery paths over a road-network graph. The route layer can
use Dijkstra for exact non-negative shortest paths or A* when coordinates are
available for heuristic search. Route distances and route costs can feed the
warehouse allocation engine as lane costs.

The road network uses optional CSV files:

- `road_nodes.csv`
- `road_edges.csv`

### What-if Simulation

Runs scenario analysis for operational changes such as:

- Demand increase
- Fuel or transportation cost increase
- Supplier reliability change
- Warehouse shutdown

The scenario module compares the base case with the changed scenario and
returns cost impact, allocation changes, risk level, and a recommendation.

## Dataset Support

The project supports two dataset modes:

### Sample Data

Sample CSV files are included under `data/` for quick local testing.

### Custom / Benchmark Data

The backend reads real-mode CSVs from `data/raw/`. A feasible transportation
benchmark importer is included:

```bash
.\backend\.venv-win\Scripts\python.exe scripts\import_pulp_beer_distribution.py
```

The importer adapts the public COIN-OR/PuLP Beer Distribution transportation
case study into the project schema. This benchmark is useful because it contains
the core inputs needed by the allocation optimizer: warehouse supply, customer
demand, and route costs.

To use your own dataset, place these files in `data/raw/`:

- `products.csv`
- `suppliers.csv`
- `warehouses.csv`
- `customers.csv`
- `inventory.csv`
- `demand_history.csv`
- `shipping_costs.csv`

See [data/raw/README.md](data/raw/README.md) for the required columns and
validation rules.

## Tech Stack

| Layer | Tools |
| --- | --- |
| Frontend | React, Vite, Recharts, Lucide React |
| Backend | FastAPI, Pydantic |
| Data / ORM | CSV data layer, SQLAlchemy models |
| Optimization | Google OR-Tools, deterministic fallback |
| Analytics / ML | pandas, NumPy, scikit-learn Linear Regression and Random Forest, XGBoost |
| Testing | pytest |
| DevOps | Docker, Docker Compose, GitHub Actions |

## Project Structure

```text
backend/
  app/
    main.py
    database.py
    models/
    routes/
    schemas/
    services/
    tests/
frontend/
  src/
    api/
    charts/
    components/
    pages/
data/
  raw/
  sample_*.csv
scripts/
  import_pulp_beer_distribution.py
  start-dev.js
docker-compose.yml
README.md
```

## API Overview

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Backend health check |
| `GET` | `/data/status` | Dataset source, validation, row counts, and required columns |
| `GET` | `/dashboard/summary` | High-level dashboard metrics and recommendation |
| `GET` | `/products` | Product records |
| `GET` | `/suppliers` | Supplier records |
| `GET` | `/suppliers/ranking` | Weighted supplier ranking |
| `GET` | `/inventory` | Inventory records |
| `GET` | `/inventory/reorder-plan` | Reorder and risk recommendations |
| `POST` | `/forecast/demand` | Demand forecasting |
| `GET` | `/routes/network` | Road-network nodes and edges |
| `GET` | `/routes/shortest-path` | Dijkstra/A* route between two nodes |
| `POST` | `/optimize/warehouse-allocation` | Cost-minimizing warehouse allocation |
| `GET` | `/optimize/runs` | Optimization run history for the current process |
| `POST` | `/scenarios/run` | What-if scenario simulation |

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://127.0.0.1:5173
```

### Start Both Servers

After installing dependencies:

```bash
node scripts/start-dev.js
```

### Docker

```bash
docker compose up --build
```

## Useful Commands

Run backend tests:

```bash
$env:PYTHONPATH='backend'
.\backend\.venv-win\Scripts\python.exe -m pytest backend\app\tests
```

Build frontend:

```bash
cd frontend
npm run build
```

Check active dataset:

```bash
curl http://127.0.0.1:8000/data/status
```

Regenerate the included feasible benchmark:

```bash
.\backend\.venv-win\Scripts\python.exe scripts\import_pulp_beer_distribution.py
```
