from models.beverage import BeverageType, Beverage
from services import s3
from typing import Dict
from datetime import datetime
import logging

logger = logging.getLogger("uvicorn.error")  # uvicorn logs

def arrange_pk(beverage : BeverageType | None = None) -> str:
    return  f"CATEGORY#{ "" if beverage == None else str(beverage).split(".")[1] }"

def arrange_sk(b_type : BeverageType | str, b_name : str):
    return f"{str(b_type).split(".")[1] if isinstance(b_type, BeverageType) else b_type}#{b_name}"

def arrange_list_of_beverages(response):
    items = []
    default_url = None
    
    for i in  range(len(response["Items"])):
        item = __arrange_item(response["Items"][i])
        
        if item["default_image"] == "":
            logger.info("No image")
            if not default_url:
                default_url = s3.get_image()
            item["default_image"] = default_url
        else:
            item["default_image"] = s3.get_image(item["default_image"])
        items.append(item)
        
    return items

# boto3 to JSON
def arrange_beverage(response : Dict) -> Dict:
    item = __arrange_item(response["Items"][0])
    
    if item["default_image"] == "":
        item["default_image"] = s3.get_image()
    else:
        item["default_image"] = s3.get_image(item["default_image"])

    return item


# JSON to boto3
def arrange_item(b : Beverage, method_post: bool = True):
    pk = arrange_pk(b.beverage_type)
    sk = arrange_sk(b.base_beverage, b.name)
    dt = datetime.now()

    item = {
                'pk': {'S': pk},
                'sk': {'S': sk},
                "tags": {"L": [{"S": tag} for tag in (b.tags)]},
                'description': {'S': b.description},
                'updated_at' : {'S' : str(dt)}
            }

    if b.beverage_type == BeverageType.COCKTAIL:
        item["ingredients"] = {
            'L': [
                {
                    'M': {
                        'name': {'S': ing["name"]},
                        'quantity': {'N': str(ing["quantity"])},
                        'quantity_type': {'S': ing["quantity_type"]}
                    }
                } 
                for ing in (b.ingredients or [])
            ]
        }

    if method_post:
        item["inserted_at"] = {'S' : str(dt)}
        item["sum_score"] = {'N': str(0)}
        item["count_score"] = {'N': str(0)}
        item["default_image"] = {'S': ""}

    return item

# bot3 to json
def __arrange_item(response : Dict) -> Dict:
    beverage_type = response["pk"]["S"].split("#")[1]
    base_beverage = response["sk"]["S"].split("#")[0]
    name = response["sk"]["S"].split("#")[1]
    tags = [ tag["S"] for tag in response["tags"]["L"]]

    item = {
        "beverage_type" : beverage_type,
        "base_beverage" : base_beverage,
        "description" : response["description"]["S"],
        "name" : name,
        "inserted_at" : response["inserted_at"]["S"],
        "updated_at" : response["updated_at"]["S"],
        "tags" : tags,
        "default_image" : response["default_image"]["S"],
        "sum_score" : int(response["sum_score"]["N"]),
        "count_score" : int(response["count_score"]["N"]),
    }

    if "ingredients" in response : 
        item["ingredients"] = [{
                "name" : ingredient["M"]["name"]["S"],
                "quantity" : ingredient["M"]["quantity"]["N"],
                "quantity_type" : ingredient["M"]["quantity_type"]["S"] 
            } for ingredient in response["ingredients"]["L"]
        ]

    return item