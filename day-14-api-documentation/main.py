from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import Response
from sqlalchemy import create_engine, Column, Integer, String, Text, Numeric, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List

app = FastAPI(
    title="GDGoC Bowen 30-Day Challenge API",
    description="""
## Backend Development Track — Fiyinfoluwa Ojo

A fully documented REST API built during the GDGoC Bowen 30-Day Challenge.

### Features
* Create, Read, Update and Delete items
* Pagination and filtering
* Input validation with Pydantic
* Global error handling
    """,
    version="1.0.0",
    contact={
        "name": "Fiyinfoluwa Ojo",
        "url": "https://dev.to/ghost_script",
    }
)

engine = create_engine("sqlite:///items.db", echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    category = Column(String, default="general")
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

db = SessionLocal()
if db.query(Item).count() == 0:
    items = [
        Item(name="Laptop", description="High performance laptop", price=999.99, category="electronics"),
        Item(name="Phone", description="Latest smartphone", price=699.99, category="electronics"),
        Item(name="Headphones", description="Noise cancelling", price=199.99, category="electronics"),
        Item(name="Monitor", description="4K display", price=449.99, category="electronics"),
        Item(name="Keyboard", description="Mechanical keyboard", price=89.99, category="accessories"),
    ]
    db.add_all(items)
    db.commit()
db.close()

class ItemCreateDTO(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = "general"

    @field_validator("price")
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Price must be a positive number")
        return v

class ItemResponseDTO(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    category: str
    created_at: datetime

    class Config:
        from_attributes = True

@app.get(
    "/items",
    response_model=List[ItemResponseDTO],
    summary="Get all items",
    description="Retrieve a paginated list of items with optional filtering by category and price range.",
    tags=["Items"]
)
def get_items(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=5, ge=1, le=20, description="Items per page"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    min_price: Optional[float] = Query(default=None, description="Minimum price"),
    max_price: Optional[float] = Query(default=None, description="Maximum price")
):
    db = SessionLocal()
    query = db.query(Item)
    if category:
        query = query.filter(Item.category == category)
    if min_price:
        query = query.filter(Item.price >= min_price)
    if max_price:
        query = query.filter(Item.price <= max_price)
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    db.close()
    return items

@app.get(
    "/items/{item_id}",
    response_model=ItemResponseDTO,
    summary="Get item by ID",
    description="Retrieve a single item by its unique ID. Returns 404 if not found.",
    tags=["Items"]
)
def get_item(item_id: int):
    db = SessionLocal()
    item = db.query(Item).filter(Item.id == item_id).first()
    db.close()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post(
    "/items",
    response_model=ItemResponseDTO,
    status_code=201,
    summary="Create a new item",
    description="Create a new item with name, description, price and category. Price must be positive.",
    tags=["Items"]
)
def create_item(item: ItemCreateDTO):
    db = SessionLocal()
    new_item = Item(**item.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    db.close()
    return new_item

@app.delete(
    "/items/{item_id}",
    status_code=204,
    summary="Delete an item",
    description="Permanently delete an item by ID. Returns 204 on success, 404 if not found.",
    tags=["Items"]
)
def delete_item(item_id: int):
    db = SessionLocal()
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    db.close()
    return Response(status_code=204)

@app.get(
    "/status",
    summary="Health check",
    description="Check if the API is running.",
    tags=["System"]
)
def status():
    return {"status": "up", "timestamp": str(datetime.utcnow())}