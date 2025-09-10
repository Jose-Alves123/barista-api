import boto3, os, logging, io
from fastapi import UploadFile
from typing import Tuple, List, Dict

logger = logging.getLogger("uvicorn.error")  # uvicorn logs

__s3 = boto3.client(
    "s3",
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    endpoint_url=os.getenv("S3_ENDPOINT_URL")          # present only in dev
)

def get_image(img : str = 'cocktail-default-image.jpg'):
    """"
    Get presigned url from S3 object. If no str is provided, default image presigned
    url is obtained

    Args:
        img (str) default empty string - name of object in s3
    
    Returns:
        str of presigned url
    """
    url = __s3.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': 'cocktail-api',
                                    'Key': img,
                                },                                  
                                ExpiresIn=3600)
    return url


def upload_image(file: UploadFile, bucket : str, object_name: str) -> int:
    temp_file = io.BytesIO()
    status = 200
    try:
        logger.info("Start uploading file to S3")
        contents = file.file.read()
        
        temp_file.write(contents)
        temp_file.seek(0)
        __s3.upload_fileobj(temp_file, bucket, object_name)
    except Exception as e:
        logger.info("Failed to add to S3")
        status = 500
    finally:
        temp_file.close()
    
    return status

def delete_image(obj_name : str, bucket: str) -> int:
    status = 200
    try:
        __s3.delete_object(
            Bucket=bucket,
            Key=obj_name
        )
    except Exception as e:
        logger.info("Failed to delete file")
        status = 500

    return status