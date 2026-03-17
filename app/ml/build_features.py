import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

print("Computing daily sales velocity per article...")
velocity_df = pd.read_sql(text("""
    SELECT
        article_id,
        COUNT(*) as total_units_sold,
        COUNT(DISTINCT t_dat::date) as days_with_sales,
        MIN(t_dat::date) as first_sale,
        MAX(t_dat::date) as last_sale
    FROM transactions
    GROUP BY article_id
"""), engine)

velocity_df["date_range_days"] = (
    pd.to_datetime(velocity_df["last_sale"]) -
    pd.to_datetime(velocity_df["first_sale"])
).dt.days.clip(lower=1)

velocity_df["avg_daily_velocity"] = (
    velocity_df["total_units_sold"] / velocity_df["date_range_days"]
).round(4)

velocity_df["days_since_last_sale"] = (
    pd.Timestamp("2020-09-22") -
    pd.to_datetime(velocity_df["last_sale"])
).dt.days

print(f"  Velocity computed for {len(velocity_df)} articles")

print("Loading stock levels...")
stock_df = pd.read_sql(text("""
    SELECT
        article_id,
        store_id,
        SUM(quantity) as total_stock
    FROM stock_levels
    GROUP BY article_id, store_id
"""), engine)

print("Loading price tier from articles_enriched...")
price_df = pd.read_sql(text("""
    SELECT article_id, retail_price
    FROM articles_enriched
"""), engine)

price_df["price_tier"] = pd.cut(
    price_df["retail_price"],
    bins=[0, 30, 80, 150, 99999],
    labels=[1, 2, 3, 4]
).astype(int)

print("Joining everything together...")
features = stock_df.merge(velocity_df[[
    "article_id", "avg_daily_velocity",
    "days_since_last_sale", "total_units_sold"
]], on="article_id", how="left")

features = features.merge(
    price_df[["article_id", "price_tier"]],
    on="article_id", how="left"
)

features["avg_daily_velocity"] = features["avg_daily_velocity"].fillna(0)
features["days_since_last_sale"] = features["days_since_last_sale"].fillna(999)
features["price_tier"] = features["price_tier"].fillna(1).astype(int)

DAYS_SNAPSHOT = 30
features["expected_stock"] = (
    features["avg_daily_velocity"] * DAYS_SNAPSHOT
).round(2).clip(upper=200)

features["stock_delta"] = (
    features["total_stock"] - features["expected_stock"]
).round(2)

features["delta_pct"] = np.where(
    features["expected_stock"] > 0,
    (features["stock_delta"] / features["expected_stock"] * 100).round(2),
    0
)
features["delta_pct"] = features["delta_pct"].clip(lower=-100, upper=500)

print(f"Writing {len(features):,} rows to feature_matrix table...")
features.to_sql("feature_matrix", engine, if_exists="replace", index=False)

print("\nDone. Feature matrix summary:")
print(features[["total_stock", "expected_stock", "stock_delta", "delta_pct", "avg_daily_velocity"]].describe().round(2))