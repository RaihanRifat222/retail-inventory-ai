from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter()

@router.get("/")
def get_anomalies(
    store_id: int = Query(default=None),
    severity: str = Query(default=None),
    limit: int = Query(default=50),
    db: Session = Depends(get_db)
):
    filters = ["a.is_anomaly = true"]
    params = {"limit": limit}

    if store_id:
        filters.append("a.store_id = :store_id")
        params["store_id"] = store_id

    if severity:
        filters.append("a.severity = :severity")
        params["severity"] = severity

    where_clause = " AND ".join(filters)

    result = db.execute(text(f"""
        SELECT
            a.article_id,
            ar.product_type_name,
            ar.product_group_name,
            ar.colour_group_name,
            s.name as store_name,
            a.store_id,
            a.total_stock,
            a.expected_stock,
            a.stock_delta,
            a.delta_pct,
            a.anomaly_score,
            a.severity,
            a.predicted_at
        FROM anomaly_scores a
        JOIN articles_enriched ar ON a.article_id = ar.article_id
        JOIN stores s ON a.store_id = s.store_id
        WHERE {where_clause}
        ORDER BY a.anomaly_score ASC
        LIMIT :limit
    """), params)

    rows = result.mappings().all()

    return {
        "total": len(rows),
        "filters": {
            "store_id": store_id,
            "severity": severity
        },
        "anomalies": [dict(r) for r in rows]
    }

@router.get("/summary")
def get_anomaly_summary(db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT
            severity,
            COUNT(*) as count,
            ROUND(AVG(stock_delta)::numeric, 2) as avg_delta,
            ROUND(AVG(delta_pct)::numeric, 2) as avg_delta_pct
        FROM anomaly_scores
        WHERE is_anomaly = true
        GROUP BY severity
        ORDER BY
            CASE severity
                WHEN 'high' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'low' THEN 3
            END
    """))
    rows = result.mappings().all()
    return {"summary": [dict(r) for r in rows]}