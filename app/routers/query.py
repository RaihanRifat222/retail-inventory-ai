from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from app.database import get_db
import anthropic
import os
import re

router = APIRouter()

SCHEMA_CONTEXT = """
PostgreSQL database schema for a retail inventory system:

- transactions (t_dat DATE, customer_id TEXT, article_id TEXT, price FLOAT, sales_channel_id INTEGER)
  -- 31.7M rows, dates from 2018-09-20 to 2020-09-22
- articles (article_id TEXT PK, product_type_name TEXT, product_group_name TEXT, colour_group_name TEXT, department_name TEXT, section_name TEXT, garment_group_name TEXT)
- articles_enriched (article_id TEXT PK, product_type_name TEXT, product_group_name TEXT, colour_group_name TEXT, department_name TEXT, available_sizes TEXT, cost_price FLOAT, retail_price FLOAT)
- customers (customer_id TEXT PK, age INTEGER, club_member_status TEXT, active INTEGER)
- stores (store_id INTEGER PK, name TEXT, city TEXT, country TEXT)
  -- 3 rows: Sydney CBD (1), Melbourne CBD (2), Brisbane CBD (3)
- stock_levels (article_id TEXT, store_id INTEGER, size TEXT, quantity INTEGER)
- anomaly_scores (article_id TEXT, store_id INTEGER, total_stock FLOAT, stock_delta FLOAT, anomaly_score FLOAT, severity TEXT, is_anomaly BOOLEAN, predicted_at TIMESTAMP)
- purchase_orders (article_id TEXT, store_id INTEGER, total_stock FLOAT, avg_daily_velocity FLOAT, days_of_stock_remaining FLOAT, reorder_point FLOAT, suggested_order_qty INTEGER, status TEXT)
  -- status values: 'critical', 'reorder', 'ok'

Notes:
- transactions.price is normalised (not real currency, values typically 0.01–0.10)
- Always include LIMIT (max 500) on large table queries
- Use DATE_TRUNC for time grouping
"""

SYSTEM_PROMPT = (
    "You are a SQL expert for a retail inventory PostgreSQL database. "
    "When given a natural language question, return ONLY a single valid PostgreSQL SELECT query — "
    "no explanation, no markdown, no code fences. "
    "Always add a LIMIT clause (max 500 rows). Only SELECT is allowed."
)


class QueryRequest(BaseModel):
    question: str


def extract_sql(text_response: str) -> str:
    """Strip any accidental markdown fences from Claude's response."""
    cleaned = re.sub(r"```(?:sql)?", "", text_response, flags=re.IGNORECASE).replace("```", "")
    return cleaned.strip()


def is_safe_sql(sql: str) -> bool:
    upper = sql.upper().strip()
    if not upper.startswith("SELECT"):
        return False
    dangerous = ["DROP", "DELETE", "INSERT", "UPDATE", "TRUNCATE", "ALTER", "CREATE", "GRANT"]
    return not any(kw in upper for kw in dangerous)


@router.post("/")
def run_nl_query(body: QueryRequest, db: Session = Depends(get_db)):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {"error": "ANTHROPIC_API_KEY not configured"}

    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Schema:\n{SCHEMA_CONTEXT}\n\nQuestion: {body.question}",
            }
        ],
    )

    sql = extract_sql(message.content[0].text)

    if not is_safe_sql(sql):
        return {"error": "Generated query was not a safe SELECT statement.", "sql": sql}

    try:
        result = db.execute(text(sql))
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        return {"question": body.question, "sql": sql, "columns": columns, "rows": rows}
    except Exception as e:
        return {"error": str(e), "sql": sql}
