from fastapi import FastAPI
from api import beverage_router, beverage_type_router

app = FastAPI(title="Barista API", version="0.1.0")

app.include_router(beverage_router, prefix="/beverages", tags=["beverage"])
app.include_router(beverage_type_router, prefix="/beverage_types", tags=["beverage_type"])
