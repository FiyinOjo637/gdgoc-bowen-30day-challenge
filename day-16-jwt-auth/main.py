from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic import BaseModel
from datetime import datetime, timedelta
import bcrypt
import jwt

app = FastAPI(title="JWT Auth API - Day 16")
engine = create_engine("sqlite:///users.db", echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)
security = HTTPBearer()

SECRET_KEY = "gdgoc-bowen-secret-key-2026"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24

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

class LoginDTO(BaseModel):
    email: str
    password: str

# JWT Helper functions
def create_token(user_id: int, email: str):
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@app.post("/auth/signup", status_code=201)
def signup(data: SignupDTO):
    db = SessionLocal()
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
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
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not bcrypt.checkpw(data.password.encode("utf-8"), user.password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(user.id, user.email)
    return {
        "access_token": token,
        "token_type": "bearer",
        "email": user.email
    }

@app.get("/protected")
def protected_route(current_user: dict = Depends(verify_token)):
    return {
        "message": "You have access to this protected route!",
        "user": current_user
    }

@app.get("/profile")
def get_profile(current_user: dict = Depends(verify_token)):
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "message": "This is your profile"
    }