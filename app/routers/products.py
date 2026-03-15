from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter()

@router.get("/")
def get_products(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT article_id, product_type_name, product_group_name,
               colour_group_name, department_name,
               available_sizes, cost_price, retail_price
        FROM articles_enriched
        LIMIT :limit OFFSET :offset
    """), {"limit": limit, "offset": offset})
    rows = result.mappings().all()
    return {"total": len(rows), "products": [dict(r) for r in rows]}

@router.get("/{article_id}")
def get_product(article_id: str, db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT article_id, product_type_name, product_group_name,
               colour_group_name, department_name,
               available_sizes, cost_price, retail_price
        FROM articles_enriched
        WHERE article_id = :article_id
    """), {"article_id": article_id})
    row = result.mappings().first()
    if not row:
        return {"error": "Product not found"}
    return dict(row)