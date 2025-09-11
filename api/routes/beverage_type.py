from fastapi import APIRouter, status
from models.beverage import BeverageType
from services import json
import logging

router = APIRouter()
logger = logging.getLogger("uvicorn.error")

@router.get("", status_code=status.HTTP_200_OK)
async def get_beverage_types():
    logger.info("Attempting to get list of beverage types")
    beverage__types : list[dict] = [ 
        {
            "id" : e.value, 
            "value" : str(e).split(".")[1].title()
        } for e in BeverageType ]
    
    logger.info("Obtained list of beverage types successfully")
    return json.get_success(beverage__types, "items")