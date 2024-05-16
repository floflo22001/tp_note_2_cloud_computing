import logging
import boto3
from boto3.dynamodb.conditions import Key
from botocore.config import Config 
import os
import json
import uuid
from pathlib import Path
from botocore.exceptions import ClientError

bucket = os.getenv("BUCKET")
my_config = Config(
    region_name=os.getenv('AWS_REGION', 'us-east-1'),  # Default to 'us-east-1' if AWS_REGION is not set
    signature_version='v4',
)
s3_client = boto3.client('s3', config=my_config)
logger = logging.getLogger("uvicorn")

def getSignedUrl(filename: str,filetype: str, postId: str, user):

    filename = f'{uuid.uuid4()}{Path(filename).name}'
    object_name = f"{user}/{postId}/{filename}"

    try:
        url = s3_client.generate_presigned_url(
            Params={
            "Bucket": bucket,
            "Key": object_name,
            "ContentType": filetype
        },
            ClientMethod='put_object'
        )
    except ClientError as e:
        logging.error(e)


    logger.info(f'Url: {url}')
    return {
            "uploadURL": url,
            "objectName" : object_name
        }