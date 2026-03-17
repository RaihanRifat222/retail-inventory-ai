from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import products, stock, sales, forecast, anomalies

app = FastAPI(title="Retail Inventory AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(stock.router, prefix="/stock", tags=["stock"])
app.include_router(sales.router, prefix="/sales", tags=["sales"])
app.include_router(forecast.router, prefix="/forecast", tags=["forecast"]) 
app.include_router(anomalies.router, prefix="/anomalies", tags=["anomalies"])

@app.get("/")
def root():
    return {"status": "ok", "message": "Retail Inventory AI is running"}