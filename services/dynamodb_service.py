import boto3
from botocore.exceptions import ClientError
from models.beverage import Beverage
from typing import Tuple, Dict
from datetime import datetime


__dynamodb = boto3.client(
    'dynamodb',
    region_name='us-east-1',          
    aws_access_key_id='jpex1e', 
    aws_secret_access_key='ghzxqt',  
    endpoint_url='http://dynamodb-local:8000'
)

def get_beverages(pk : str = ""):
    response = __dynamodb.scan(
        TableName='cocktail-reviewer',
        FilterExpression="begins_with(#pk, :val)",
        ExpressionAttributeNames={
            "#pk": "pk"
        },
        ExpressionAttributeValues={
            ":val": {"S": pk}
        }
    )
    return response

def get_beverage(pk : str, sk : str) -> Tuple[int, Dict]:
    response : Dict = __dynamodb.scan(
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
        return (400, {"message" : "Error: Not possible to find beverage with given pk and sk"})
    
    return (200, response)

def put_beverage(item) -> Tuple[int, Dict]:
    try:
        response = __dynamodb.put_item(
            TableName='cocktail-reviewer',
            Item=item,
            ConditionExpression="attribute_not_exists(pk) AND attribute_not_exists(sk)"
        )

    except Exception as e:
        return (500, {"message": e})

    return (201, {"item": response })

def delete_beverage(pk : str, sk : str) -> Tuple[int, Dict]:
    response = __dynamodb.delete_item(
        TableName='cocktail-reviewer',
        Key={
            "pk": {"S": pk},
            "sk": {"S": sk}
        },
        ReturnValues="ALL_OLD"
    )

    if not "Attributes" in response:
        return (404, {"message" : "Item not found to delete"})
    
    return (204, response["Attributes"])


def edit_beverage(pk : str, sk : str, update_expression, expression_attribute_values, expression_attribute_names)-> Tuple[int, Dict]:
    try:
        response = __dynamodb.update_item(
            TableName="cocktail-reviewer",
            Key={"pk": {"S": pk}, "sk": {"S": sk}},
            UpdateExpression="SET " + ", ".join(update_expression),
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names,
            ConditionExpression="attribute_exists(pk) AND attribute_exists(sk)", 
            ReturnValues="ALL_NEW" 
        )

    except ClientError as e:
        return (404, {"message" : "Item not found to update. Aborted."})
    
    return (200, {"beverage": response})

def set_expression_to_edit_beverage(b : Beverage):
    update_expression = []
    expression_attribute_values = {}
    expression_attribute_names = {}

    if b.description:
        update_expression.append("#desc = :desc")
        expression_attribute_values[":desc"] = {"S": b.description}
        expression_attribute_names["#desc"] = "description"

    if b.tags:
        update_expression.append("#tags = :tags")
        expression_attribute_values[":tags"] = {
            "L": [{"S": tag} for tag in b.tags]
        }
        expression_attribute_names["#tags"] = "tags"


    if b.ingredients:
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
                for ing in b.ingredients
            ]
        }
        expression_attribute_names["#ingredients"] = "ingredients"

    update_expression.append("#updated_at = :dt")
    expression_attribute_values[":dt"] = {"S": str(datetime.now())}
    expression_attribute_names["#updated_at"] = "updated_at"
    return (update_expression, expression_attribute_names, expression_attribute_values)