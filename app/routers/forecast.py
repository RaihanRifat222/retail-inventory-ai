from fastapi import APIRouter, Query
from app.ml.forecasting import forecast_product

router = APIRouter()

@router.get("/{article_id}")
def get_forecast(
    article_id: str,
    days: int = Query(default=90, ge=7, le=365)
):
    return forecast_product(article_id, days)