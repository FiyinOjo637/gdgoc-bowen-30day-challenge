from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="GDGoC Bowen API - Dockerized")

@app.get("/")
def home():
    return {
        "message": "App is running inside Docker!",
        "timestamp": str(datetime.utcnow()),
        "status": "healthy"
    }

@app.get("/status")
def status():
    return {"status": "up", "container": "Docker"}