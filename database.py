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



