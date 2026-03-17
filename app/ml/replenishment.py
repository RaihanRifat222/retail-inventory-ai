import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

LEAD_TIME_DAYS = 14       # Days from order to delivery
SAFETY_STOCK_DAYS = 7     # Buffer stock to hold above reorder point
ORDER_CYCLE_DAYS = 30     # How many days of stock to order at a time

print("Loading feature matrix...")
features = pd.read_sql(text("""
    SELECT article_id, store_id, total_stock, avg_daily_velocity, price_tier
    FROM feature_matrix
    WHERE avg_daily_velocity > 0
"""), engine)

print(f"  Loaded {len(features):,} article-store rows with positive velocity")

# Reorder point = stock needed to cover lead time + safety buffer
features["reorder_point"] = (
    features["avg_daily_velocity"] * (LEAD_TIME_DAYS + SAFETY_STOCK_DAYS)
).round(2)

# Days of stock remaining at current velocity
features["days_of_stock_remaining"] = (
    features["total_stock"] / features["avg_daily_velocity"]
).round(1).clip(upper=999)

# Suggested order quantity to reach ORDER_CYCLE_DAYS of cover
features["suggested_order_qty"] = (
    (features["avg_daily_velocity"] * ORDER_CYCLE_DAYS) - features["total_stock"]
).clip(lower=0).round(0).astype(int)

# Status classification
def classify_status(row):
    if row["days_of_stock_remaining"] < LEAD_TIME_DAYS:
        return "critical"     # Will stock out before order arrives
    elif row["total_stock"] <= row["reorder_point"]:
        return "reorder"      # At or below reorder point — order now
    else:
        return "ok"

features["status"] = features.apply(classify_status, axis=1)
features["computed_at"] = datetime.utcnow()

# Only persist items that need attention or are borderline
purchase_orders = features[[
    "article_id", "store_id", "total_stock", "avg_daily_velocity",
    "days_of_stock_remaining", "reorder_point", "suggested_order_qty",
    "status", "computed_at"
]]

status_counts = features["status"].value_counts()
print(f"\nStatus breakdown:")
for status, count in status_counts.items():
    print(f"  {status}: {count:,}")

print(f"\nWriting {len(purchase_orders):,} rows to purchase_orders table...")
purchase_orders.to_sql("purchase_orders", engine, if_exists="replace", index=False)

print("Done. Auto-replenishment engine complete.")
