from models.beverage import BeverageType, Beverage
from services import s3
from typing import Dict, List
from datetime import datetime

def arrange_pk(beverage : BeverageType | None = None) -> str:
    """
    Creates a string based pk. A PK is set the the join of the
    beverage type with a prefix CATEGORY|
    
    Args:
        beverage (BeverageType): The beverage type of the item.

    Returns:
        str: The result of the joining between CAETGORY | and the beverage type

    Examples:

       beverage -> BeverageType.COCKTAIL returns string CATEGORY|COCKTAIL

       beverage -> BeverageType.VODKA returns string CATEGORY|VODKA
    """

    return  f"CATEGORY|{ "" if beverage == None else str(beverage).split(".")[1] }"

def arrange_sk(b_type : BeverageType | str, b_name : str) -> str:
    """
    Creates a string based sk. A SK is set the the join of the
    base_beverage with the name of the beverage
    
    Args:
        b_type (BeverageType): The base beverage type of the item.
        b_name (str): The name of the beverage

    Returns:
        str: The result of the joining between base_beverage | and the beverage name

    Examples:

       b_type -> BeverageType.VODKA and b_name -> Russian Vodka returns string VODKA|Russian Vodka

       b_type -> Pinot Nero and b_name -> Toscana returns string Pinot Nero|Toscana
    """

    return f"{str(b_type).split(".")[1] if isinstance(b_type, BeverageType) else b_type}|{b_name}"

def arrange_list_of_beverages(response) -> List[Dict]:
    """"
    Creates a json based dictionary listing all the important attributes from the beverage.
    
    Args:
        response: a dictionary containing an atributte Items that is a list of items.
        An item could contain the following attributes
        - pk : response["Items"][i][pk][S]
        - sk : response["Items"][i][sk][S]
        - description : response["Items"][i]["description"]["S"],
        - name : response["Items"][i][name][S],
        - inserted_at : response["Items"][i]["inserted_at"]["S"],
        - updated_at : response["Items"][i]["updated_at"]["S"],
        - tags : response["Items"][i][tags][L],
            - tag : tags[i][S]
        - default_image : response["Items"][i]["default_image"]["S"],
        - sum_score : int(response["Items"][i]["sum_score"]["N"]),
        - count_score : int(response["Items"][i]["count_score"]["N"]),
        - ingredients : response["Items"][i]["ingredients"]["L"]
            - name : ingredient["M"]["name"]["S"],
            - quantity" : ingredient["M"]["quantity"]["N"],
            - quantity_type : ingredient["M"]["quantity_type"]["S"] 

    All the items will be transformed.
            
    Returns:
        dict: The result of the response Dict transformation.

    """
    items = []
    default_url = None
    
    for i in  range(len(response["Items"])):
        item = __arrange_beverage(response["Items"][i])
        
        if item["default_image"] == "":
            if not default_url:
                default_url = s3.get_image()
            item["default_image"] = default_url
        else:
            item["default_image"] = s3.get_image(item["default_image"])
        items.append(item)
        
    return items

def arrange_beverage(response : Dict) -> Dict:
    """
    Creates a json based dictionary listing all the important attributes from the beverage.
    
    Args:
        response: a dictionary containing an atributte Items that is a list of items.
        An item could contain the following attributes
        - pk : response["Items"][i][pk][S]
        - sk : response["Items"][i][sk][S]
        - description : response["Items"][i]["description"]["S"],
        - name : response["Items"][i][name][S],
        - inserted_at : response["Items"][i]["inserted_at"]["S"],
        - updated_at : response["Items"][i]["updated_at"]["S"],
        - tags : response["Items"][i][tags][L],
            - tag : tags[i][S]
        - default_image : response["Items"][i]["default_image"]["S"],
        - sum_score : int(response["Items"][i]["sum_score"]["N"]),
        - count_score : int(response["Items"][i]["count_score"]["N"]),
        - ingredients : response["Items"][i]["ingredients"]["L"]
            - name : ingredient["M"]["name"]["S"],
            - quantity" : ingredient["M"]["quantity"]["N"],
            - quantity_type : ingredient["M"]["quantity_type"]["S"] 

    Only the first item will be transformed.
            
    Returns:
        dict: The result of the response Dict transformation, ready to input into dynamodb

    """
    item = __arrange_beverage(response["Items"][0])
    
    if item["default_image"] == "":
        item["default_image"] = s3.get_image()
    else:
        item["default_image"] = s3.get_image(item["default_image"])

    return item

def arrange_item(b : Beverage, method_post: bool = True) -> Dict:
    """"
    Creates a json based dictionary to post or put item in dynamodb.

    Args:
        b (Beverage) : the beverage to convert to format to add to dynamodb

        method_post (bool) default = True : the method od the items to add/edit to dynamodb.
            if is of method post attributes such as name, inserted_at, base_beverage and beverage_type
            are included, else are not

    Returns:

    """
    pk = arrange_pk(b.beverage_type)
    sk = arrange_sk(b.base_beverage, b.name)
    dt = datetime.now()

    item = {
                'pk': {'S': pk},
                'sk': {'S': sk},
                "tags": {"L": [{"S": tag} for tag in (b.tags)]},
                'description': {'S': b.description},
                'updated_at' : {'S' : str(dt)}
            }

    if b.beverage_type == BeverageType.COCKTAIL:
        item["ingredients"] = {
            'L': [
                {
                    'M': {
                        'name': {'S': ing["name"]},
                        'quantity': {'N': str(ing["quantity"])},
                        'quantity_type': {'S': ing["quantity_type"]}
                    }
                } 
                for ing in (b.ingredients or [])
            ]
        }

    if method_post:
        item["inserted_at"] = {'S' : str(dt)}
        item["sum_score"] = {'N': str(0)}
        item["count_score"] = {'N': str(0)}
        item["default_image"] = {'S': ""}

    return item

def __arrange_beverage(response : Dict) -> Dict:
    """
    Creates a json based dictionary listing all the important attributes from the beverage.
    
    Args:
        response: a dictionary containing an atributtes to transform.
        An item could contain the following attributes
        - pk : response[pk][S]
        - sk : response[sk][S]
        - description : response["description"]["S"],
        - name : response[name][S],
        - inserted_at : response["inserted_at"]["S"],
        - updated_at : response["updated_at"]["S"],
        - tags : response[tags][L],
            - tag : tags[i][S]
        - default_image : response["default_image"]["S"],
        - sum_score : int(response["sum_score"]["N"]),
        - count_score : int(response["count_score"]["N"]),
        - ingredients : response["ingredients"]["L"]
            - name : ingredient["M"]["name"]["S"],
            - quantity" : ingredient["M"]["quantity"]["N"],
            - quantity_type : ingredient["M"]["quantity_type"]["S"] 

            
    Returns:
        dict: The result of the response Dict transformation.

    """
    beverage_type = response["pk"]["S"].split("|")[1]
    base_beverage = response["sk"]["S"].split("|")[0]
    name = response["sk"]["S"].split("|")[1]
    tags = [ tag["S"] for tag in response["tags"]["L"]]

    item = {
        "beverage_type" : beverage_type,
        "base_beverage" : base_beverage,
        "description" : response["description"]["S"],
        "name" : name,
        "inserted_at" : response["inserted_at"]["S"],
        "updated_at" : response["updated_at"]["S"],
        "tags" : tags,
        "default_image" : response["default_image"]["S"],
        "sum_score" : int(response["sum_score"]["N"]),
        "count_score" : int(response["count_score"]["N"]),
    }

    if "ingredients" in response : 
        item["ingredients"] = [{
                "name" : ingredient["M"]["name"]["S"],
                "quantity" : ingredient["M"]["quantity"]["N"],
                "quantity_type" : ingredient["M"]["quantity_type"]["S"] 
            } for ingredient in response["ingredients"]["L"]
        ]

    return item