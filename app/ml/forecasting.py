import pandas as pd
from prophet import Prophet
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import warnings
warnings.filterwarnings("ignore")

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

def get_sales_history(article_id: str) -> pd.DataFrame:
    query = text("""
        SELECT t_dat::date as ds, COUNT(*) as y
        FROM transactions
        WHERE article_id = :article_id
        GROUP BY t_dat::date
        ORDER BY ds
    """)
    df = pd.read_sql(query, engine, params={"article_id": article_id})
    df["ds"] = pd.to_datetime(df["ds"])
    return df

def forecast_product(article_id: str, days: int = 90) -> dict:
    df = get_sales_history(article_id)

    if len(df) < 10:
        return {"error": "Not enough sales history to forecast this product"}

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=0.05
    )
    model.fit(df)

    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)

    result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(days)
    result = result.copy()
    result["ds"] = result["ds"].dt.strftime("%Y-%m-%d")
    result["yhat"] = result["yhat"].clip(lower=0).round(2)
    result["yhat_lower"] = result["yhat_lower"].clip(lower=0).round(2)
    result["yhat_upper"] = result["yhat_upper"].clip(lower=0).round(2)

    return {
        "article_id": article_id,
        "forecast_days": days,
        "forecast": result.to_dict(orient="records")
    }