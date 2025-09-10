from . import s3_service as s3
from . import beverages_service as beverage
from . import dynamodb_service as dynamodb
from . import json_service as json
from . import reviews_service as review

__all__ = [
    "s3",
    "beverage",
    "dynamodb",
    "json",
    "review"
]