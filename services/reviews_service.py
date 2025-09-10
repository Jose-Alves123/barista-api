from models.review import Review
from services import s3
from typing import Dict, List

def arrange_item(review: Review, method_post : bool = True) -> Dict:
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
    items = []
    
    for i in  range(len(response["Items"])):
        item = __arrange_review(response["Items"][i])
        item["image"] = s3.get_image(item["image"])
        items.append(item)
        
    return items

def arrange_review(response: Dict) -> Dict:
    item = __arrange_review(response["Items"][0])
    item["image"] = s3.get_image(item["image"])
    
    return item

def __arrange_review(item : Dict) -> Dict:

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




