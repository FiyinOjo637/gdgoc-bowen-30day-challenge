from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, Integer, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
import jwt

app = FastAPI(title="Permissions & Ownership - Day 17")
engine = create_engine("sqlite:///app.db", echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)
security = HTTPBearer()

SECRET_KEY = "gdgoc-bowen-secret-key-2026"
ALGORITHM = "HS256"

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

# DTOs
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

class ItemUpdateDTO(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

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
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Auth routes
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
        "access_token": create_token(user.id, user.email),
        "token_type": "bearer"
    }

# Item routes
@app.post("/items", status_code=201)
def create_item(item: ItemCreateDTO, current_user: dict = Depends(verify_token)):
    db = SessionLocal()
    new_item = Item(
        name=item.name,
        description=item.description,
        price=item.price,
        user_id=current_user["user_id"]
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    db.close()
    return {
        "id": new_item.id,
        "name": new_item.name,
        "price": float(new_item.price),
        "user_id": new_item.user_id
    }

@app.delete("/items/{item_id}", status_code=200)
def delete_item(item_id: int, current_user: dict = Depends(verify_token)):
    db = SessionLocal()
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")
    if item.user_id != current_user["user_id"]:
        db.close()
        raise HTTPException(status_code=403, detail="Forbidden — you don't own this item")
    db.delete(item)
    db.commit()
    db.close()
    return {"message": "Item deleted successfully"}

@app.put("/items/{item_id}")
def update_item(
    item_id: int,
    data: ItemUpdateDTO,
    current_user: dict = Depends(verify_token)
):
    db = SessionLocal()
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")
    if item.user_id != current_user["user_id"]:
        db.close()
        raise HTTPException(status_code=403, detail="Forbidden — you don't own this item")
    if data.name: item.name = data.name
    if data.description: item.description = data.description
    if data.price: item.price = data.price
    db.commit()
    db.refresh(item)
    db.close()
    return {
        "id": item.id,
        "name": item.name,
        "price": float(item.price),
        "user_id": item.user_id
    }