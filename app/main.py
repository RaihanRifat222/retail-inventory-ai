import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import products, stock, sales, forecast, anomalies, replenishment, query

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
app.include_router(replenishment.router, prefix="/replenishment", tags=["replenishment"])
app.include_router(query.router, prefix="/query", tags=["query"])

# Serve built React frontend (production / Railway)
DIST_DIR = "frontend/dist"

@app.get("/", include_in_schema=False)
def root():
    if os.path.isfile(os.path.join(DIST_DIR, "index.html")):
        return FileResponse(os.path.join(DIST_DIR, "index.html"))
    return {"status": "ok", "message": "Retail Inventory AI is running"}

@app.get("/{full_path:path}", include_in_schema=False)
def serve_frontend(full_path: str):
    file_path = os.path.join(DIST_DIR, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(DIST_DIR, "index.html"))
