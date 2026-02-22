from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Query parameter with validation
@app.get("/search")
def search(q: str = Query(min_length=1, description="Search term")):
    return {
        "query": q,
        "message": f"Searching for: {q}"
    }

# Query with optional filter
@app.get("/products")
def get_products(
    category: str = Query(default="all", description="Product category"),
    limit: int = Query(default=10, ge=1, le=100, description="Number of results")
):
    return {
        "category": category,
        "limit": limit,
        "message": f"Fetching {limit} products from category: {category}"
    }

# POST with Pydantic validation
class Item(BaseModel):
    name: str
    price: float
    quantity: int

@app.post("/items")
def create_item(item: Item):
    return {
        "message": "Item created successfully",
        "item": item
    }