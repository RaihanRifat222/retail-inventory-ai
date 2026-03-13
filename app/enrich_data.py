import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import random

load_dotenv()
random.seed(42)
np.random.seed(42)

engine = create_engine(os.getenv("DATABASE_URL"))

# --- Stores ---
print("Creating stores...")
stores = pd.DataFrame([
    {"store_id": 1, "name": "Sydney CBD",    "city": "Sydney",    "country": "Australia"},
    {"store_id": 2, "name": "Melbourne CBD", "city": "Melbourne", "country": "Australia"},
    {"store_id": 3, "name": "Brisbane CBD",  "city": "Brisbane",  "country": "Australia"},
])
stores.to_sql("stores", engine, if_exists="replace", index=False)
print(f"  Done — {len(stores)} stores")

# --- Articles with sizes and cost prices ---
print("Enriching articles...")
articles = pd.read_sql("SELECT article_id, product_type_name, product_group_name, colour_group_name, department_name FROM articles", engine)

SIZE_MAP = {
    "Garment Upper body": ["XS","S","M","L","XL","XXL"],
    "Garment Lower body": ["26","28","30","32","34","36"],
    "Garment Full body":  ["XS","S","M","L","XL"],
    "Shoes":              ["36","37","38","39","40","41","42"],
    "Accessories":        ["ONE SIZE"],
    "Underwear":          ["XS","S","M","L","XL"],
    "Swimwear":           ["XS","S","M","L","XL"],
    "Nightwear":          ["XS","S","M","L","XL"],
    "Socks & Tights":     ["S","M","L"],
    "Bags":               ["ONE SIZE"],
}

DEFAULT_SIZES = ["XS","S","M","L","XL"]

def get_sizes(group):
    return SIZE_MAP.get(group, DEFAULT_SIZES)

articles["available_sizes"] = articles["product_group_name"].apply(
    lambda g: ",".join(get_sizes(g))
)
articles["cost_price"] = np.round(np.random.uniform(5, 80, len(articles)), 2)
articles["retail_price"] = np.round(articles["cost_price"] * np.random.uniform(2.0, 3.5, len(articles)), 2)

articles.to_sql("articles_enriched", engine, if_exists="replace", index=False)
print(f"  Done — {len(articles)} articles enriched")

# --- Stock levels (one row per article per store) ---
print("Generating stock levels...")
store_ids = [1, 2, 3]
records = []

for _, row in articles.iterrows():
    sizes = row["available_sizes"].split(",")
    for store_id in store_ids:
        for size in sizes:
            records.append({
                "article_id": row["article_id"],
                "store_id":   store_id,
                "size":       size,
                "quantity":   int(np.random.choice(
                    [0, 0, 2, 5, 8, 12, 20],
                    p=[0.15, 0.10, 0.20, 0.25, 0.15, 0.10, 0.05]
                )),
            })

print(f"  Writing {len(records):,} stock rows to database...")
stock_df = pd.DataFrame(records)
stock_df.to_sql("stock_levels", engine, if_exists="replace", index=False, chunksize=10000)
print(f"  Done — {len(stock_df):,} rows")

print("\nAll done! Enriched data is ready.")