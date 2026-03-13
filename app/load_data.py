## Load CSV into POSTGRESQL

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

print("Loading articles...")
articles = pd.read_csv("data/articles.csv", dtype=str)
articles.to_sql("articles", engine, if_exists="replace", index=False)
print(f"  Done — {len(articles)} rows")

print("Loading customers...")
customers = pd.read_csv("data/customers.csv", dtype=str)
customers.to_sql("customers", engine, if_exists="replace", index=False)
print(f"  Done — {len(customers)} rows")

print("Loading transactions (this will take a few minutes)...")
chunks = pd.read_csv("data/transactions_train.csv", dtype=str, chunksize=500000)
for i, chunk in enumerate(chunks):
    chunk.to_sql("transactions", engine, if_exists="append" if i > 0 else "replace", index=False)
    print(f"  Chunk {i+1} loaded ({(i+1)*500000:,} rows so far...)")

print("\nAll done! Database is ready.")