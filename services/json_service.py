from datetime import datetime
from models.beverage import Beverage
from typing import List, Dict


def get_beverage(b : List[Dict] | Dict, item_key : str = "items"):
    return { 
        f"{item_key}" : b,
        "time" : str(datetime.now())
    }


def get_error(status: int, message: str):
    return { 
        "message" : message,
        "time" : str(datetime.now())
    }