from schemas.post import PostBase

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from database import insert_post

router = APIRouter()

@router.post("/api/new-post")
def new_post(post : PostBase):
    add_to_db = insert_post(post.username,post.title,post.content)
    if add_to_db:
        return JSONResponse(
            status_code = 201,
            content = {"message" : "Successfully posted your issue"}
        )
    else :
        return JSONResponse(
            status_code = 400,
            content = {"message" : "Failed to post"}
        )
    
    
    





