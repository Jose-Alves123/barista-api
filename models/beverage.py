from pydantic import BaseModel, field_validator, model_validator
from enum import Enum

import logging

logger = logging.getLogger("uvicorn.error")  # uvicorn logs

class BeverageType(int, Enum):
    COCKTAIL = 1
    GIN = 2
    BEER = 3
    WINE = 4
    VODKA = 5

    @classmethod
    def _missing_(cls, value):
        return cls.COCKTAIL
    
    def __str__(self) -> str:
        return super().__str__()


class Beverage(BaseModel):
    name : str
    description: str
    beverage_type: BeverageType
    base_beverage: BeverageType | str
    ingredients : list[dict] | None = []
    tags: list[str]
    default_images : list[str] | None = []
    sum_score : int | None = 0
    count_score : int | None = 0

    @field_validator("description")
    def validate_description_length(cls, v):
        logger.info("Hello from validate_description_length")
        if len(v) < 10 or len(v) > 500:
            raise ValueError("Description field must have between 10 and 500 characters")
        
        return v

    @model_validator(mode='after')
    def validate_base_beverage(self):
        logger.info(self.base_beverage)
        logger.info( self.beverage_type)

        if self.beverage_type.value != BeverageType.COCKTAIL.value and isinstance(self.base_beverage, BeverageType):
            raise ValueError("A non cocktail beverage must nor have any base beverage.")
        
        if self.beverage_type.value != BeverageType.COCKTAIL.value and isinstance(self.base_beverage, str) and len(self.base_beverage) < 1:
            raise ValueError("Please provide the subclass of the beverage")

        if isinstance(self.base_beverage, BeverageType) and self.base_beverage.value == self.beverage_type.value == BeverageType.COCKTAIL.value:
            raise ValueError("A cocktail must not have a base beverage of type Cocktail")
        
        return self
    
    @model_validator(mode='after')
    def validate_ingredients(self):
        if self.beverage_type == BeverageType.COCKTAIL:
            if not self.ingredients or len(self.ingredients) <= 1:
                raise ValueError("Cocktails must have at least two ingredients")
        else:
            if self.ingredients:
                raise ValueError("Non-cocktail beverages cannot have ingredients")

        return self

    @model_validator(mode='after')
    def validate_tags(self):

        assert self.tags != None
        tags_set = set([e for e in self.tags])
        if len(tags_set) != len(self.tags):
            raise ValueError("Must not repeat values in tags")

        return self
    

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "GinFizz",
                    "description": "The best Giz Fizz in the world",
                    "beverage_type": BeverageType.COCKTAIL,
                    "base_beverage" : BeverageType.GIN,
                    "tags" : ["hello", "world"],
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
                        },
                    ],
                    "default_images" : [],
                    "sum_score" : 0,
                    "count_score" : 0
                }
            ]
        }
    }