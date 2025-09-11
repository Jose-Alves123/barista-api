from fastapi import APIRouter, status, HTTPException
from services import s3, beverage, dynamodb, json
import logging
from models.beverage import BeverageType, Beverage

router = APIRouter()

logger = logging.getLogger("uvicorn.error")  # uvicorn logs

@router.get("/", status_code=status.HTTP_200_OK)
async def get_beverages(b_type : BeverageType | None = None):
    logger.info("Attempting to obtain list of beverages")
    pk : str = beverage.arrange_pk(b_type)
    response = dynamodb.get_beverages(pk)

    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        logger.info("Failed to obtain list of beverages")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=json.get_error("An error occurred when trying to fetch the data"))

    items = beverage.arrange_list_of_beverages(response)
    logger.info("Obtained list of beverages successfully")

    return json.get_success(items, "items")

@router.get("/pk/{pk}/sk/{sk}", status_code=status.HTTP_200_OK)
async def get_beverage(pk : str, sk : str):
    logger.info(f"Attempting to obtain beverage with pk - {pk} and sk - {sk}")
    response = dynamodb.get_beverage(pk, sk)

    if response[0] == 404:
        logger.info(f"Failed to obtain beverage with pk - {pk} and sk - {sk} - not found")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=json.get_error(response[1]["message"]))
    
    if response[0] != 200:
        logger.info(f"Failed to obtain beverage with pk - {pk} and sk - {sk} - boto3 error")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=json.get_error(response[1]["message"]))
    
    item = beverage.arrange_beverage(response[1])
    logger.info(f"Obtained beverage with pk - {pk} and sk - {sk} successfully")

    return json.get_success(item, "item")

@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_beverage(b : Beverage):
    logger.info("Attempting to insert new beverage")

    item = beverage.arrange_item(b)
    response = dynamodb.put_beverage(item)
    item = beverage.arrange_beverage({"Items" : [item]})

    if response[0] != 201:
        logger.info("Failed to add new beverage")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=json.get_error("Cannot override existing item"))
    
    logger.info("Added new beverage successfully")
    return json.get_success(item, "item")

@router.put("/pk/{pk}/sk/{sk}")
async def edit_beverage(pk : str, sk : str,  b : Beverage):
    logger.info(f"Attempting to edit beverage with pk - {pk} and sk - {sk}")
    pk = beverage.arrange_pk(b.beverage_type)
    sk = beverage.arrange_sk(b.base_beverage, b.name)
    item = beverage.arrange_item(b, False)
        
    (
        update_expression, 
        expression_attribute_names, 
        expression_attribute_values
    ) = dynamodb.set_expression_to_edit_beverage(b)
    
    response = dynamodb.edit_beverage(pk, sk, update_expression, expression_attribute_values, expression_attribute_names)
    
    if response[0] != 200:
        logger.info(f"Failed to edit beverage with pk - {pk} and sk - {sk}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=json.get_error(response[1]["message"]) )

    item = beverage.arrange_beverage({"Items" : [ response[1]["item"]["Attributes"] ]})
    logger.info(f"Edited beverage with pk - {pk} and sk - {sk} successfully")

    return json.get_success(item, "item")

@router.delete("/pk/{pk}/sk/{sk}", status_code=status.HTTP_202_ACCEPTED)
async def delete_beverage(pk : str, sk : str):
    logger.info(f"Attempting to delete beverage with pk - {pk} and sk - {sk}")
    response = dynamodb.delete_beverage(pk, sk)    

    if response[0] != 204:
        logger.info(f"Failed to delete beverage with pk - {pk} and sk - {sk}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=json.get_error(response[1]["message"]))
    
    item = beverage.arrange_beverage({"Items" : [response[1]]})
    logger.info(f"Deleted beverage with pk - {pk} and sk - {sk} successfully")

    return json.get_success(item, "item")