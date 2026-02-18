from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"msg": "hello"}

@app.get("/about")
def about():
    return {"msg": "GDGoC Bowen 30 Day Challenge - Day 1", "track": "Backend Development"} 
