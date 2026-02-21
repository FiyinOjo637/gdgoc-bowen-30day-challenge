from fastapi import FastAPI

app = FastAPI()

@app.get("/user/{user_id}")
def get_user(user_id: int):
    return {
        "user_id": user_id,
        "message": f"Fetching user with ID {user_id}"
    }

@app.get("/product/{product_name}")
def get_product(product_name: str):
    return {
        "product": product_name,
        "message": f"Fetching product: {product_name}"
    }

@app.get("/user/{user_id}/order/{order_id}")
def get_user_order(user_id: int, order_id: int):
    return {
        "user_id": user_id,
        "order_id": order_id,
        "message": f"Order {order_id} for user {user_id}"
    }