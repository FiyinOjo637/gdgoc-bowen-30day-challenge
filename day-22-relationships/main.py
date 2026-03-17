from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

app = FastAPI(title="Relationships & Nested Resources - Day 22")
engine = create_engine("sqlite:///shop.db", connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# Models
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    items = relationship("Item", back_populates="category")

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    category = relationship("Category", back_populates="items")

Base.metadata.create_all(engine)

# Seed data
db = SessionLocal()
if db.query(Category).count() == 0:
    categories = [
        Category(name="Electronics", description="Electronic devices and gadgets"),
        Category(name="Accessories", description="Device accessories"),
        Category(name="Furniture", description="Home and office furniture"),
    ]
    db.add_all(categories)
    db.commit()

if db.query(Item).count() == 0:
    electronics = db.query(Category).filter(Category.name == "Electronics").first()
    accessories = db.query(Category).filter(Category.name == "Accessories").first()
    furniture = db.query(Category).filter(Category.name == "Furniture").first()
    items = [
        Item(name="Laptop", description="High performance laptop", price=999.99, category_id=electronics.id),
        Item(name="Phone", description="Latest smartphone", price=699.99, category_id=electronics.id),
        Item(name="Headphones", description="Noise cancelling", price=199.99, category_id=electronics.id),
        Item(name="Keyboard", description="Mechanical keyboard", price=89.99, category_id=accessories.id),
        Item(name="Mouse", description="Wireless mouse", price=49.99, category_id=accessories.id),
        Item(name="Desk", description="Standing desk", price=399.99, category_id=furniture.id),
    ]
    db.add_all(items)
    db.commit()
db.close()

# DTOs
class CategoryDTO(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True

class ItemWithCategoryDTO(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    category: Optional[CategoryDTO]

    class Config:
        from_attributes = True

class CategoryWithItemsDTO(BaseModel):
    id: int
    name: str
    description: Optional[str]
    items: List[ItemWithCategoryDTO]

    class Config:
        from_attributes = True

# Routes
@app.get("/items", response_model=List[ItemWithCategoryDTO])
def get_all_items():
    db = SessionLocal()
    items = db.query(Item).all()
    result = [
        ItemWithCategoryDTO(
            id=item.id,
            name=item.name,
            description=item.description,
            price=float(item.price),
            category=CategoryDTO(
                id=item.category.id,
                name=item.category.name,
                description=item.category.description
            ) if item.category else None
        )
        for item in items
    ]
    db.close()
    return result

@app.get("/items/{item_id}", response_model=ItemWithCategoryDTO)
def get_item(item_id: int):
    db = SessionLocal()
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")
    result = ItemWithCategoryDTO(
        id=item.id,
        name=item.name,
        description=item.description,
        price=float(item.price),
        category=CategoryDTO(
            id=item.category.id,
            name=item.category.name,
            description=item.category.description
        ) if item.category else None
    )
    db.close()
    return result

@app.get("/categories", response_model=List[CategoryWithItemsDTO])
def get_categories():
    db = SessionLocal()
    categories = db.query(Category).all()
    result = [
        CategoryWithItemsDTO(
            id=cat.id,
            name=cat.name,
            description=cat.description,
            items=[
                ItemWithCategoryDTO(
                    id=item.id,
                    name=item.name,
                    description=item.description,
                    price=float(item.price),
                    category=None
                )
                for item in cat.items
            ]
        )
        for cat in categories
    ]
    db.close()
    return result

@app.get("/categories/{category_id}", response_model=CategoryWithItemsDTO)
def get_category(category_id: int):
    db = SessionLocal()
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        db.close()
        raise HTTPException(status_code=404, detail="Category not found")
    result = CategoryWithItemsDTO(
        id=cat.id,
        name=cat.name,
        description=cat.description,
        items=[
            ItemWithCategoryDTO(
                id=item.id,
                name=item.name,
                description=item.description,
                price=float(item.price),
                category=None
            )
            for item in cat.items
        ]
    )
    db.close()
    return result