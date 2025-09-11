import boto3, os, io
from fastapi import UploadFile
import os


__s3 = boto3.client(
    "s3",
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
    endpoint_url=os.getenv("S3_ENDPOINT_URL")          # present only in dev
)

def get_image(img : str = 'cocktail-default-image.jpg'):
    """
    Get presigned url from S3 object. If no str is provided, default image presigned
    url is obtained

    Args:
        img (str) default - cocktail-default-image.jpg is default image in bucket for beverages without image
    
    Returns:
        str of presigned url
    """
    url = __s3.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': os.getenv("BUCKET_NAME"),
                                    'Key': img,
                                },                                  
                                ExpiresIn=3600)
    return url

def upload_image(file: UploadFile, object_name: str) -> int:
    """
    Upload image to bucket.

    Args:
        file (UploadFile) - file to upload to S3
        object_name - name of the new object in S3
    
    Returns:
        int confirming status, 200 is success, 500 is insuccess.
    """
    temp_file = io.BytesIO()
    status = 200
    try:
        contents = file.file.read()
        temp_file.write(contents)
        temp_file.seek(0)
        __s3.upload_fileobj(temp_file, os.getenv("BUCKET_NAME"), object_name)
    except Exception as e:
        status = 500
    finally:
        temp_file.close()
    
    return status

def delete_image(obj_name : str) -> int:
    """
    Delete image from bucket

    Args:
        object_name - name of the object in S3
    
    Returns:
        int confirming status, 200 is success, 500 is insuccess.
    """
    status = 200
    try:
        __s3.delete_object(
            Bucket=os.getenv("BUCKET_NAME"),
            Key=obj_name
        )
    except Exception as e:
        status = 500

    return status