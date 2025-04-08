from sqlalchemy import create_engine,text
from dotenv import load_dotenv
import os
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError
from utils import format_time_ago, helper_query
from uuid import UUID
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

def create_user(name,username,password_hash,email,role):
    with engine.connect() as conn:
        trans = conn.begin()
        try : 
            conn.execute(text("""
                INSERT INTO users (name, username, email, password_hash, role)
                VALUES (:name, :username, :email, :password_hash, :role)
            """), {
                "name": name,
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "role": role
            })
            trans.commit()
            return True 
        except:
            trans.rollback()
            return False 
        
def get_user_data(username):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM users WHERE username = :username"), 
                              {"username" : username}).mappings().all()
        if len(result) == 0:
            return False 
        return result[0]

def insert_post(username, title, content):
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            user_query = text("SELECT id FROM users WHERE username = :username")
            user_result = conn.execute(user_query, {"username": username}).fetchone()

            if not user_result:
                raise Exception("User not found")

            user_id = user_result[0]  

            insert_query = text("""
                INSERT INTO posts (user_id, title, content, status, created_at)
                VALUES (:user_id, :title, :content, 'pending', NOW())
            """)
            conn.execute(insert_query, {
                "user_id": user_id,
                "title": title,
                "content": content
            })

            trans.commit()
            print("You posted successfully")
            return True
        
        except Exception as e:
            print(" Error inserting post:", e)
            trans.rollback()
            return False

def get_all_posts(status = None, sort = "latest"):
    query = helper_query(status,sort)
    print(f"print status : {status} and sort : {sort}")
    with engine.connect() as conn:
        results = conn.execute(text(query)).mappings().all()
    
    posts = []

    for row in results:
        post_dict = dict(row)  
        post_dict["time_ago"] = format_time_ago(post_dict["created_at"])
        posts.append(post_dict)

    # Convert UUID objects to strings
    for key, value in post_dict.items():
        if isinstance(value, UUID):
            post_dict[key] = str(value)

    # Add human-readable time
    for post in posts:
        post["time_ago"] = format_time_ago(post["created_at"])

    return posts  

def get_post_by_id(post_id):
    with engine.connect() as conn:
        query = text("""
            SELECT 
                posts.id,
                posts.title,
                posts.content,
                posts.status,
                posts.created_at,
                users.username,
                COUNT(DISTINCT upvotes.id) AS upvotes,
                COUNT(DISTINCT comments.id) AS comments
            FROM posts
            JOIN users ON posts.user_id = users.id
            LEFT JOIN upvotes ON upvotes.post_id = posts.id
            LEFT JOIN comments ON comments.post_id = posts.id
            WHERE posts.id = :post_id
            GROUP BY posts.id, users.username
        """)
        result = conn.execute(query, {"post_id": post_id}).mappings().all()
    
    if len(result) == 0:
        return False 
    
    post_dict = dict(result[0])  
    post_dict["time_ago"] = format_time_ago(post_dict["created_at"])
    return post_dict
