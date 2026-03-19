from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List
import bcrypt
import jwt
import os

app = FastAPI(
    title="To-Do App API",
    description="GDGoC Bowen Capstone Project — Task Management API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///todo.db")
SECRET_KEY = os.getenv("SECRET_KEY", "gdgoc-bowen-todo-secret-2026")
ALGORITHM = "HS256"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)
security = HTTPBearer()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

Base.metadata.create_all(engine)

# DTOs
class SignupDTO(BaseModel):
    email: str
    password: str

class LoginDTO(BaseModel):
    email: str
    password: str

class TaskCreateDTO(BaseModel):
    title: str
    description: Optional[str] = None

class TaskUpdateDTO(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# JWT helpers
def create_token(user_id: int, email: str):
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        return jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# Auth routes
@app.get("/")
def home():
    return {
        "app": "To-Do App API",
        "version": "1.0.0",
        "status": "live",
        "endpoints": ["/auth/signup", "/auth/login", "/tasks"]
    }

@app.post("/auth/signup", status_code=201)
def signup(data: SignupDTO):
    db = SessionLocal()
    if db.query(User).filter(User.email == data.email).first():
        db.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt())
    user = User(email=data.email, password=hashed.decode("utf-8"))
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return {"message": "Signup successful", "email": user.email}

@app.post("/auth/login")
def login(data: LoginDTO):
    db = SessionLocal()
    user = db.query(User).filter(User.email == data.email).first()
    db.close()
    if not user or not bcrypt.checkpw(
        data.password.encode("utf-8"), user.password.encode("utf-8")
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "accessToken": create_token(user.id, user.email),
        "tokenType": "bearer",
        "email": user.email
    }

# Task routes
@app.get("/tasks")
def get_tasks(current_user: dict = Depends(verify_token)):
    db = SessionLocal()
    tasks = db.query(Task).filter(Task.user_id == current_user["user_id"]).all()
    db.close()
    return {
        "data": [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "completed": t.completed,
                "createdAt": str(t.created_at),
                "updatedAt": str(t.updated_at)
            }
            for t in tasks
        ],
        "count": len(tasks)
    }

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreateDTO, current_user: dict = Depends(verify_token)):
    db = SessionLocal()
    new_task = Task(
        title=task.title,
        description=task.description,
        user_id=current_user["user_id"]
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    db.close()
    return {
        "id": new_task.id,
        "title": new_task.title,
        "description": new_task.description,
        "completed": new_task.completed,
        "createdAt": str(new_task.created_at)
    }

@app.put("/tasks/{task_id}")
def update_task(task_id: int, data: TaskUpdateDTO, current_user: dict = Depends(verify_token)):
    db = SessionLocal()
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user["user_id"]
    ).first()
    if not task:
        db.close()
        raise HTTPException(status_code=404, detail="Task not found")
    if data.title is not None: task.title = data.title
    if data.description is not None: task.description = data.description
    if data.completed is not None: task.completed = data.completed
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    db.close()
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "updatedAt": str(task.updated_at)
    }

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, current_user: dict = Depends(verify_token)):
    from fastapi.responses import Response
    db = SessionLocal()
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user["user_id"]
    ).first()
    if not task:
        db.close()
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    db.close()
    return Response(status_code=204)