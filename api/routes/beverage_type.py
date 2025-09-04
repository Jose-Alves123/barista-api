from fastapi import APIRouter, status
from datetime import datetime
from models.beverage import BeverageType
import logging

router = APIRouter()
logger = logging.getLogger("uvicorn.error")

@router.get("", status_code=status.HTTP_200_OK)
async def get_beverage_types():

    beverage__types : list[dict] = [ 
        {
            "id" : e.value, 
            "value" : str(e).split(".")[1].title()
        } for e in BeverageType ]
    
    return {
        "status" : 200,
        "beverage_types" : beverage__types,
        "time" : datetime.now()
    }