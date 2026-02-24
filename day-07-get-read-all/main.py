from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, Text, Numeric, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

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

# Seed data on startup
db = SessionLocal()
if db.query(Item).count() == 0:
    items = [
        Item(name="Laptop", description="High performance laptop", price=999.99),
        Item(name="Phone", description="Latest smartphone", price=699.99),
        Item(name="Headphones", description="Noise cancelling headphones", price=199.99),
        Item(name="Monitor", description="4K display monitor", price=449.99),
        Item(name="Keyboard", description="Mechanical keyboard", price=89.99),
    ]
    db.add_all(items)
    db.commit()
db.close()

@app.get("/items")
def get_all_items():
    db = SessionLocal()
    items = db.query(Item).all()
    db.close()
    return {
        "status": "success",
        "count": len(items),
        "data": [
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "price": float(item.price),
                "created_at": str(item.created_at)
            }
            for item in items
        ]
    }