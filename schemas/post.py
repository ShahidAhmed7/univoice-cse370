from pydantic import BaseModel

class PostBase(BaseModel):
    title : str 
    content : str 
    username : str

class CommentBase(BaseModel):
    content : str
    username : str
    post_id : str 
