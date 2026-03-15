from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter()

@router.get("/{article_id}")
def get_stock(article_id: str, db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT s.article_id, s.store_id, st.name as store_name,
               s.size, s.quantity
        FROM stock_levels s
        JOIN stores st ON s.store_id = st.store_id
        WHERE s.article_id = :article_id
        ORDER BY s.store_id, s.size
    """), {"article_id": article_id})
    rows = result.mappings().all()
    if not rows:
        return {"error": "No stock found for this product"}
    return {"article_id": article_id, "stock": [dict(r) for r in rows]}

@router.get("/low/alert")
def get_low_stock(threshold: int = 3, db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT s.article_id, a.product_type_name, s.store_id,
               st.name as store_name, s.size, s.quantity
        FROM stock_levels s
        JOIN articles_enriched a ON s.article_id = a.article_id
        JOIN stores st ON s.store_id = st.store_id
        WHERE s.quantity <= :threshold
        ORDER BY s.quantity ASC
        LIMIT 50
    """), {"threshold": threshold})
    rows = result.mappings().all()
    return {"low_stock_items": [dict(r) for r in rows]}