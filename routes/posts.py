from schemas.post import PostBase

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from database import insert_post, get_all_posts, get_post_by_id,get_user_id
from uuid import UUID
from database import add_upvote, remove_upvote, has_upvoted

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
def get_post(post_id: str):
    try:
        post = get_post_by_id(post_id)
        if post:
            return JSONResponse(status_code=200, content={"post": post})
        return JSONResponse(status_code=404, content={"message": "Post not found"})
    except Exception as e:
        print("🔥 API error:", e)
        return JSONResponse(status_code=500, content={"error": str(e)})

# Add this to routes/posts.py after the other routes

@router.get("/api/upvote/check/{post_id}")
def check_upvote(post_id: str, username: str = Query(...)):
    try:
        post_id = UUID(post_id)
    except ValueError:
        return JSONResponse(status_code=400, content={"message": "Invalid post ID"})

    user_id = get_user_id(username)
    if not user_id:
        return JSONResponse(status_code=404, content={"message": "User not found"})

    upvoted = has_upvoted(post_id, user_id)
    return JSONResponse(status_code=200, content={"upvoted": upvoted})

@router.post("/api/upvote/{post_id}")
def upvote_toggle(post_id: str, username: str = Query(...)):
    try:
        post_id = UUID(post_id)
    except ValueError:
        return JSONResponse(status_code=400, content={"message": "Invalid post ID"})

    user_id = get_user_id(username)
    if not user_id:
        return JSONResponse(status_code=404, content={"message": "User not found"})

    if has_upvoted(post_id, user_id):
        removed = remove_upvote(post_id, user_id)
        return JSONResponse(status_code=200, content={"message": "Removed"})
    else:
        added = add_upvote(post_id, user_id)
        return JSONResponse(status_code=200, content={"message": "Upvoted"})

                           
    
    





