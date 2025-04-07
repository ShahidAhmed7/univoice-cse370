import bcrypt
import os 
from dotenv import load_dotenv
from itsdangerous import URLSafeSerializer

def create_password_hash(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')  # convert bytes to string for DB storage

def verify_password(given_pw: str, password_hash: str) -> bool:
    return bcrypt.checkpw(given_pw.encode('utf-8'), password_hash.encode('utf-8'))

load_dotenv()

secret_key = os.getenv("SECRET_KEY")
serializer = URLSafeSerializer(secret_key)