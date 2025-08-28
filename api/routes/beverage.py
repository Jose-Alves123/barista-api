from fastapi import APIRouter, status, HTTPException, Form
from typing import Annotated
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
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


@router.get("/pk/{pk}/sk/{sk}", status_code=status.HTTP_200_OK)
async def get_beverage(pk : str, sk : str):

    response = dynamodb.scan(
        TableName='cocktail-reviewer',
    FilterExpression="#pk = :val_pk AND #sk = :val_sk",
    ExpressionAttributeNames={
        "#pk": "pk",
        "#sk": "sk"
    },
    ExpressionAttributeValues={
        ":val_pk": {"S": pk},
        ":val_sk": {"S": sk},
    }
    )
    if response['Count'] != 1:
        return {
            "status": 400,
            "message" : "Error: Not possible to find beverage with given pk and sk"
        }
    
    beverage_type = response["Items"][0]["pk"]["S"].split("#")[1].title()
    base_beverage = response["Items"][0]["sk"]["S"].split("#")[0].title()
    name = response["Items"][0]["sk"]["S"].split("#")[1]
    ingredients = [{
            "name" : ingredient["M"]["name"]["S"],
            "quantity" : ingredient["M"]["quantity"]["N"],
            "quantity_type" : ingredient["M"]["quantity_type"]["S"] 
        } for ingredient in response["Items"][0]["ingredients"]["L"]
    ]

    tags = [ tag["S"] for tag in response["Items"][0]["tags"]["L"]]

    return {
        "message": "Scan complete with success", 
        "item" : {
            "beverage_type" : beverage_type,
            "base_beverage" : base_beverage,
            "name" : name,
            "ingredients" : ingredients,
            "inserted_at" : response["Items"][0]["inserted_at"]["S"],
            "tags" : tags,
            "sum_score" : int(response["Items"][0]["sum_score"]["N"]),
            "count_score" : int(response["Items"][0]["count_score"]["N"]),
        },
        "time" : datetime.now()
        }


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
                'default_image' : {'S': ""},
                'description': {'S': beverage.description},
                'sum_score': {'N': str(0)},
                'count_score': {'N': str(0)},
                'inserted_at' : {'S' : str(dt)},
                'updated_at' : {'S' : str(dt)}
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


# TODO when pk or sk change, must delete previous item and create new one (update then reviews as well)
@router.put("/pk/{pk}/sk/{sk}")
async def edit_beverage(pk : str, sk : str,  beverage : Beverage):

    new_pk = f"CATEGORY#{str(beverage.beverage_type).split(".")[1]}"
    new_sk = f"{str(beverage.base_beverage).split(".")[1] if isinstance(beverage.base_beverage, BeverageType) else beverage.base_beverage}#{beverage.name}"
    dt = datetime.now()

    item = {
                'pk': {'S': new_pk},
                'sk': {'S': new_sk},
                "tags": {"L": [{"S": tag} for tag in (beverage.tags)]},
                'description': {'S': beverage.description},
                'updated_at' : {'S' : str(dt)}
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
        
    update_expression = []
    expression_attribute_values = {}
    expression_attribute_names = {}

    if beverage.description:
        update_expression.append("#desc = :desc")
        expression_attribute_values[":desc"] = {"S": beverage.description}
        expression_attribute_names["#desc"] = "description"

    if beverage.tags:
        update_expression.append("#tags = :tags")
        expression_attribute_values[":tags"] = {
            "L": [{"S": tag} for tag in beverage.tags]
        }
        expression_attribute_names["#tags"] = "tags"


    if beverage.ingredients:
        update_expression.append("#ingredients = :ings")
        expression_attribute_values[":ings"] = {
            "L": [
                {
                    "M": {
                        "name": {"S": ing["name"]},
                        "quantity": {"N": str(ing["quantity"])},
                        "quantity_type": {"S": ing["quantity_type"]},
                    }
                }
                for ing in beverage.ingredients
            ]
        }
        expression_attribute_names["#ingredients"] = "ingredients"

    update_expression.append("#updated_at = :dt")
    expression_attribute_values[":dt"] = {"S": str(dt)}
    expression_attribute_names["#updated_at"] = "updated_at"
        
    try:
        response = dynamodb.update_item(
        TableName="cocktail-reviewer",
        Key={"pk": {"S": new_pk}, "sk": {"S": new_sk}},
        UpdateExpression="SET " + ", ".join(update_expression),
        ExpressionAttributeValues=expression_attribute_values,
        ExpressionAttributeNames=expression_attribute_names,
        ConditionExpression="attribute_exists(pk) AND attribute_exists(sk)", 
        ReturnValues="ALL_NEW" 
    )

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            logger.warning("Item does not exist, cannot update")
        raise HTTPException(status_code=404, detail="Item not found to update. Aborted.")
    
    return {"beverage": response}

@router.delete("/pk/{pk}/sk/{sk}", status_code=status.HTTP_202_ACCEPTED)
async def delete_beverage(pk : str, sk : str):
    response = dynamodb.delete_item(
        TableName='cocktail-reviewer',
        Key={
            "pk": {"S": pk},
            "sk": {"S": sk}
        },
        ReturnValues="ALL_OLD"
    )

    if not "Attributes" in response:
        raise HTTPException(status_code=404, detail="Item not found to delete")
    
    return {
        "status": 204, 
        "message": "Item deleted",
        "item" : response["Attributes"],
        "time": datetime.now()
    }