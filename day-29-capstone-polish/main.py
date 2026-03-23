from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
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
    description="""
## GDGoC Bowen Capstone Project

A fully documented Task Management REST API.

### Features
* JWT Authentication
* Full CRUD for tasks
* Task filtering and pagination
* Input validation
* Global error handling
    """,
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global error handlers
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": {"message": "Invalid input data", "status": 400}}
    )

@app.exception_handler(Exception)
async def global_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": {"message": "Internal server error", "status": 500}}
    )

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///todo.db")
SECRET_KEY = os.getenv("SECRET_KEY", "gdgoc-bowen-todo-secret-key-2026-secure")
ALGORITHM = "HS256"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)
security = HTTPBearer()

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
    priority = Column(String, default="medium")
    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

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
    priority: Optional[str] = "medium"

class TaskUpdateDTO(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None

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

# Routes
@app.get("/", tags=["System"])
def home():
    return {
        "app": "To-Do App API",
        "version": "2.0.0",
        "status": "live",
        "docs": "/docs",
        "timestamp": str(datetime.utcnow())
    }

@app.get("/status", tags=["System"])
def status():
    return {"status": "up", "timestamp": str(datetime.utcnow())}

@app.post("/auth/signup", status_code=201, tags=["Auth"],
    summary="Register a new user")
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

@app.post("/auth/login", tags=["Auth"],
    summary="Login and get JWT token")
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

@app.get("/tasks", tags=["Tasks"],
    summary="Get all tasks with filtering and pagination")
def get_tasks(
    current_user: dict = Depends(verify_token),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50),
    completed: Optional[bool] = None,
    priority: Optional[str] = None
):
    db = SessionLocal()
    query = db.query(Task).filter(Task.user_id == current_user["user_id"])
    if completed is not None:
        query = query.filter(Task.completed == completed)
    if priority:
        query = query.filter(Task.priority == priority)
    total = query.count()
    tasks = query.offset((page - 1) * limit).limit(limit).all()
    db.close()
    return {
        "metadata": {
            "total": total,
            "page": page,
            "limit": limit,
            "totalPages": -(-total // limit)
        },
        "data": [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "completed": t.completed,
                "priority": t.priority,
                "createdAt": str(t.created_at),
                "updatedAt": str(t.updated_at)
            }
            for t in tasks
        ]
    }

@app.post("/tasks", status_code=201, tags=["Tasks"],
    summary="Create a new task")
def create_task(task: TaskCreateDTO, current_user: dict = Depends(verify_token)):
    db = SessionLocal()
    new_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
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
        "priority": new_task.priority,
        "createdAt": str(new_task.created_at)
    }

@app.put("/tasks/{task_id}", tags=["Tasks"],
    summary="Update a task")
def update_task(
    task_id: int,
    data: TaskUpdateDTO,
    current_user: dict = Depends(verify_token)
):
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
    if data.priority is not None: task.priority = data.priority
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    db.close()
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "priority": task.priority,
        "updatedAt": str(task.updated_at)
    }

@app.delete("/tasks/{task_id}", status_code=204, tags=["Tasks"],
    summary="Delete a task")
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