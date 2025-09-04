from fastapi.testclient import TestClient
from services.beverages_service import arrange_pk, arrange_sk
from models.beverage import BeverageType
from main import app
from random import choices
from string import ascii_letters

client = TestClient(app)

def test_get_beverages():
    response = client.get("/beverages")
    assert response.status_code == 200

def test_get_beverage_status_404():
    pk="PKTHATDOESNTEXIST"
    sk="SKTHATDOESNTEXIST"

    response = client.get(f"/beverages/pk/{pk}/sk/{sk}")
    assert response.status_code == 404

def test_create_beverage_cocktail_success():
    name = "".join(choices(ascii_letters, k=10))
    item = {
        "name" : name,
        "base_beverage" : 2, # GIN
        "beverage_type" : 1, # COCKTAIL
        "ingredients": [
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
        "description" : f"The best {name} in the world!",
        "tags": [
            "hello",
            "world"
        ]
    }

    response = client.post(url="/beverages", json=item)
    assert response.status_code == 201

    pk = arrange_pk(BeverageType.COCKTAIL)
    sk = arrange_sk(BeverageType.GIN, name)

    client.delete(f"/beverages/pk/{pk}/sk/{sk}")

def test_create_beverage_cocktail_without_ingredients_fail():
    name = "".join(choices(ascii_letters, k=10))
    item = {
        "name" : name,
        "base_beverage" : 2, # GIN
        "beverage_type" : 1, # COCKTAIL
        "description" : f"The best {name} in the world!",
        "tags": [
            "hello",
            "world"
        ]
    }

    response = client.post(url="/beverages", json=item)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Value error, Cocktails must have at least two ingredients"

def test_create_beverage_cocktail_with_base_beverage_cocktail_fail():
    name = "".join(choices(ascii_letters, k=10))
    item = {
        "name" : name,
        "base_beverage" : 1, # COCKTAIL
        "beverage_type" : 1, # COCKTAIL
        "ingredients": [
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
        "description" : f"The best {name} in the world!",
        "tags": [
            "hello",
            "world"
        ]
    }

    response = client.post(url="/beverages", json=item)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Value error, A cocktail must not have a base beverage of type Cocktail"

def test_create_non_cocktail_beverage_with_ingredients_fail():
    name = "".join(choices(ascii_letters, k=10))
    item = {
        "name" : name,
        "base_beverage" : "Dry Gin",
        "beverage_type" : 2, # GIN
        "ingredients": [
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
        "description" : f"The best {name} in the world!",
        "tags": [
            "hello",
            "world"
        ]
    }

    response = client.post(url="/beverages", json=item)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Value error, Non-cocktail beverages cannot have ingredients"

def test_create_non_cocktail_beverage_with_invalid_base_beverage_fail():
    name = "".join(choices(ascii_letters, k=10))
    item = {
        "name" : name,
        "base_beverage" : "", # Must have at least 1 character long
        "beverage_type" : 2, # GIN
        "description" : f"The best {name} in the world!",
        "tags": [
            "hello",
            "world"
        ]
    }

    response = client.post(url="/beverages", json=item)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Value error, Please provide the subclass of the beverage"

def test_create_beverage_with_invalid_description_fail():
    name = "".join(choices(ascii_letters, k=10))
    item = {
        "name" : name,
        "base_beverage" : 2, # GIN
        "beverage_type" : 1, # COCKTAIL
        "ingredients": [
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
        "description" : f"Invalid", # Description must be between 10 and 500 characters long
        "tags": [
            "hello",
            "world"
        ]
    }

    response = client.post(url="/beverages", json=item)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Value error, Description field must have between 10 and 500 characters"

def test_create_beverage_with_invalid_tags_fail():
    name = "".join(choices(ascii_letters, k=10))
    item = {
        "name" : name,
        "base_beverage" : 2, # GIN
        "beverage_type" : 1, # COCKTAIL
        "ingredients": [
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
        "description" : f"The best {name} in the world!",
        "tags": [
            "hello",
            "hello"
        ] # Must not repeat tags, tags can be however None or empty list
    }

    response = client.post(url="/beverages", json=item)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Value error, Must not repeat values in tags"

def test_edit_cocktail_beverage_success():
    name = "".join(choices(ascii_letters, k=10))
    item = {
        "name" : name,
        "base_beverage" : 2, # GIN
        "beverage_type" : 1, # COCKTAIL
        "ingredients": [
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
        "description" : f"The best {name} in the world!",
        "tags": [
            "hello",
            "world"
        ]
    }

    response = client.post(url="/beverages", json=item)
    assert response.status_code == 201
    
    update_item = {
        "name" : name,
        "base_beverage" : BeverageType.GIN, # GIN
        "beverage_type" : BeverageType.COCKTAIL, # COCKTAIL
        "ingredients": [
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
        "description" : f"The worst {name} in the world!",
        "tags": [
            "good bye",
            "world"
        ]
    }

    pk = arrange_pk(BeverageType.COCKTAIL)
    sk = arrange_sk(BeverageType.GIN, name)
    
    response = client.put(url=f"/beverages/pk/{pk}/sk/{sk}", json=update_item)
    assert response.status_code == 200

    data = response.json()
    assert data["items"]['description'] == f"The worst {name} in the world!"

    client.delete(f"/beverages/pk/{pk}/sk/{sk}")
    
def delete_cocktail_beverage_success():
    name = "".join(choices(ascii_letters, k=10))
    item = {
        "name" : name,
        "base_beverage" : 2, # GIN
        "beverage_type" : 1, # COCKTAIL
        "ingredients": [
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
        "description" : f"The best {name} in the world!",
        "tags": [
            "hello",
            "world"
        ]
    }

    response = client.post(url="/beverages", json=item)
    assert response.status_code == 201

    pk = arrange_pk(BeverageType.COCKTAIL)
    sk = arrange_sk(BeverageType.GIN, name)

    res = client.delete(f"/beverages/pk/{pk}/sk/{sk}")

    assert res.status_code == 202

def test_get_existing_beverage_success():
    name =  "".join(choices(ascii_letters, k=10))
    item = {
        "name" : name,
        "base_beverage" : 2, # GIN
        "beverage_type" : 1, # COCKTAIL
        "ingredients": [
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
        "description" : f"The best {name} in the world!",
        "tags": [
            "hello",
            "world"
        ]
    }

    response = client.post(url="/beverages", json=item)
    assert response.status_code == 201

    pk= arrange_pk(BeverageType.COCKTAIL)
    sk = arrange_sk(BeverageType.GIN, name)

    response = client.get(f"/beverages/pk/{pk}/sk/{sk}")
    assert response.status_code == 200
    assert response.json()["item"]["name"] == name

    client.delete(f"/beverages/pk/{pk}/sk/{sk}")

def test_get_beverages_filter_success():    
    name1 = "".join(choices(ascii_letters, k=10))
    item1 = {
        "name" : name1,
        "base_beverage" : 2, # GIN
        "beverage_type" : 1, # COCKTAIL
        "ingredients": [
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
        "description" : f"The best {name1} in the world!",
        "tags": [
            "hello",
            "world"
        ]
    }

    name2 = "".join(choices(ascii_letters, k=10))
    item2 = {
        "name" : name2,
        "base_beverage" : "Dry Gin", 
        "beverage_type" : 2, # GIN
        "description" : f"The best {name2} in the world!",
        "tags": [
            "hello",
            "world"
        ]
    }

    response = client.post(url="/beverages", json=item1)
    assert response.status_code == 201

    response = client.post(url="/beverages", json=item2)
    assert response.status_code == 201

    response = client.get("/beverages")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 2

    response = client.get("/beverages/?b_type=1") # Cocktails only
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["name"] == name1

    response = client.get("/beverages/?b_type=2") # Gin only
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["name"] == name2


    pk1 = arrange_pk(BeverageType.COCKTAIL)
    sk1 = arrange_sk(BeverageType.GIN, name1)

    client.delete(f"/beverages/pk/{pk1}/sk/{sk1}")

    pk2 = arrange_pk(BeverageType.GIN)
    sk2 = arrange_sk(item2["base_beverage"], name2)

    client.delete(f"/beverages/pk/{pk2}/sk/{sk2}")