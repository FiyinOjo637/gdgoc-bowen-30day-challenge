from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic import BaseModel, EmailStr
from datetime import datetime
import bcrypt

app = FastAPI(title="Auth API - Day 15")
engine = create_engine("sqlite:///users.db", echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# User Model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

# DTOs
class SignupDTO(BaseModel):
    email: str
    password: str

class UserResponseDTO(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

@app.post("/auth/signup", response_model=UserResponseDTO, status_code=201)
def signup(data: SignupDTO):
    db = SessionLocal()

    # Check if email already exists
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password
    hashed_password = bcrypt.hashpw(
        data.password.encode("utf-8"),
        bcrypt.gensalt()
    )

    new_user = User(
        email=data.email,
        password=hashed_password.decode("utf-8")
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    return new_user

@app.get("/auth/users")
def get_users():
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return {
        "data": [
            {
                "id": u.id,
                "email": u.email,
                "password": u.password,
                "created_at": str(u.created_at)
            }
            for u in users
        ]
    }