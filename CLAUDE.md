# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered retail inventory management platform for fashion/apparel retailers, built on the H&M Fashion dataset (~31M transactions). Combines a FastAPI backend with ML pipelines for demand forecasting (Prophet) and loss prevention anomaly detection (Isolation Forest).

## Environment Setup

```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Required: .env file with database connection
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/retail_inventory
```

## Running the Application

```bash
# Start FastAPI dev server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at `http://localhost:8000/docs` (Swagger UI).

## Data Pipeline (run in order on fresh setup)

```bash
python app/load_data.py          # Load H&M CSVs into PostgreSQL (large — chunks 500k rows)
python app/enrich_data.py        # Create synthetic stores, sizes, pricing, stock levels
python app/ml/inject_shrinkage.py  # Generate 2000 synthetic shrinkage events
python app/ml/build_features.py    # Build feature_matrix table for ML
python app/ml/train_anomaly.py     # Train Isolation Forest → models/isolation_forest.pkl
python app/ml/evaluate_anomaly.py  # Evaluate catch rates against shrinkage events
```

## Architecture

**Backend:** FastAPI with 5 domain routers (`products`, `stock`, `sales`, `forecast`, `anomalies`). Database sessions injected via `Depends(get_db)` from `app/database.py`.

**Database (PostgreSQL):** Two categories of tables:
- *Source data:* `articles`, `articles_enriched`, `customers`, `transactions`, `stores`, `stock_levels`
- *ML outputs:* `feature_matrix`, `anomaly_scores`, `shrinkage_events`

**ML Pipelines** (standalone scripts, not wired into FastAPI request cycle):
- `app/ml/forecasting.py` — Prophet reads `transactions` table, generates 90-day forecasts with confidence intervals
- `app/ml/train_anomaly.py` — Isolation Forest on `feature_matrix`; serializes model + scaler to `models/isolation_forest.pkl`
- The `forecast` and `anomalies` routers serve pre-computed results from database tables

**Key patterns:**
- Raw SQL via SQLAlchemy `text()` with parameterized queries (not ORM models)
- CORS open to all origins (`*`) — no auth layer currently
- `DAYS_SNAPSHOT=30` hardcoded in feature building scripts

## Planned Next Steps (from README)

- Auto-replenishment engine
- Claude API integration for natural language querying
- React/Vite frontend
