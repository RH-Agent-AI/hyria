from fastapi import FastAPI
from candidats import router as candidats_router
from job_description import router as job_description_router
from applications import router as applications_router
from call import router as call_router
from candidate_info import router as candidate_info_router
from elevenlabs_webhook import router as elevenlabs_router 

app = FastAPI()

app.include_router(candidats_router)
app.include_router(job_description_router)
app.include_router(applications_router)
app.include_router(call_router)
app.include_router(candidate_info_router)
app.include_router(elevenlabs_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
