from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.database import create_db
from app.routes.auth_routes import auth_routes
from app.routes.file_routes import file_router
# from app.routes.sessions_router import sessions_router



app = FastAPI()

create_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['http://localhost:3000'],
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

jobs = {}

app.include_router(auth_routes, prefix="/api/auth", tags=["Authentication"])
app.include_router(file_router, prefix="/api/file", tags=["File"])
# app.include_router(sessions_router, prefix="/api/sessions", tags=["Sessions"])

if __name__ == "__main__":
    
    app.run(app, host="0.0.0.0", port=8000,reload=True)