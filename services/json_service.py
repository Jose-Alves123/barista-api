from datetime import datetime
from models.beverage import Beverage
from typing import List, Dict


def get_beverage(b : List[Dict] | Dict, item_key : str = "items"):
    """"
    Get the JSON based dictionary of response to API call.
    """
    return { 
        f"{item_key}" : b,
        "time" : str(datetime.now())
    }


def get_error(status: int, message: str):
    """"
    Get the JSON based dictionary of response to API call when an error occurs.
    """
    return { 
        "message" : message,
        "time" : str(datetime.now())
    }