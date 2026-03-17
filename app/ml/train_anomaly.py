import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from dotenv import load_dotenv
import os
import pickle

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

print("Loading feature matrix...")
features = pd.read_sql("SELECT * FROM feature_matrix", engine)

FEATURE_COLS = [
    "stock_delta",
    "delta_pct",
    "avg_daily_velocity",
    "days_since_last_sale",
    "price_tier"
]

X = features[FEATURE_COLS].fillna(0)

print("Scaling features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print("Training Isolation Forest...")
model = IsolationForest(
    contamination=0.05,
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)
model.fit(X_scaled)

print("Scoring all SKUs...")
features["anomaly_label"] = model.predict(X_scaled)
features["anomaly_score"] = model.score_samples(X_scaled)

features["is_anomaly"] = features["anomaly_label"] == -1

features["severity"] = "normal"
features.loc[features["is_anomaly"] & (features["anomaly_score"] > -0.62), "severity"] = "low"
features.loc[features["is_anomaly"] & (features["anomaly_score"].between(-0.68, -0.62)), "severity"] = "medium"
features.loc[features["is_anomaly"] & (features["anomaly_score"] < -0.68), "severity"] = "high"
anomaly_scores = features[[
    "article_id", "store_id",
    "total_stock", "expected_stock", "stock_delta", "delta_pct",
    "anomaly_score", "is_anomaly", "severity"
]].copy()
anomaly_scores["predicted_at"] = pd.Timestamp("now")

print(f"Writing {len(anomaly_scores):,} rows to anomaly_scores table...")
anomaly_scores.to_sql("anomaly_scores", engine, if_exists="replace", index=False)

os.makedirs("models", exist_ok=True)
with open("models/isolation_forest.pkl", "wb") as f:
    pickle.dump({"model": model, "scaler": scaler}, f)

print("\nDone. Results summary:")
print(f"  Total SKUs scored:  {len(features):,}")
print(f"  Flagged anomalies:  {features['is_anomaly'].sum():,} ({features['is_anomaly'].mean()*100:.1f}%)")
print(f"\n  Severity breakdown:")
print(features[features["is_anomaly"]]["severity"].value_counts())