from fastapi.testclient import TestClient
from services.beverages_service import arrange_pk, arrange_sk, arrange_item, arrange_beverage, arrange_list_of_beverages
from models.beverage import BeverageType, Beverage
from main import app
from datetime import datetime

client = TestClient(app)

def test_arrange_pk():
    assert arrange_pk(BeverageType.COCKTAIL) == "CATEGORY|COCKTAIL"
    assert arrange_pk(BeverageType.GIN) == "CATEGORY|GIN"
    assert arrange_pk(BeverageType.WINE) == "CATEGORY|WINE"
    assert arrange_pk(BeverageType.BEER) == "CATEGORY|BEER"
    assert arrange_pk(BeverageType.VODKA) == "CATEGORY|VODKA"


def test_arrange_sk():
    assert arrange_sk(BeverageType.GIN, "Gugugaga") == "GIN|Gugugaga"
    assert arrange_sk(BeverageType.VODKA, "Yeyyeyyuu") == "VODKA|Yeyyeyyuu"
    assert arrange_sk("Pinot Nero", "Toscana") == "Pinot Nero|Toscana"

def test_arrange_item():

    b = Beverage(
        name="Cool drink", 
        description="description of cool drink",
        beverage_type=BeverageType.COCKTAIL,
        base_beverage=BeverageType.GIN,
        ingredients= [
            {
            "name": "ingredient 1",
            "quantity": 0.5,
            "quantity_type": "oz"
            },
            {
            "name": "ingredient 2",
            "quantity": 2,
            "quantity_type": "cups"
            }
        ],
        tags=["cool", "drink"]
        )
    
    item = arrange_item(b)

    assert item["count_score"] == {'N': '0'}
    assert item["sum_score"] == {'N': '0'}
    assert item["default_image"] == {'S': ''}
    assert item["ingredients"] == {
        'L': [
             {
                 'M': {
                     'name': {
                         'S': 'ingredient 1',
                     },
                     'quantity': {
                         'N': '0.5',
                     },
                     'quantity_type': {
                         'S': 'oz',
                     },
                 },
            },
            {
                 'M': {
                     'name': {
                         'S': 'ingredient 2',
                     },
                     'quantity': {
                         'N': '2',
                     },
                     'quantity_type': {
                         'S': 'cups',
                     },
                },
            },
        ],
    }
    assert item["tags"] == { 'L': [ { 'S': 'cool',}, {'S': 'drink', },],}
    assert item["pk"] == {'S': "CATEGORY|COCKTAIL"}
    assert item["sk"] == {'S': f"GIN|{b.name}"}
    assert item["inserted_at"] == item["updated_at"] 

def test_arrange_beverage():
    time = datetime.now()
    item = {
        "pk" : {'S': "CATEGORY|COCKTAIL"},
        "sk" :  {'S': "GIN|Average Drink"},
        "description" : {'S': "The best Average Drink in the World"},
        "default_image" : {'S': ""},
        "inserted_at" : {'S': str(time)},
        "updated_at" : {'S': str(time)},
        "ingredients" : {
            'L': [
                {
                    'M': {
                        'name': {
                            'S': 'ingredient 1',
                        },
                        'quantity': {
                            'N': '0.5',
                        },
                        'quantity_type': {
                            'S': 'oz',
                        },
                    },
                },
                {
                    'M': {
                        'name': {
                            'S': 'ingredient 2',
                        },
                        'quantity': {
                            'N': '2',
                        },
                        'quantity_type': {
                            'S': 'cups',
                        },
                    },
                },
            ],
        },
        "tags" : { 'L': [ { 'S': 'Average',}, {'S': 'Drink', },],},
        "sum_score" : {'N': '0'},
        "count_score" : {'N': '0'}
    }
    response = {
        "Items" : [item]
    }
    b = arrange_beverage(response)
    
    assert b["name"] == "Average Drink"
    assert b["description"] == "The best Average Drink in the World"
    assert b["inserted_at"] == str(time)
    assert b["updated_at"] == str(time)
    assert b["ingredients"] == [
        {
            "name": "ingredient 1",
            "quantity": str(0.5),
            "quantity_type": "oz"
        },
        {
            "name": "ingredient 2",
            "quantity": str(2),
            "quantity_type": "cups"
        }
    ]
    assert b["tags"] == ['Average', 'Drink']

def test_arrange_list_of_beverages():
    time = datetime.now()
    item1 = {
        "pk" : {'S': "CATEGORY|COCKTAIL"},
        "sk" :  {'S': "GIN|Average Drink"},
        "description" : {'S': "The best Average Drink in the World"},
        "default_image" : {'S': ""},
        "inserted_at" : {'S': str(time)},
        "updated_at" : {'S': str(time)},
        "ingredients" : {
            'L': [
                {
                    'M': {
                        'name': {
                            'S': 'ingredient 1',
                        },
                        'quantity': {
                            'N': '0.5',
                        },
                        'quantity_type': {
                            'S': 'oz',
                        },
                    },
                },
                {
                    'M': {
                        'name': {
                            'S': 'ingredient 2',
                        },
                        'quantity': {
                            'N': '2',
                        },
                        'quantity_type': {
                            'S': 'cups',
                        },
                    },
                },
            ],
        },
        "tags" : { 'L': [ { 'S': 'Average',}, {'S': 'Drink', },],},
        "sum_score" : {'N': '0'},
        "count_score" : {'N': '0'}
    }

    item2 = {
        "pk" : {'S': "CATEGORY|COCKTAIL"},
        "sk" :  {'S': "VODKA|Great Drink"},
        "description" : {'S': "The best Great Drink in the World"},
        "default_image" : {'S': ""},
        "inserted_at" : {'S': str(time)},
        "updated_at" : {'S': str(time)},
        "ingredients" : {
            'L': [
                {
                    'M': {
                        'name': {
                            'S': 'ingredient 1',
                        },
                        'quantity': {
                            'N': '0.5',
                        },
                        'quantity_type': {
                            'S': 'oz',
                        },
                    },
                },
                {
                    'M': {
                        'name': {
                            'S': 'ingredient 2',
                        },
                        'quantity': {
                            'N': '2',
                        },
                        'quantity_type': {
                            'S': 'cups',
                        },
                    },
                },
            ],
        },
        "tags" : { 'L': [ { 'S': 'Great',}, {'S': 'Drink', },],},
        "sum_score" : {'N': '0'},
        "count_score" : {'N': '0'}
    }
    
    item3 = {
        "pk" : {'S': "CATEGORY|VODKA"},
        "sk" :  {'S': "Ahmeh|Meh Drink"},
        "description" : {'S': "The best Meh Drink in the World"},
        "default_image" : {'S': ""},
        "inserted_at" : {'S': str(time)},
        "updated_at" : {'S': str(time)},
        "tags" : { 'L': [ { 'S': 'Meh',}, {'S': 'Drink', },],},
        "sum_score" : {'N': '0'},
        "count_score" : {'N': '0'}
    }

    response = {
        "Items" : [item1, item2, item3]
    }

    b = arrange_list_of_beverages(response)

    assert b[0]["name"] == "Average Drink"
    assert b[0]["beverage_type"] == "COCKTAIL"
    assert b[0]["base_beverage"] == "GIN"
    assert b[0]["description"] == "The best Average Drink in the World"
    assert b[0]["inserted_at"] == str(time)
    assert b[0]["updated_at"] == str(time)
    assert b[0]["ingredients"] == [
        {
            "name": "ingredient 1",
            "quantity": str(0.5),
            "quantity_type": "oz"
        },
        {
            "name": "ingredient 2",
            "quantity": str(2),
            "quantity_type": "cups"
        }
    ]
    assert b[0]["tags"] == ['Average', 'Drink']

    assert b[1]["name"] == "Great Drink"
    assert b[1]["beverage_type"] == "COCKTAIL"
    assert b[1]["base_beverage"] == "VODKA"
    assert b[1]["description"] == "The best Great Drink in the World"
    assert b[1]["inserted_at"] == str(time)
    assert b[1]["updated_at"] == str(time)
    assert b[1]["ingredients"] == [
        {
            "name": "ingredient 1",
            "quantity": str(0.5),
            "quantity_type": "oz"
        },
        {
            "name": "ingredient 2",
            "quantity": str(2),
            "quantity_type": "cups"
        }
    ]
    assert b[1]["tags"] == ['Great', 'Drink']

    assert b[2]["name"] == "Meh Drink"
    assert b[2]["beverage_type"] == "VODKA"
    assert b[2]["base_beverage"] == "Ahmeh"
    assert b[2]["description"] == "The best Meh Drink in the World"
    assert b[2]["inserted_at"] == str(time)
    assert b[2]["updated_at"] == str(time)
    assert b[2]["tags"] == ['Meh', 'Drink']