from fastapi import Header, APIRouter, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer
import uuid
from app.utils.database import get_db_connection 
from app.utils.models import SubmitInput
from datetime import datetime
from app.analyzer_logic.graph import analyze_code

file_router = APIRouter()
security = HTTPBearer()

@file_router.post("/submit_code")
def submit_code(payload:SubmitInput,background_tasks: BackgroundTasks):

    payload = payload.model_dump()
    user_code = payload.get("code")
    username = payload.get("username")
    print(username,user_code)
    if not user_code:
        raise HTTPException(status_code=400, detail="Code is required.")
    print(user_code)
    job_id = str(uuid.uuid4())

    db, conn = get_db_connection()
    conn.execute("INSERT into job(job_id,status,username,created_at,result,error) VALUES (?, ?, ?, ?, ?, ?)",
                (job_id,"processing",username,datetime.now().isoformat(),None,None))
    db.commit()
    conn.close()

    background_tasks.add_task(analyze_code_task, user_code, username, job_id)

    return {"job_id":job_id,"status":"processing"}

@file_router.get("/job/{username}/{job_id}")
def get_job_status(username:str,job_id: str):

    db,conn = get_db_connection()
    conn.execute("select * from job where username= ? AND job_id = ?",(username,job_id))
    jobs = conn.fetchone()
    
    print(jobs)
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found.")
    
    print(jobs[0])

    return {
        "job_id": jobs[0],
        "status": jobs[1],
        "created_at": jobs[3],
        "result": jobs[4] if jobs[4] == "completed" else None,
        "error": jobs[5]
    }

def analyze_code_task(user_code: str, user_id: str, job_id: str):
    """Background task to analyze code and update job status."""
    try:
        # print(user_code,type(user_code))
        result = analyze_code(user_code, user_id, job_id)
        print(result)

        db,conn = get_db_connection()
        conn.execute("update job set status= ?,path=? where job_id=?",("completed",result['file_path'],job_id))
        db.commit()
        conn.close()

    except Exception as e:
        db,conn = get_db_connection()
        conn.execute("update job set status= ?,error= ? where job_id=?",("failed",result["metadata"]["error"],job_id))
        db.commit()
        conn.close()