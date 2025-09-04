from .routes.beverage import router as beverage_router
from .routes.review import router as review_router
from .routes.beverage_type import router as beverage_type_router

__all__ = [
    "beverage_router",
    "review_router",
    "beverage_type_router"
]