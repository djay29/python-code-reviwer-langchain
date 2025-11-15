from fastapi import APIRouter,HTTPException,Header
from fastapi.security import HTTPBearer
import hashlib
import secrets
from datetime import datetime,timedelta
import sqlite3
from app.utils.models import UserCreate, UserLogin, Token
from app.utils.database import get_db_connection

auth_routes = APIRouter()
security = HTTPBearer()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_session_token(user_id: int) -> tuple[str, datetime]:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=7)
    
    db,conn = get_db_connection()
    db.execute(
        "INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)",
        (user_id, token, expires_at)
    )
    db.commit()
    conn.close()
    
    return token, expires_at

@auth_routes.post("/register",response_model=Token)
def register(user : UserCreate):
    password_hash = hash_password(user.password)

    try:
        db,conn = get_db_connection()
        db.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (user.username, user.email, password_hash))
        db.commit()
        conn.close()
        user_id = user.username
        token, _ = create_session_token(user_id)
        return {
            "access_token":token,"token_type":"bearer"
        }
    
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
@auth_routes.post("/login", response_model=Token)
def login(credentials: UserLogin):
    password_hash = hash_password(credentials.password)

    db,conn = get_db_connection()
    conn.execute(
        "SELECT id FROM users WHERE username = ? AND password_hash = ?",
        (credentials.username, password_hash)
    )

    user = conn.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token, _ = create_session_token(user[0])
    return {"access_token": token, "token_type": "bearer"}

@auth_routes.post("/logout")
def logout(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    
    token = authorization.replace("Bearer ", "")
    
    db,conn = get_db_connection()
    conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    db.commit()
    conn.close()
    
    return {"message": "Logged out successfully"}