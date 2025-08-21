from fastapi import FastAPI
from enum import Enum
from datetime import datetime
from pydantic import BaseModel
import boto3
from boto3.dynamodb.conditions import Key, Attr, BeginsWith
import logging

logger = logging.getLogger("uvicorn.error")  # uvicorn logs

dynamodb = boto3.client(
    'dynamodb',
    region_name='us-east-1',          
    aws_access_key_id='jpex1e', 
    aws_secret_access_key='ghzxqt',  
    endpoint_url='http://dynamodb-local:8000'
)

app = FastAPI()

class BeverageType(int, Enum):
    COCKTAIL = 1
    GIN = 2
    BEER = 3
    WINE = 4
    VODKA = 5

    @classmethod
    def _missing_(cls, value):
        return BeverageType.COCKTAIL
    
    def __str__(self) -> str:
        return super().__str__()

class Beverage(BaseModel):
    name : str
    description: str | None = ""
    beverage_type: BeverageType
    base_beverage: BeverageType | None
    ingredients : list[dict] | None
    tags: list[str] | None = []
    default_images : list[str] | None = []
    sum_score : int
    count_score : int

@app.get("/beverages")
async def get_beverages(beverage : BeverageType = BeverageType.COCKTAIL):

    filter = f"CATEGORY#{str(beverage).split(".")[1]}"
    logger.info(f"CATEGORY#{str(beverage).split(".")[1]}")
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


@app.get("/beverages/{id}")
async def get_beverage(id : int):
    beverage_list : list[str] = [e.name for e in BeverageType]
    return {
        "message": "Hello World", 
        "id" : id, 
        "bv_list" : beverage_list, 
        "time" : datetime.now()}


## TODO validation of input
@app.post("/beverages")
async def add_beverage(beverage : Beverage):
    logger.info("Attempting to insert new beverage")

    pk = f"CATEGORY#{str(beverage.beverage_type).split(".")[1]}"
    sk = f"{str(beverage.base_beverage).split(".")[1]}#{beverage.name}"
    dt = datetime.now()

    try:
        response = dynamodb.put_item(
            TableName='cocktail-reviewer',
            Item={
                'pk': {'S': pk},
                'sk': {'S': sk},
                'tags': {'L' : beverage.tags},
                'default_images' : {'L' : beverage.default_images},
                'description': {'S': beverage.description},
                'sum_score': {'N': str(0)},
                'count_score': {'N': str(0)},
                'inserted_at' : {'S' : str(dt)}
            }
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