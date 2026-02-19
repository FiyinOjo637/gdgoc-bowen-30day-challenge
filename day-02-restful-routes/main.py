from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {
        "msg": "Welcome to my API",
        "version": "1.0",
        "track": "Backend Development"
    }

@app.get("/about")
def about():
    return {
        "name": "Fiyinfoluwa Ojo",
        "challenge": "GDGoC Bowen 30 Day Challenge",
        "track": "Backend Development",
        "day": 2
    }

@app.get("/status")
def status():
    return {
        "status": "up",
        "message": "Server is running smoothly"
    }