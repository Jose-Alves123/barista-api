import boto3, os

_s3 = boto3.client(
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
    url = _s3.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': 'cocktail-api',
                                    'Key': img,
                                },                                  
                                ExpiresIn=3600)
    return url