import boto3

_s3 = boto3.client("s3",
    aws_access_key_id="DUMMYIDEXAMPLE",
    aws_secret_access_key="DUMMYEXAMPLEKEY",
    region_name='us-east-1',
    endpoint_url="http://minio:9000"
)


def get_image(img : str = 'cocktail-default-image.jpg'):
    url = _s3.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': 'cocktail-api',
                                    'Key': img,
                                },                                  
                                ExpiresIn=3600)
    return url