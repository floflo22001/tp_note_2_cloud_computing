import boto3
from botocore.config import Config
import os
from dotenv import load_dotenv
from typing import Union, List, Dict
import logging
from fastapi import FastAPI, Request, status, Header
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from boto3.dynamodb.conditions import Key, Attr
import uuid

from getSignedUrl import getSignedUrl

load_dotenv()

app = FastAPI()
logger = logging.getLogger("uvicorn")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logger.error(f"{request}: {exc_str}")
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class Post(BaseModel):
    title: str
    body: str


my_config = Config(
    region_name='us-east-1',
    signature_version='v4',
)

dynamodb = boto3.resource('dynamodb', config=my_config)
table = dynamodb.Table(os.getenv("DYNAMO_TABLE"))
s3_client = boto3.client('s3', config=my_config)
bucket = os.getenv("BUCKET")


@app.post("/posts")
async def post_a_post(post: Post, authorization: str | None = Header(default=None)):

    item = {
        'id': str(uuid.uuid4()),
        'title': post.title,
        'body': post.body,
        'user': authorization
    }

    logger.info(f"title : {post.title}")
    logger.info(f"body : {post.body}")
    logger.info(f"user : {authorization}")

    # Doit retourner le résultat de la requête la table dynamodb
    try:
        table.put_item(Item=item)
        return {"status": "success", "data": item}
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.get("/posts")
async def get_all_posts(user: Union[str, None] = None):

    # Doit retourner une liste de post
    try:
        if user:
            response = table.scan(FilterExpression=Attr('user').eq(user))
        else:
            response = table.scan()
        return {"status": "success", "data": response.get('Items', [])}
    except Exception as e:
        logger.error(f"Error getting posts: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


    
@app.delete("/posts/{post_id}")
async def get_post_user_id(post_id: str):
    # Doit retourner le résultat de la requête la table dynamodb
    try:
        response = table.delete_item(
            Key={'id': post_id},
            ReturnValues='ALL_OLD'
        )
        if 'Attributes' in response:
            return {"status": "success", "data": response['Attributes']}
        else:
            return JSONResponse(status_code=404, content={"status": "error", "message": "Post not found"})
    except Exception as e:
        logger.error(f"Error deleting post: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@app.get("/signedUrlPut")
async def get_signed_url_put(filename: str,filetype: str, postId: str,authorization: str | None = Header(default=None)):
    return getSignedUrl(filename, filetype, postId, authorization)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")

