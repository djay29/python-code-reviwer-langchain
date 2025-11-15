from fastapi import FastAPI, HTTPException, BackgroundTasks, requests
from fastapi.middleware.cors import CORSMiddleware
from app.analyzer_logic.graph import analyze_code
import uuid
from datetime import datetime
from pydantic import BaseModel
from app.utils.database import create_db
from app.utils.models import SubmitInput
from app.routes.auth import auth_routes
# from app.routes.user_router import user_router
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
# app.include_router(user_router, prefix="/api/users", tags=["Users"])
# app.include_router(sessions_router, prefix="/api/sessions", tags=["Sessions"])



@app.post("/submit_code")
def submit_code(payload:SubmitInput,background_tasks: BackgroundTasks):
    payload = payload.model_dump()
    user_code = payload.get("code")
    user_id = payload.get("user_id")
    if not user_code:
        raise HTTPException(status_code=400, detail="Code is required.")
    print(user_code)
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "status": "processing",
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "result": None,
        "error": None
    }

    background_tasks.add_task(analyze_code_task, user_code, user_id, job_id)

    return {"job_id":job_id,"status":"processing"}

@app.get("/job/{job_id}")
def get_job_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found.")
    
    job = jobs[job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "created_at": job["created_at"],
        "result": job["result"] if job["status"] == "completed" else None,
        "error": job["error"]
    }

def analyze_code_task(user_code: str, user_id: str, job_id: str):
    """Background task to analyze code and update job status."""
    try:
        # print(user_code,type(user_code))
        result = analyze_code(user_code, user_id, job_id)
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

if __name__ == "__main__":
    
    app.run(app, host="0.0.0.0", port=8000,reload=True)