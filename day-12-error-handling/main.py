from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy import create_engine, Column, Integer, String, Text, Numeric, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

app = FastAPI()
engine = create_engine("sqlite:///items.db", echo=True)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

# Seed data
db = SessionLocal()
if db.query(Item).count() == 0:
    items = [
        Item(name="Laptop", description="High performance laptop", price=999.99),
        Item(name="Phone", description="Latest smartphone", price=699.99),
        Item(name="Headphones", description="Noise cancelling headphones", price=199.99),
    ]
    db.add_all(items)
    db.commit()
db.close()

# Global 404 Handler
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "message": "Resource not found",
                "status": 404,
                "path": str(request.url)
            }
        }
    )

# Global 400 / Validation Error Handler
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "message": "Invalid input data",
                "status": 400,
                "details": str(exc.errors())
            }
        }
    )

# Global 500 Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "Internal server error",
                "status": 500
            }
        }
    )

# Request DTO
class ItemCreateDTO(BaseModel):
    name: str
    price: float

    @field_validator("price")
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Price must be a positive number")
        return v

@app.get("/items/{item_id}")
def get_item(item_id: int):
    db = SessionLocal()
    item = db.query(Item).filter(Item.id == item_id).first()
    db.close()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item.id, "name": item.name, "price": float(item.price)}

@app.post("/items", status_code=201)
def create_item(item: ItemCreateDTO):
    db = SessionLocal()
    new_item = Item(name=item.name, price=item.price)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    db.close()
    return {"id": new_item.id, "name": new_item.name, "price": float(new_item.price)}