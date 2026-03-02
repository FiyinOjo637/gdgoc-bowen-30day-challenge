from fastapi import FastAPI, Query
from sqlalchemy import create_engine, Column, Integer, String, Text, Numeric, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
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
    category = Column(String, default="general")
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

# Seed with more data for pagination to make sense
db = SessionLocal()
if db.query(Item).count() == 0:
    items = [
        Item(name="Laptop", description="High performance laptop", price=999.99, category="electronics"),
        Item(name="Phone", description="Latest smartphone", price=699.99, category="electronics"),
        Item(name="Headphones", description="Noise cancelling", price=199.99, category="electronics"),
        Item(name="Monitor", description="4K display", price=449.99, category="electronics"),
        Item(name="Keyboard", description="Mechanical keyboard", price=89.99, category="accessories"),
        Item(name="Mouse", description="Wireless mouse", price=49.99, category="accessories"),
        Item(name="Desk", description="Standing desk", price=399.99, category="furniture"),
        Item(name="Chair", description="Ergonomic chair", price=299.99, category="furniture"),
        Item(name="Webcam", description="HD webcam", price=79.99, category="electronics"),
        Item(name="Microphone", description="USB microphone", price=129.99, category="accessories"),
        Item(name="Lamp", description="LED desk lamp", price=39.99, category="furniture"),
        Item(name="Notebook", description="A5 notebook", price=9.99, category="accessories"),
    ]
    db.add_all(items)
    db.commit()
db.close()

@app.get("/items")
def get_items(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=5, ge=1, le=20),
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    db = SessionLocal()
    query = db.query(Item)

    # Filtering
    if category:
        query = query.filter(Item.category == category)
    if min_price:
        query = query.filter(Item.price >= min_price)
    if max_price:
        query = query.filter(Item.price <= max_price)

    total = query.count()
    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()
    db.close()

    return {
        "metadata": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": -(-total // limit)
        },
        "data": [
            {
                "id": item.id,
                "name": item.name,
                "price": float(item.price),
                "category": item.category
            }
            for item in items
        ]
    }