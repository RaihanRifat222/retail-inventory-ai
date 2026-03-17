# Retail Inventory AI

An AI-powered inventory management platform for fashion and apparel retailers, built on the H&M Kaggle dataset (31.7M transactions). Demonstrates full-stack AI engineering across Python, FastAPI, PostgreSQL, and React.

## Features

| Module | Description |
|--------|-------------|
| **Demand Forecasting** | 30/60/90-day SKU-level forecasts using Facebook Prophet |
| **Loss Prevention** | Anomaly detection on stock deltas using Isolation Forest — flags theft, admin errors, and receiving discrepancies |
| **Auto-Replenishment** | Dynamic reorder points from forecast velocity, auto-drafts purchase orders when stock falls below threshold |
| **Natural Language Analytics** | Ask questions in plain English, powered by Claude API — returns SQL results and auto-renders charts |

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React + Vite + TypeScript + TailwindCSS + Recharts |
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| Forecasting | Prophet (Meta) |
| Anomaly Detection | scikit-learn (Isolation Forest) |
| NL Queries | Claude API (Anthropic) |
| Deployment | Railway |

## Dataset

[H&M Personalized Fashion Recommendations](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations) — repurposed from recommendation to inventory intelligence.

- 31,788,324 transactions · 105,542 products · 1,371,980 customers
- Date range: September 2018 – September 2020
- Enriched with synthetic stores, stock levels, sizes, pricing, and shrinkage events

## Local Setup

**Prerequisites:** Python 3.11+, PostgreSQL, Node.js 18+

```bash
# 1. Clone and create virtualenv
git clone https://github.com/RaihanRifat222/retail-inventory-ai.git
cd retail-inventory-ai
python -m venv venv && venv\Scripts\activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — set DATABASE_URL and ANTHROPIC_API_KEY

# 4. Download H&M dataset from Kaggle and place CSVs in data/
#    articles.csv, customers.csv, transactions_train.csv

# 5. Run data pipeline (in order)
python app/load_data.py
python app/enrich_data.py
python app/ml/inject_shrinkage.py
python app/ml/build_features.py
python app/ml/train_anomaly.py
python app/ml/replenishment.py

# 6. Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 7. Start frontend (separate terminal)
cd frontend && npm install && npm run dev
```

- **Frontend:** http://localhost:5173
- **API docs:** http://localhost:8000/docs

## Deployment (Railway)

1. Create a Railway project and add a PostgreSQL plugin
2. Set environment variables: `DATABASE_URL`, `ANTHROPIC_API_KEY`
3. Push to GitHub — Railway auto-deploys using `railway.toml`
4. Run the data pipeline scripts once via Railway's shell

## API Endpoints

```
GET  /products/              Product catalogue
GET  /stock/{article_id}     Stock levels by product
GET  /sales/summary          Monthly transaction trends
GET  /sales/top-products     Top products by units sold
GET  /forecast/{article_id}  Demand forecast (7–365 days)
GET  /anomalies/             Loss prevention alerts
GET  /replenishment/         Items at or below reorder point
POST /query/                 Natural language → SQL → results
```
