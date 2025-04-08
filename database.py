from datetime import datetime
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
def get_all_posts(status=None, sort="latest"):
    query = helper_query(status, sort)
    with engine.connect() as conn:
        results = conn.execute(text(query)).mappings().all()
    
    posts = []

    for row in results:
        post_dict = dict(row)

        # Convert UUIDs to strings
        for key, value in post_dict.items():
            if isinstance(value, UUID):
                post_dict[key] = str(value)

        # Add time_ago using created_at, then remove created_at
        post_dict["time_ago"] = format_time_ago(row["created_at"])
        post_dict.pop("created_at", None)  # Safely remove created_at

        posts.append(post_dict)

    return posts


from uuid import UUID
from sqlalchemy import text
from utils import format_time_ago

def get_post_by_id(post_id):
    try:
        post_id = UUID(post_id)
    except ValueError:
        print("Invalid UUID format:", post_id)
        return False

    with engine.connect() as conn:
        query = text("""
            SELECT 
                posts.id,
                posts.title,
                posts.content,
                posts.status,
                posts.created_at,
                users.username,
                COALESCE(COUNT(DISTINCT upvotes.id), 0) AS upvotes,
                COALESCE(COUNT(DISTINCT comments.id), 0) AS comments
            FROM posts
            JOIN users ON posts.user_id = users.id
            LEFT JOIN upvotes ON upvotes.post_id = posts.id
            LEFT JOIN comments ON comments.post_id = posts.id
            WHERE posts.id = :post_id
            GROUP BY posts.id, posts.title, posts.content, posts.status, posts.created_at, users.username
        """)
        result = conn.execute(query, {"post_id": post_id}).mappings().all()

    if len(result) == 0:
        return False

    post_dict = dict(result[0])
    
    # Convert UUIDs to string
    post_dict["id"] = str(post_dict["id"])

    # Format time ago
    if "created_at" in post_dict:
        post_dict["time_ago"] = format_time_ago(post_dict["created_at"])
        post_dict.pop("created_at", None)
    else:
        post_dict["time_ago"] = "Unknown"

    return post_dict


