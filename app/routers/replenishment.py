from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter()

@router.get("/")
def get_replenishment(
    store_id: int = Query(default=None),
    status: str = Query(default=None, description="Filter by status: critical, reorder, ok"),
    limit: int = Query(default=50, le=500),
    db: Session = Depends(get_db)
):
    filters = ["p.status != 'ok'"]
    params = {"limit": limit}

    if store_id:
        filters.append("p.store_id = :store_id")
        params["store_id"] = store_id

    if status:
        filters.append("p.status = :status")
        params["status"] = status

    where_clause = " AND ".join(filters)

    result = db.execute(text(f"""
        SELECT
            p.article_id,
            a.product_type_name,
            a.product_group_name,
            a.colour_group_name,
            a.retail_price,
            s.name as store_name,
            p.store_id,
            p.total_stock,
            p.avg_daily_velocity,
            p.days_of_stock_remaining,
            p.reorder_point,
            p.suggested_order_qty,
            p.status,
            p.computed_at
        FROM purchase_orders p
        JOIN articles_enriched a ON p.article_id = a.article_id
        JOIN stores s ON p.store_id = s.store_id
        WHERE {where_clause}
        ORDER BY
            CASE p.status
                WHEN 'critical' THEN 1
                WHEN 'reorder' THEN 2
                ELSE 3
            END,
            p.days_of_stock_remaining ASC
        LIMIT :limit
    """), params)

    rows = result.mappings().all()

    return {
        "total": len(rows),
        "filters": {"store_id": store_id, "status": status},
        "items": [dict(r) for r in rows]
    }


@router.get("/summary")
def get_replenishment_summary(db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT
            s.name as store_name,
            p.store_id,
            p.status,
            COUNT(*) as item_count,
            ROUND(SUM(p.suggested_order_qty)::numeric, 0) as total_units_to_order,
            ROUND(AVG(p.days_of_stock_remaining)::numeric, 1) as avg_days_remaining
        FROM purchase_orders p
        JOIN stores s ON p.store_id = s.store_id
        GROUP BY s.name, p.store_id, p.status
        ORDER BY p.store_id,
            CASE p.status
                WHEN 'critical' THEN 1
                WHEN 'reorder' THEN 2
                ELSE 3
            END
    """))
    rows = result.mappings().all()
    return {"summary": [dict(r) for r in rows]}
