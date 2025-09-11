from datetime import datetime
from typing import List, Dict

def get_success(i : List[Dict] | Dict, item_key : str = "items"):
    """
    Get the JSON based dictionary of response to API call.

    Args:
        i (List[Dict] | Dict) : item(s) to send as return from API request
        item_key (str) default "items" : name of field with the data fetched

    Returns:
        Dict with data fetched and time of fetch. 
    """
    return { 
        f"{item_key}" : i,
        "time" : str(datetime.now())
    }


def get_error(message: str):
    """
    Get the JSON based dictionary of response to API call when an error occurs.

    Args:
        message (str) : message to send explaining the error.

    Returns:
        Dict with field message and time.
    """
    return { 
        "message" : message,
        "time" : str(datetime.now())
    }