from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/")
def home():
    return {
        "msg": "Welcome to my API",
        "version": "2.0",
        "track": "Backend Development",
        "challenge": "GDGoC Bowen 30-Day Challenge",
        "day": 10
    }

@app.get("/about")
def about():
    return {
        "developer": "Fiyinfoluwa Ojo",
        "track": "Backend Development",
        "stack": "FastAPI + SQLAlchemy + SQLite",
        "progress": "Day 10 of 30"
    }

@app.get("/status")
def status():
    return {
        "status": "up",
        "message": "Server is running smoothly",
        "timestamp": str(datetime.utcnow()),
        "uptime": "healthy"
    }