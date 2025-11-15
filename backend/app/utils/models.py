from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class SubmitInput(BaseModel):
    code : str
    user_id : str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: str

class SessionResponse(BaseModel):
    id: int
    user_id: int
    token: str
    expires_at: str

class Token(BaseModel):
    access_token: str
    token_type: str
