from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter()

@router.get("/summary")
def get_sales_summary(db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT
            DATE_TRUNC('month', t_dat::date) as month,
            COUNT(*) as transactions,
            ROUND(SUM(price::numeric), 2) as total_revenue
        FROM transactions
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
    """))
    rows = result.mappings().all()
    return {"monthly_sales": [dict(r) for r in rows]}

@router.get("/top-products")
def get_top_products(limit: int = 10, db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT
            t.article_id,
            a.product_type_name,
            a.colour_group_name,
            COUNT(*) as units_sold
        FROM transactions t
        JOIN articles_enriched a ON t.article_id = a.article_id
        GROUP BY t.article_id, a.product_type_name, a.colour_group_name
        ORDER BY units_sold DESC
        LIMIT :limit
    """), {"limit": limit})
    rows = result.mappings().all()
    return {"top_products": [dict(r) for r in rows]}