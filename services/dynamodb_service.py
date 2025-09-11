import boto3, os
from botocore.exceptions import ClientError
from models.beverage import Beverage
from models.review import Review
from typing import Tuple, Dict, List
from datetime import datetime

__dynamodb = boto3.client(
    "dynamodb",
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    endpoint_url=os.getenv("DYNAMODB_ENDPOINT_URL") 
)

def get_beverages(pk : str = "CATEGORY|") -> Dict:
    """"
    Get the beverages base on the if argumennt pk fits with the beggining of
    the tables primary key.

    Args:
        pk (str) default is value CATEGORY| : condition to check begining of pk in table and
        retrieve those items that match. The default value is the begining of the pk for the items
        that are beverages, thus with it we can retrive all beverages.

    Returns:
        Response to dynamodb
    """
    return __get_items(pk)

def get_beverage(pk : str, sk : str) -> Tuple[int, Dict]:
    """
    Get the beverage based on the if argumennt pk and sk. Only one item can fit condition

    Args:
        pk (str) : condition to check pk in table - should be like CATEGORY|{beverage_type}
        sk (str) : condition to check sk in table - should be like {base_beverage}|{name}

    Returns:
        Response to dynamodb
    """
    return __get_item(pk, sk)

def put_beverage(item : Dict) -> Tuple[int, Dict]:
    """
    Add the new beverage to dynamodb.

    Args:
        item (dict): prepared item to add to dynamodb

    Condition:
        No item must be in dynamodb that match the pk and sk from argument item

    Returns:
        Response from dynamodb
    """
    return __put_item(item)

def edit_beverage(pk : str, sk : str, update_expression : List[str], expression_attribute_values : Dict, expression_attribute_names : Dict)-> Tuple[int, Dict]:
    """"
    Edit beverage to dynamodb.

    Args:
        pk (str) : condition to check pk in table - should be like CATEGORY|{beverage_type}
        sk (str) : condition to check sk in table - should be like {base_beverage}|{name}
        update_expression (list[str]) - expression to update values of fields
        expression_attribute_values (Dict) - values of fields to update
        expression_attribute_names (Dict)- names of the field to update values

    Condition:
        Anitem must be in dynamodb that match the pk and sk from argument item
    
    Note:
        use function set_expression_to_edit_beverage to obtain the attributes update_expression,
        expression_attribute_value and expression_attribute_names

    Returns:
        Response from dynamodb
    """
    return __edit_item(pk, sk, update_expression, expression_attribute_values, expression_attribute_names)

def delete_beverage(pk : str, sk : str) -> Tuple[int, Dict]:
    """
    Delete beverage with sk and pk from dynamodb.

    Args:
        pk (str): primary key
        sk (str): sort key

    Condition:
       An item must be in dynamodb that match the pk and sk from argument item

    Returns:
        Response from dynamodb
    """
    return __delete_item(pk, sk)

def set_expression_to_edit_beverage(b : Beverage) -> Tuple[List, Dict, Dict]:
    """
    Set expressions to edit existing item in dynamodb

    Args
        b (Beverage): beverage item to edit certain attributes

    Returns
        tuple with (update_expression, expression_attribute_names, expression_attribute_values)
    """

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

def get_reviews(pk: str) -> Dict:
    """"
    Get the reviews based on the if argumennt pk fits with the beggining of
    the tables primary key.

    Args
        pk (str) : condition to check begining of pk in table and retrieve those items that match. 
        An item that is a review follows the pattern base_beverage|name, for exemple a cocktail based in 
        GIN named Gin Fizz will have the pk GIN|Gin Fizz

    Returns
        Response to dynamodb
    """
    return  __get_items(pk)

def get_review(pk: str, sk : str) -> Tuple[int, Dict]:
    """
    Get the review based on the if argumennt pk and sk. Only one item can fit condition

    Args:
        pk (str) : condition to check pk in table - should be like {base_beverage}|{name}
        sk (str) : condition to check sk in table- should be like REVIEW|{inserted_at}

    Returns:
        Response to dynamodb
    """
    return __get_item(pk, sk)

def put_review(item : Dict) -> Tuple[int, Dict]:
    """
    Add the new review to dynamodb.

    Args:
        item (dict): prepared item to add to dynamodb

    Condition:
        No item must be in dynamodb that match the pk and sk from argument item

    Returns:
        Response from dynamodb
    """
    return __put_item(item)

def edit_review(pk : str, sk : str, update_expression : List[str], expression_attribute_values : Dict, expression_attribute_names : Dict) -> Tuple[int, Dict]:
    """
    Edit review to dynamodb.

    Args:
        pk (str) : condition to check pk in table - should be like {base_beverage}|{name}
        sk (str) : condition to check sk in table- should be like REVIEW|{inserted_at}
        update_expression (list[str]) - expression to update values of fields
        expression_attribute_values (Dict) - values of fields to update
        expression_attribute_names (Dict)- names of the field to update values

    Condition:
        Anitem must be in dynamodb that match the pk and sk from argument item
    
    Note:
        use function set_expression_to_edit_review to obtain the attributes update_expression,
        expression_attribute_value and expression_attribute_names

    Condition:
        An item must be in dynamodb that match the pk and sk from argument item

    Returns
        Response from dynamodb
    """
    return __edit_item(pk, sk, update_expression, expression_attribute_values, expression_attribute_names)

def delete_review(pk : str, sk : str) -> Tuple[int, Dict]:
    """
    Delete review with sk and pk from dynamodb.

    Args:
        pk (str) : condition to check pk in table - should be like {base_beverage}|{name}
        sk (str) : condition to check sk in table- should be like REVIEW|{inserted_at}

    Condition:
       An item must be in dynamodb that match the pk and sk from argument item

    Returns:
        Response from dynamodb
    """
    return __delete_item(pk, sk)

def set_expression_to_edit_review(r : Review) -> Tuple[List, Dict, Dict]:
    """
    Set expressions to edit existing item in dynamodb

    Args
        r (Review): review item to edit certain attributes

    Note:
        the only attributes that are to be updated are description, score and updated_at
    Returns
        tuple with (update_expression, expression_attribute_names, expression_attribute_values)
    """
    update_expression = []
    expression_attribute_values = {}
    expression_attribute_names = {}

    update_expression.append("#desc = :desc")
    expression_attribute_values[":desc"] = {"S": r.description}
    expression_attribute_names["#desc"] = "description"
    
    update_expression.append("#score = :score")
    expression_attribute_values[":score"] = {"N": str(r.score)}
    expression_attribute_names["#score"] = "score"

    update_expression.append("#updated_at = :dt")
    expression_attribute_values[":dt"] = {"S": str(datetime.now())}
    expression_attribute_names["#updated_at"] = "updated_at"

    return update_expression, expression_attribute_values, expression_attribute_names

def __get_items(pk : str) -> Dict:
    """"
    Get the items based on the if argumennt pk fits with the beggining of
    the tables primary key.

    Args:
        pk (str) : condition to check begining of pk in table and retrieve those items that match. 

    Returns:
        Response to dynamodb
    """
    response = __dynamodb.scan(
        TableName=os.getenv("DB"),
        FilterExpression="begins_with(#pk, :val)",
        ExpressionAttributeNames={
            "#pk": "pk"
        },
        ExpressionAttributeValues={
            ":val": {"S": pk}
        }
    )
    return response

def __get_item(pk: str, sk : str) -> Tuple[int, Dict]:
    """
    Get the item based on the if argumennt checks pk and sk. Only one item can fit condition

    Args:
        pk (str) : condition to check pk in table 
        sk (str) : condition to check sk in table

    Returns:
        Response to dynamodb
    """
    response : Dict = __dynamodb.scan(
        TableName=os.getenv("DB"),
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
        return (404, {"message" : "Error: Not possible to find beverage with given pk and sk"})
    
    return (200, response)

def __put_item(item : Dict) -> Tuple[int, Dict]:
    """
    Add the new item to dynamodb.

    Args:
        item (dict): prepared item to add to dynamodb

    Condition:
        No item must be in dynamodb that match the pk and sk from argument item

    Returns:
        Response from dynamodb
    """
    try:
        response = __dynamodb.put_item(
            TableName=os.getenv("DB"),
            Item=item,
            ConditionExpression="attribute_not_exists(pk) AND attribute_not_exists(sk)"
        )

    except Exception as e:
        return (500, {"message": e})

    return (201, {"item": response })

def __edit_item(pk : str, sk : str, update_expression, expression_attribute_values, expression_attribute_names) -> Tuple[int, Dict]:
    """
    Edit any item to dynamodb.

    Args:
        item (dict): prepared item to edit to dynamodb

    Condition:
        An item must be in dynamodb that match the pk and sk from argument item

    Returns:
        Response from dynamodb
    """
    try:
        response = __dynamodb.update_item(
            TableName=os.getenv("DB"),
            Key={"pk": {"S": pk}, "sk": {"S": sk}},
            UpdateExpression="SET " + ", ".join(update_expression),
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names,
            ConditionExpression="attribute_exists(pk) AND attribute_exists(sk)", 
            ReturnValues="ALL_NEW" 
        )

    except ClientError as e:
        return (409, {"message" : "Item not found to update. Aborted."})
    
    return (200, {"item": response})

def __delete_item(pk : str, sk : str) -> Tuple[int, Dict]:
    """
    Delete item with sk and pk from dynamodb.

    Args:
        pk (str): primary key
        sk (str): sort key

    Condition:
       An item must be in dynamodb that match the pk and sk from argument item

    Returns:
        Response from dynamodb
    """
    response = __dynamodb.delete_item(
        TableName=os.getenv("DB"),
        Key={
            "pk": {"S": pk},
            "sk": {"S": sk}
        },
        ReturnValues="ALL_OLD"
    )

    if not "Attributes" in response:
        return (404, {"message" : "Item not found to delete"})
    
    return (204, response["Attributes"])