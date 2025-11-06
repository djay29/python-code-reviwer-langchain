from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.graph import analyze_code

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['http://localhost:3000'],
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)
