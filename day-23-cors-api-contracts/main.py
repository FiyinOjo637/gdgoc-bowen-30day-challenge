from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, Integer, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from pydantic import BaseModel, field_validator
from datetime import datetime, timedelta
from typing import Optional, List
import bcrypt
import jwt
import os

app = FastAPI(
    title="GDGoC Bowen API",
    description="Production-ready REST API with CORS enabled",
    version="1.0.0"
)

# CORS Configuration
origins = [
    "http://localhost:3000",    # React dev server
    "http://localhost:5173",    # Vite dev server
    "http://localhost:8080",    # Vue dev server
    "https://gdgoc-bowen-api.onrender.com",  # Production
    "*"                         # Allow all for development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")
SECRET_KEY = os.getenv("SECRET_KEY", "gdgoc-bowen-secret-key-2026")
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
    createdAt = Column(DateTime, default=datetime.utcnow)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    items = relationship("Item", back_populates="category")

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    categoryId = Column(Integer, ForeignKey("categories.id"), nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow)
    category = relationship("Category", back_populates="items")

Base.metadata.create_all(engine)

# Seed
db = SessionLocal()
if db.query(Category).count() == 0:
    db.add_all([
        Category(name="Electronics"),
        Category(name="Accessories"),
    ])
    db.commit()
if db.query(Item).count() == 0:
    elec = db.query(Category).filter(Category.name == "Electronics").first()
    db.add_all([
        Item(name="Laptop", description="High performance laptop", price=999.99, categoryId=elec.id),
        Item(name="Phone", description="Latest smartphone", price=699.99, categoryId=elec.id),
    ])
    db.commit()
db.close()

# DTOs — camelCase for frontend
class SignupDTO(BaseModel):
    email: str
    password: str

class LoginDTO(BaseModel):
    email: str
    password: str

class ItemCreateDTO(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    categoryId: Optional[int] = None

    @field_validator("price")
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Price must be positive")
        return v

class CategoryResponseDTO(BaseModel):
    id: int
    name: str

class ItemResponseDTO(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    categoryId: Optional[int]
    category: Optional[CategoryResponseDTO]
    createdAt: str

def create_token(user_id: int, email: str):
    payload = {
        "userId": user_id,
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
@app.get("/")
def home():
    return {
        "message": "GDGoC Bowen API",
        "version": "1.0.0",
        "status": "live",
        "cors": "enabled"
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

@app.get("/items")
def get_items():
    db = SessionLocal()
    items = db.query(Item).all()
    result = [
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "price": float(item.price),
            "categoryId": item.categoryId,
            "category": {"id": item.category.id, "name": item.category.name} if item.category else None,
            "createdAt": str(item.createdAt)
        }
        for item in items
    ]
    db.close()
    return {"data": result, "count": len(result)}

@app.post("/items", status_code=201)
def create_item(item: ItemCreateDTO, current_user: dict = Depends(verify_token)):
    db = SessionLocal()
    new_item = Item(
        name=item.name,
        description=item.description,
        price=item.price,
        categoryId=item.categoryId
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    db.close()
    return {"id": new_item.id, "name": new_item.name, "price": float(new_item.price)}