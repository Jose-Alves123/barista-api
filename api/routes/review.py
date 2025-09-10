from fastapi import APIRouter, status, Form, File, UploadFile, HTTPException
from models.review import Review
from services import s3, dynamodb, review, json
from datetime import datetime
from typing import Dict
import logging

router = APIRouter()

logger = logging.getLogger("uvicorn.error")  # uvicorn logs

@router.get("/pk/{pk}", status_code=status.HTTP_200_OK)
async def get_reviews_from_beverage(pk : str = "") -> Dict:
    response = dynamodb.get_reviews(pk)

    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred when trying to fetch the data")
    

    items = review.arrange_list_of_reviews(response)
    return json.get_beverage(items, "items")


@router.get("/pk/{pk}/sk{sk}", status_code=status.HTTP_200_OK)
async def get_review_from_beverage(pk : str, sk : str) -> Dict:
    response = dynamodb.get_review(pk, sk)

    if response[0] == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response[1]["message"])

    if response[0] != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred when trying to fetch the data")
    

    items = review.arrange_review(response[1])
    
    return json.get_beverage(items, "item")

@router.post("/", status_code=status.HTTP_200_OK)
async def add_review_from_beverage(file: UploadFile, pk: str = Form(...), description: str = Form(...), score: int = Form(...)) -> Dict:
    logger.info("Start adding")

    try:
        r = Review(pk=pk, description=description, score=score, filename = file.filename or "")
    except Exception as e:
        logger.info(e)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Please validate your data")
    
    obj_name = f"REVIEW|{datetime.now()}.{r.filename.split(".")[1]}"
    r.filename = obj_name
    response = s3.upload_image(file, 'cocktail-api', obj_name)

    if response != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred, please validate the data sent is correct.")

    item = review.arrange_item(r)
    logger.info(item)
    response = dynamodb.put_review(item)

    logger.info(response)

    return {"response" : response}

@router.put("/pk/{pk}/sk/{sk}", status_code=status.HTTP_200_OK)
def edit_review(pk : str, sk : str, file: UploadFile, description: str = Form(...), score: int = Form(...)):

    try:
        r = Review(pk=pk, description=description, score=score, filename = file.filename or "")
    except Exception as e:
        logger.info(e)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Please validate your data")
    
    response = dynamodb.get_review(pk, sk)

    if response[0] == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response[1]["message"])

    if response[0] != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred when trying to fetch the data")
    
    obj_name: str = response[1]["Items"][0]["image"]["S"]
    s3.delete_image(obj_name, "cocktail-api")

    r.filename = obj_name
    response = s3.upload_image(file, 'cocktail-api', obj_name)

    if response != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred, please validate the data sent is correct.")


    (
        update_expression,
        expression_attribute_values,
        expression_attribute_names
    ) = dynamodb.set_expression_to_edit_review(r)

    response = dynamodb.edit_review(pk, sk, update_expression, expression_attribute_values, expression_attribute_names)

    return {"response" : response}


@router.delete("/pk/{pk}/sk/{sk}", status_code=status.HTTP_200_OK)
def delete_review(pk : str, sk : str) -> Dict:
    response = dynamodb.get_review(pk, sk)

    if response[0] == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response[1]["message"])

    if response[0] != 200:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred when trying to fetch the data")
    
    filename : str = response[1]["Items"][0]["image"]["S"]
    s3.delete_image(filename, "cocktail-api")

    pk, sk = response[1]["Items"][0]["pk"]["S"], response[1]["Items"][0]["sk"]["S"]

    response = dynamodb.delete_review(pk, sk)
    if response[0] != 204:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response[1])
    
    return {
        "item" : response[1]
        }