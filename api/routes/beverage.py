from fastapi import APIRouter, status, HTTPException
from services import s3, beverage, dynamodb, json
import logging
from models.beverage import BeverageType, Beverage

router = APIRouter()

logger = logging.getLogger("uvicorn.error")  # uvicorn logs

@router.get("/", status_code=status.HTTP_200_OK)
async def get_beverages(b_type : BeverageType | None = None):
    pk : str = beverage.arrange_pk(b_type)
    response = dynamodb.get_beverages(pk)

    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        return json.get_error(500, "An error occurred when trying to fetch the data")

    items = beverage.arrange_list_of_beverages(response)
    return json.get_beverage(items, "items")

@router.get("/pk/{pk}/sk/{sk}", status_code=status.HTTP_200_OK)
async def get_beverage(pk : str, sk : str):

    response = dynamodb.get_beverage(pk, sk)
    if response[0] != 200:
        return json.get_error(response[0], response[1]["message"])
    
    item = beverage.arrange_beverage(response[1])
    return json.get_beverage(item, "item")

@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_beverage(b : Beverage):
    logger.info("Attempting to insert new beverage")

    item = beverage.arrange_item(b)

    response = dynamodb.put_beverage(item)

    item = beverage.arrange_beverage({"Items" : [item]})

    if response[0] != 201:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot override existing item")
    
    return json.get_beverage(item)


# TODO when pk or sk change, must delete previous item and create new one (update then reviews as well)
@router.put("/pk/{pk}/sk/{sk}")
async def edit_beverage(pk : str, sk : str,  b : Beverage):

    item = beverage.arrange_item(b, False)
        
    (
        update_expression, 
        expression_attribute_names, 
        expression_attribute_values
    ) = dynamodb.set_expression_to_edit_beverage(b)
    
    response = dynamodb.edit_beverage(pk, sk, update_expression, expression_attribute_values, expression_attribute_names)
    
    if response[0] != 200:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=response[1]["message"])

    item = beverage.arrange_beverage({"Items" : [ response[1]["beverage"]["Attributes"] ]})
    return json.get_beverage(item)

# TODO delete reviews after deleting beverage
@router.delete("/pk/{pk}/sk/{sk}", status_code=status.HTTP_202_ACCEPTED)
async def delete_beverage(pk : str, sk : str):
    response = dynamodb.delete_beverage(pk, sk)    

    if response[0] != 204:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response[1]["message"])
    
    item = beverage.arrange_beverage({"Items" : [response[1]]})
    return json.get_beverage(item, "item")