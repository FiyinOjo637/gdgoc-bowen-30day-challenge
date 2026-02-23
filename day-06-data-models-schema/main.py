from sqlalchemy import create_engine, Column, Integer, String, Text, Numeric, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Database setup
engine = create_engine("sqlite:///items.db", echo=True)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# Item Model
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

db = SessionLocal()

items = [
    Item(name="Laptop", description="High performance laptop", price=999.99),
    Item(name="Phone", description="Latest smartphone", price=699.99),
    Item(name="Headphones", description="Noise cancelling headphones", price=199.99),
    Item(name="Monitor", description="4K display monitor", price=449.99),
    Item(name="Keyboard", description="Mechanical keyboard", price=89.99),
]

db.add_all(items)
db.commit()
print("5 items inserted successfully!")
db.close()