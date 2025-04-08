import bcrypt
import os 
from dotenv import load_dotenv
from itsdangerous import URLSafeSerializer
from datetime import datetime

def create_password_hash(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')  # convert bytes to string for DB storage

def verify_password(given_pw: str, password_hash: str) -> bool:
    return bcrypt.checkpw(given_pw.encode('utf-8'), password_hash.encode('utf-8'))

load_dotenv()

secret_key = os.getenv("SECRET_KEY")
serializer = URLSafeSerializer(secret_key)

from datetime import datetime, timezone

def format_time_ago(created_at):
    now = datetime.now(timezone.utc)  # now is timezone-aware (UTC)
    diff = now - created_at

    seconds = diff.total_seconds()
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24

    if seconds < 60:
        return "Just now"
    elif minutes < 60:
        return f"{int(minutes)} minute(s) ago"
    elif hours < 24:
        return f"{int(hours)} hour(s) ago"
    else:
        return f"{int(days)} day(s) ago"

def helper_query(status, sort):
    if status is None:
        if sort == "latest":
            query = """
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
                GROUP BY posts.id, users.username
                ORDER BY posts.created_at DESC;
            """
        else:
            query = """
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
                GROUP BY posts.id, users.username
                ORDER BY upvotes DESC;
            """

    elif status in ["pending", "eligible", "submitted"]:
        if sort == "latest":
            query = f"""
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
                WHERE posts.status = '{status}'
                GROUP BY posts.id, users.username
                ORDER BY posts.created_at DESC;
            """
        else:
            query = f"""
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
                WHERE posts.status = '{status}'
                GROUP BY posts.id, users.username
                ORDER BY upvotes DESC;
            """

    return query
