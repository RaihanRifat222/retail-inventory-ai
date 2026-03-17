import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

print("Loading anomaly scores...")
scores = pd.read_sql("SELECT * FROM anomaly_scores", engine)

print("Loading shrinkage events...")
shrinkage = pd.read_sql("SELECT * FROM shrinkage_events", engine)

print("\n--- Model Evaluation ---\n")

print(f"Total SKUs scored:        {len(scores):,}")
print(f"Total flagged:            {scores['is_anomaly'].sum():,} ({scores['is_anomaly'].mean()*100:.1f}%)")
print(f"Total shrinkage events:   {len(shrinkage):,}")

# Match shrinkage events to anomaly scores
merged = shrinkage.merge(
    scores[["article_id", "store_id", "is_anomaly", "anomaly_score", "severity"]],
    on=["article_id", "store_id"],
    how="left"
)

merged["is_anomaly"] = merged["is_anomaly"].fillna(False)

print(f"\n--- Coverage by event type ---\n")
for event_type in merged["event_type"].unique():
    subset = merged[merged["event_type"] == event_type]
    caught = subset["is_anomaly"].sum()
    total = len(subset)
    print(f"  {event_type:<30} {caught:>4} / {total} caught ({caught/total*100:.1f}%)")

print(f"\n--- Overall catch rate ---")
total_caught = merged["is_anomaly"].sum()
print(f"  {total_caught} / {len(merged)} shrinkage events flagged ({total_caught/len(merged)*100:.1f}%)")

print(f"\n--- Top 20 flagged anomalies ---\n")
top = scores[scores["is_anomaly"]].sort_values("anomaly_score").head(20)
top = top.merge(
    pd.read_sql("SELECT article_id, product_type_name FROM articles_enriched", engine),
    on="article_id", how="left"
)
top = top.merge(
    pd.read_sql("SELECT store_id, name as store_name FROM stores", engine),
    on="store_id", how="left"
)

for _, row in top.iterrows():
    print(
        f"  [{row['severity'].upper():<6}] {row['product_type_name']:<25} "
        f"store: {row['store_name']:<15} "
        f"expected: {row['expected_stock']:>7.1f}  "
        f"actual: {row['total_stock']:>4}  "
        f"delta: {row['stock_delta']:>8.1f}  "
        f"score: {row['anomaly_score']:.4f}"
    )