from fastapi import FastAPI
from enum import Enum
from datetime import datetime
from pydantic import BaseModel

app = FastAPI()

class BeverageType(int, Enum):
    COCKTAIL = 1
    GIN = 2
    BEER = 3
    WINE = 4
    VODKA = 5

    @classmethod
    def _missing_(cls, value):
        return BeverageType.COCKTAIL
    
    def __str__(self) -> str:
        return super().__str__()

class Beverage(BaseModel):
    name : str
    description: str | None = ""
    beverage_type: BeverageType
    base_beverage: BeverageType | None
    ingredients : list[dict] | None
    tags: list[str] | None = []
    default_images : list[str] | None = []
    sum_score : int
    count_score : int

@app.get("/beverages")
async def get_beverages(beverage : BeverageType = BeverageType.COCKTAIL):
    return {
        "message": "Hello World", 
        "beverage_list": beverage, 
        "time" : datetime.now()}


@app.get("/beverages/{id}")
async def get_beverage(id : int):
    beverage_list : list[str] = [e.name for e in BeverageType]
    return {
        "message": "Hello World", 
        "id" : id, 
        "bv_list" : beverage_list, 
        "time" : datetime.now()}


@app.post("/beverages")
async def add_beverage(beverage : Beverage):
    return {"message": "Hello POST", "beverage" : beverage, "time" : datetime.now()}