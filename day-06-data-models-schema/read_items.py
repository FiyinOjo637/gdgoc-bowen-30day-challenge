from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from main import Item, SessionLocal

db = SessionLocal()
items = db.query(Item).all()

for item in items:
    print(f"ID: {item.id} | Name: {item.name} | Price: {item.price} | Created: {item.created_at}")

db.close()