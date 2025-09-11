from fastapi import APIRouter, status, Form, File, UploadFile, HTTPException
from models.review import Review
from services import s3, dynamodb, review, json
from datetime import datetime
from typing import Dict
import logging

router = APIRouter()

logger = logging.getLogger("uvicorn.error")  # uvicorn logs

@router.get("/pk/{pk}", status_code=status.HTTP_200_OK)
async def get_reviews(pk : str = "") -> Dict:
    logger.info("Attempting to obtain list of reviews")
    response = dynamodb.get_reviews(pk)

    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        logger.info("Failed to obtain list of reviews")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=json.get_error("An error occurred when trying to fetch the data"))
    
    items = review.arrange_list_of_reviews(response)
    logger.info("Obtained list of reviews successfully")

    return json.get_success(items, "items")

@router.get("/pk/{pk}/sk{sk}", status_code=status.HTTP_200_OK)
async def get_review(pk : str, sk : str) -> Dict:
    logger.info(f"Attempting to obtain review with pk - {pk} and sk - {sk}")
    response = dynamodb.get_review(pk, sk)

    if response[0] == 404:
        logger.info(f"Failed to obtain review with pk - {pk} and sk - {sk} - not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=json.get_error(response[1]["message"]))

    if response[0] != 200:
        logger.info(f"Failed to obtain review with pk - {pk} and sk - {sk} - boto3 error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=json.get_error("An error occurred when trying to fetch the data."))
    
    items = review.arrange_review(response[1])
    logger.info(f"Obtained review with pk - {pk} and sk - {sk} successfully")
    
    return json.get_success(items, "item")

@router.post("/", status_code=status.HTTP_200_OK)
async def add_review(file: UploadFile, pk: str = Form(...), description: str = Form(...), score: int = Form(...)) -> Dict:
    logger.info("Attempting to start adding new review.")

    try:
        r = Review(pk=pk, description=description, score=score, filename = file.filename or "")
    except Exception as e:
        logger.info("Error validating data for Review class")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=json.get_error("Please validate your data."))
    
    obj_name = f"REVIEW|{datetime.now()}.{r.filename.split(".")[1]}"
    r.filename = obj_name
    response = s3.upload_image(file, obj_name)

    if response != 200:
        logger.info("Failed to add image to S3.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=json.get_error("An internal error occurred, please validate the data sent is correct."))

    item = review.arrange_item(r)
    response = dynamodb.put_review(item)

    if response[0] != 200:
        logger.info("Failed to add new review to DynamoDB - image was added S3.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=json.get_error("An internal error occurred, please validate the data sent is correct."))

    logger.info("Added new review successfully.")

    return json.get_success(response[1], "item")

@router.put("/pk/{pk}/sk/{sk}", status_code=status.HTTP_200_OK)
def edit_review(pk : str, sk : str, file: UploadFile, description: str = Form(...), score: int = Form(...)) -> Dict:
    logger.info(f"Attempting to edit review with pk - {pk} and sk - {sk}")
    try:
        r = Review(pk=pk, description=description, score=score, filename = file.filename or "")
    except Exception as e:
        logger.info(f"Error validating data to edit review. Aborted.")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=json.get_error("Please validate your data"))
    
    response = dynamodb.get_review(pk, sk)

    if response[0] == 404:
        logger.info(f"Failed to edit review with pk - {pk} and sk - {sk} - Review not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=json.get_error(response[1]["message"]))

    if response[0] != 200:
        logger.info(f"Failed to edit review with pk - {pk} and sk - {sk} - boto3 error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=json.get_error("An error occurred when trying to fetch the data"))
    
    obj_name: str = response[1]["Items"][0]["image"]["S"]
    s3.delete_image(obj_name)

    r.filename = obj_name
    response = s3.upload_image(file, obj_name)

    if response != 200:
        logger.info(f"Failed to upload image for review with with pk - {pk} and sk - {sk}.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=json.get_error("An internal error occurred, please validate the data sent is correct."))

    (
        update_expression,
        expression_attribute_values,
        expression_attribute_names
    ) = dynamodb.set_expression_to_edit_review(r)

    response = dynamodb.edit_review(pk, sk, update_expression, expression_attribute_values, expression_attribute_names)

    if response[0] != 200:
        logger.info(f"Failed to edit review with pl - {pk} and sk - {sk}.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response[1]["message"])

    logger.info(f"Edited review with successfully")

    return json.get_success(response[1], "item")

@router.delete("/pk/{pk}/sk/{sk}", status_code=status.HTTP_200_OK)
def delete_review(pk : str, sk : str) -> Dict:
    logger.info(f"Attempting to delete review with pk - {pk} and sk - {sk}")
    response = dynamodb.get_review(pk, sk)

    if response[0] == 404:
        logger.info(f"Failed to delete review with pk - {pk} and sk - {sk} - review not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response[1]["message"])

    if response[0] != 200:
        logger.info(f"Failed to delete review with pk - {pk} and sk - {sk} - boto3 error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=json.get_error("An error occurred when trying to fetch the data"))
    
    filename : str = response[1]["Items"][0]["image"]["S"]
    s3.delete_image(filename)

    pk, sk = response[1]["Items"][0]["pk"]["S"], response[1]["Items"][0]["sk"]["S"]

    response = dynamodb.delete_review(pk, sk)
    if response[0] != 204:
        logger.info(f"Failed to delete review with pk - {pk} and sk - {sk}.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response[1])
    
    return json.get_success(response[1], "item")