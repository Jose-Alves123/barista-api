from fastapi import APIRouter, status
from datetime import datetime
import boto3
import logging

router = APIRouter()