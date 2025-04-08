from sqlalchemy import create_engine,text
from dotenv import load_dotenv
import os
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError

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

