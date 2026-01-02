from fastapi import FastAPI, BackgroundTasks
from app import db, utils, worker, llm

app = FastAPI()

@app.post("/jobs")
def submit_job(url: str, background_tasks: BackgroundTasks):
    job_id = utils.hash_url(url)
    job = db.get_job(job_id)
    access_link = utils.generate_access_link()
    if job:
        db.add_access_link(job_id, access_link)
    else:
        job = db.create_job(job_id, url, access_link)
        background_tasks.add_task(worker.process_job, job_id)
    return {"job_id": job_id, "status": job.status, "access_link": access_link}

@app.get("/jobs/{access_link}/status")
def get_status(access_link: str):
    job = db.get_job_by_access_link(access_link)
    return {"status": job.status}

@app.get("/jobs/{access_link}/result")
def get_result(access_link: str):
    job = db.get_job_by_access_link(access_link)
    if job.status != "done":
        return {"status": job.status}
    return {"transcript": job.transcript, "summary": job.summary}

@app.post("/jobs/{access_link}/chat")
def chat(access_link: str, question: str):
    job = db.get_job_by_access_link(access_link)
    answer = llm.ask_question(job.transcript, question)
    return {"answer": answer}
