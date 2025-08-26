from fastapi import APIRouter, status
from datetime import datetime
import boto3
import logging
from models.beverage import BeverageType, Beverage

router = APIRouter()

dynamodb = boto3.client(
    'dynamodb',
    region_name='us-east-1',          
    aws_access_key_id='jpex1e', 
    aws_secret_access_key='ghzxqt',  
    endpoint_url='http://dynamodb-local:8000'
)

s3 = boto3.client("s3",
    aws_access_key_id="DUMMYIDEXAMPLE",
    aws_secret_access_key="DUMMYEXAMPLEKEY",
    region_name='us-east-1',
    endpoint_url="http://minio:9000"
    )

logger = logging.getLogger("uvicorn.error")  # uvicorn logs

@router.get("/", status_code=status.HTTP_200_OK)
async def get_beverages(beverage : BeverageType | None = None):
    filter = f"CATEGORY#{ "" if beverage == None else str(beverage).split(".")[1] }"
    logger.info(filter)
    response = dynamodb.scan(
        TableName='cocktail-reviewer',
    FilterExpression="begins_with(#pk, :val)",
    ExpressionAttributeNames={
        "#pk": "pk"
    },
    ExpressionAttributeValues={
        ":val": {"S": filter}
    }
    )
    return {
        "message": "Hello World",
        "filter" : filter,
        "beverages": response,
        "beverage_list": beverage, 
        "time" : datetime.now()}

@router.get("/image", status_code=status.HTTP_200_OK)
async def get_image():
    url = s3.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': 'cocktail-api',
                                    'Key': 'cocktail-default-image.jpg',
                                },                                  
                                ExpiresIn=3600)
    return {"url" : url}


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_beverage(id : int):
    return {
        "message": "Hello World", 
        "id" : id, 
        "time" : datetime.now()}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_beverage(beverage : Beverage):
    logger.info("Attempting to insert new beverage")

    pk = f"CATEGORY#{str(beverage.beverage_type).split(".")[1]}"
    sk = f"{str(beverage.base_beverage).split(".")[1] if isinstance(beverage.base_beverage, BeverageType) else beverage.base_beverage}#{beverage.name}"
    dt = datetime.now()

    logger.info(beverage.tags, type(beverage.tags))
    item = {
                'pk': {'S': pk},
                'sk': {'S': sk},
                "tags": {"L": [{"S": tag} for tag in (beverage.tags)]},
                'default_images' : {'L': [{'S' : img} for img in (beverage.default_images) or []]},
                'description': {'S': beverage.description},
                'sum_score': {'N': str(0)},
                'count_score': {'N': str(0)},
                'inserted_at' : {'S' : str(dt)}
            }
    
    if beverage.beverage_type == BeverageType.COCKTAIL and beverage.ingredients != None:
        item["ingredients"] = {
        'L': [
            {
                'M': {
                    'name': {'S': ing["name"]},
                    'quantity': {'N': str(ing["quantity"])},
                    'quantity_type': {'S': ing["quantity_type"]}
                }
            }
            for ing in beverage.ingredients
        ]
    }

    try:
        response = dynamodb.put_item(
            TableName='cocktail-reviewer',
            Item=item
        )
        logger.info("DynamoDB response: %s", response)
    except Exception as e:
        logger.info("Error:", e)
        return {
            "status" : 500,
            "message": e, 
            "time" : dt
            }

    return {
        "status" : 201,
        "message": "Beverage inserted successfully", 
        "PK" : pk,
        "SK" : sk, 
        "time" : dt
        }