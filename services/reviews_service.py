from models.review import Review
from services import s3
from typing import Dict, List

def arrange_item(review: Review, method_post : bool = True) -> Dict:
    """
    Creates a json based dictionary to post or put item in dynamodb.

    Args:
        review (Review) : the review to convert to format to add to dynamodb
        method_post (bool) default = True : the method od the items to add/edit to dynamodb.
            if is of method post attributes such as pk, inserted_at and sk are included

    Returns:
        Dict item ready to upload to DynamoDB
    """
    sk = review.filename.split(".")[0]
    date = sk.split("|")[1]
    item : dict = {
                'description': {'S': review.description},
                "updated_at" : {'S' : date},
                "image" : {'S' : review.filename},
                "score" : {'N' : str(review.score)},
            }
    if method_post:
        item["pk"] = {'S': review.pk}
        item["sk"] = {'S': review.filename.split(".")[0]}
        item["inserted_at"] = {'S' : date}
    
    return item

def arrange_list_of_reviews(response : Dict) -> List[Dict]:
    """
    Creates a json based dictionary listing all the important attributes from the review.
    
    Args:
        response: a dictionary containing an atributte Items that is a list of items.
        An item could contain the following attributes
        - pk : response["Items"][i][pk][S]
        - sk : response["Items"][i][sk][S]
        - description : response["Items"][i]["description"]["S"],
        - inserted_at : response["Items"][i]["inserted_at"]["S"],
        - updated_at : response["Items"][i]["updated_at"]["S"],
        - image : response["Items"][i]["image"]["S"],
        - score : int(response["Items"][i]["score"]["N"]),


    Only the first item will be transformed.
            
    Returns:
        dict: The result of the response Dict transformation, ready to input into dynamodb

    """
    items = []
    
    for i in  range(len(response["Items"])):
        item = __arrange_review(response["Items"][i])
        item["image"] = s3.get_image(item["image"])
        items.append(item)
        
    return items

def arrange_review(response: Dict) -> Dict:
    """
    Creates a json based dictionary listing all the important attributes from the review.
    
    Args:
        response: a dictionary containing an atributte Items that is a list of items.
        An item could contain the following attributes
        - pk : response["Items"][i][pk][S]
        - sk : response["Items"][i][sk][S]
        - description : response["Items"][i]["description"]["S"],
        - inserted_at : response["Items"][i]["inserted_at"]["S"],
        - updated_at : response["Items"][i]["updated_at"]["S"],
        - image : response["Items"][i]["image"]["S"],
        - score : int(response["Items"][i]["score"]["N"]),


    Only the first item will be transformed.
            
    Returns:
        dict: The result of the response Dict transformation, ready to input into dynamodb

    """
    item = __arrange_review(response["Items"][0])
    item["image"] = s3.get_image(item["image"])
    
    return item

def __arrange_review(item : Dict) -> Dict:
    """
    Creates a json based dictionary listing all the important attributes from the review.
    
    Args:
        response: a dictionary containing an atributte Items that is a list of items.
        An item could contain the following attributes
        - pk : item[pk][S]
        - sk : item[sk][S]
        - description : item["description"]["S"],
        - inserted_at : item["inserted_at"]["S"],
        - updated_at : item["updated_at"]["S"],
        - image : item["image"]["S"],
        - score : int(item["score"]["N"]),


    Only the first item will be transformed.
            
    Returns:
        dict: The result of the response Dict transformation, ready to input into dynamodb

    """
    item = {
        "pk" : item["pk"]["S"],
        "sk" : item["sk"]["S"], 
        "description" : item["description"]["S"],
        "image" : item["image"]["S"],
        "inserted_at" : item["inserted_at"]["S"],
        "updated_at" : item["updated_at"]["S"],
        "score" : item["score"]["N"]
    }

    return item




