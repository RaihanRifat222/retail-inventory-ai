# Retail Inventory AI

An AI-powered inventory management platform for fashion and apparel retailers.

## Features
- Demand forecasting (Prophet)
- Loss prevention / anomaly detection (scikit-learn)
- Auto-replenishment engine (XGBoost)
- Natural language analytics (Claude API)

## Stack
- **Backend:** Python, FastAPI, SQLAlchemy
- **Frontend:** React, Vite, TailwindCSS
- **Database:** PostgreSQL
- **AI/ML:** Prophet, scikit-learn, XGBoost, Claude API

## Setup

1. Clone the repo
2. Create a virtual environment: `python -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Create a `.env` file with your `DATABASE_URL`
5. Download the H&M dataset from Kaggle and place CSVs in `data/`
6. Run `python app/load_data.py` to load the dataset
7. Run `python app/enrich_data.py` to generate synthetic data

## Build Log
| Day | Goal | Status |
|-----|------|--------|
| 1 | Environment + data loaded | ✅ Done |
| 2 | Synthetic data enrichment | ✅ Done |
| 3 | FastAPI backend | 🔄 Next |