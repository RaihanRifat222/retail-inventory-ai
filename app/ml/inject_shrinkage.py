import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import random

load_dotenv()
random.seed(42)
np.random.seed(42)

engine = create_engine(os.getenv("DATABASE_URL"))

print("Loading articles and stock levels...")
articles = pd.read_sql("SELECT article_id FROM articles_enriched", engine)
article_ids = articles["article_id"].tolist()
store_ids = [1, 2, 3]

records = []

# --- Theft events (~800) ---
# Sudden unexplained stock drops on specific SKUs
print("Generating theft events...")
for _ in range(800):
    article_id = random.choice(article_ids)
    store_id = random.choice(store_ids)
    expected = random.randint(10, 30)
    delta = random.randint(2, int(expected * 0.4))
    records.append({
        "event_type": "theft",
        "article_id": article_id,
        "store_id": store_id,
        "expected_qty": expected,
        "actual_qty": expected - delta,
        "delta": -delta,
    })

# --- Admin errors (~700) ---
# Duplicate entries or reversed adjustments
print("Generating admin error events...")
for _ in range(700):
    article_id = random.choice(article_ids)
    store_id = random.choice(store_ids)
    expected = random.randint(5, 20)
    delta = random.randint(1, 5) * random.choice([-1, 1])
    records.append({
        "event_type": "admin_error",
        "article_id": article_id,
        "store_id": store_id,
        "expected_qty": expected,
        "actual_qty": expected + delta,
        "delta": delta,
    })

# --- Receiving discrepancies (~500) ---
# Quantity received differs from what was ordered
print("Generating receiving discrepancy events...")
for _ in range(500):
    article_id = random.choice(article_ids)
    store_id = random.choice(store_ids)
    expected = random.randint(20, 50)
    delta = random.randint(3, 10) * random.choice([-1, -1, 1])  # mostly short-shipped
    records.append({
        "event_type": "receiving_discrepancy",
        "article_id": article_id,
        "store_id": store_id,
        "expected_qty": expected,
        "actual_qty": expected + delta,
        "delta": delta,
    })

df = pd.DataFrame(records)
df["created_at"] = pd.Timestamp("now")

print(f"Writing {len(df)} shrinkage events to database...")
df.to_sql("shrinkage_events", engine, if_exists="replace", index=False)
print(f"Done — {len(df)} events written")
print(df["event_type"].value_counts())