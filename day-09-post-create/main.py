from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, Text, Numeric, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

app = FastAPI()
engine = create_engine("sqlite:///items.db", echo=True)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# Database Model
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

# Request DTO
class ItemCreateDTO(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

    @field_validator("price")
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Price must be a positive number")
        return v

# Response DTO
class ItemResponseDTO(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    created_at: datetime

    class Config:
        from_attributes = True

@app.post("/items", response_model=ItemResponseDTO, status_code=201)
def create_item(item: ItemCreateDTO):
    db = SessionLocal()
    new_item = Item(
        name=item.name,
        description=item.description,
        price=item.price
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    db.close()
    return new_item