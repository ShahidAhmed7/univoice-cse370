from schemas.post import PostBase

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from database import insert_post, get_all_posts, get_post_by_id
from uuid import UUID

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
    
@router.get("/api/posts")
def get_posts(status : str, sort : str):
    if status == "":
        status = None
    posts = get_all_posts(status,sort)
    
    if len(posts) == 0:
        return JSONResponse(
            status_code = 400,
            content = {"message" : "No posts found"}
        )
    
    if posts:
        return JSONResponse(
            status_code = 200,
            content = {"posts" : posts}
        )
    else :
        return JSONResponse(
            status_code = 400,
            content = {"message" : "Failed to get posts"}
        )

@router.get("/api/posts/{post_id}")
def get_post(post_id: UUID):
    post = get_post_by_id(post_id)
    if post:
        return JSONResponse(
            status_code = 200,
            content = {"post" : post}
        )
    else :
        return JSONResponse(
            status_code = 400,
            content = {"message" : "Failed to get posts"}
        )

                                
    
    





