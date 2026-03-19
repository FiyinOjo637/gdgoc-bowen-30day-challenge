from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timedelta
from typing import Optional, List
import time

app = FastAPI(title="Caching Intro - Day 24")
engine = create_engine("sqlite:///shop.db", connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# In-memory cache
cache = {}
CACHE_TTL = 60  # seconds

def get_from_cache(key: str):
    if key in cache:
        data, expires_at = cache[key]
        if time.time() < expires_at:
            print(f" CACHE HIT for key: {key}")
            return data
        else:
            del cache[key]
            print(f" CACHE EXPIRED for key: {key}")
    print(f" CACHE MISS for key: {key}")
    return None

def set_cache(key: str, data):
    cache[key] = (data, time.time() + CACHE_TTL)
    print(f" CACHE SET for key: {key} (expires in {CACHE_TTL}s)")

# Models
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    items = relationship("Item", back_populates="category")

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    category = relationship("Category", back_populates="items")

Base.metadata.create_all(engine)

# Seed
db = SessionLocal()
if db.query(Category).count() == 0:
    cats = [
        Category(name="Electronics", description="Electronic devices"),
        Category(name="Accessories", description="Device accessories"),
        Category(name="Furniture", description="Home and office furniture"),
    ]
    db.add_all(cats)
    db.commit()
    elec = db.query(Category).filter(Category.name == "Electronics").first()
    db.add_all([
        Item(name="Laptop", price=999.99, category_id=elec.id),
        Item(name="Phone", price=699.99, category_id=elec.id),
        Item(name="Headphones", price=199.99, category_id=elec.id),
    ])
    db.commit()
db.close()

@app.get("/")
def home():
    return {"message": "Caching Demo API", "cache_ttl": f"{CACHE_TTL} seconds"}

@app.get("/categories")
def get_categories():
    cache_key = "all_categories"
    cached = get_from_cache(cache_key)
    if cached:
        return {"source": "cache", "data": cached}

    # Cache miss — hit the database
    db = SessionLocal()
    categories = db.query(Category).all()
    result = [
        {
            "id": cat.id,
            "name": cat.name,
            "description": cat.description,
            "itemCount": len(cat.items)
        }
        for cat in categories
    ]
    db.close()

    set_cache(cache_key, result)
    return {"source": "database", "data": result}

@app.get("/items")
def get_items():
    cache_key = "all_items"
    cached = get_from_cache(cache_key)
    if cached:
        return {"source": "cache", "data": cached}

    db = SessionLocal()
    items = db.query(Item).all()
    result = [
        {
            "id": item.id,
            "name": item.name,
            "price": float(item.price),
        }
        for item in items
    ]
    db.close()

    set_cache(cache_key, result)
    return {"source": "database", "data": result}

@app.delete("/cache")
def clear_cache():
    cache.clear()
    return {"message": "Cache cleared successfully"}