from pydantic import BaseModel, field_validator, model_validator
from typing import Annotated
from fastapi import File
import logging

logger = logging.getLogger("uvicorn.error")  # uvicorn logs

class Review(BaseModel):
    pk: str # Example: GIN|Gin Fizz
    description : str
    score : int
    filename: str


    @field_validator("score")
    def valid_score_between_zero_and_five(cls, v):
        if v < 0 or v > 5:
            raise ValueError("Score can only be an integer from 0 to 5 included.")
        
        return v
    
    @field_validator("filename")
    def validate_file_extension(cls, v):
        logger.info("Start file validation")
        data = v.split(".")
        if len(data) != 2 or data[1] not in ["jpg", "png", "jpeg"]:
            raise ValueError("Can only accept files with format png, jpg or jpeg.")
        logger.info("Passed file type")
        return v