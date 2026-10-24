from fastapi import FastAPI

app = FastAPI()

products = [
    {"id":1, "name": "Golden Full Heart Pendent", "category":"Pendant", "price":249},
    {"id":2,"name": "Simple Bracelet", "category": "Bracelet", "price": 259},
    {"id":3, "name": "Serpent Watch", "category": "Watch", "price": 500},
    {"id":4, "name": "Chunky Rings", "category": "Rings", "price": 179}

]


@app.get("/")
def home():
    return {"messasge": "Welcome To Celeste Rose Ai"}

@app.get("/products")
def get_products():
    return products

@app.get("/products/filter")
def filter_products(max_price: int):
    return [p for p in products if p["price"] <= max_price]

@app.get("/products/category")
def get_products_by_category(category : str):
    return [p for p in products if p["category"].lower()== category.lower()]

@app.get("/products/search")
def search_products(category : str, max_price : int):
    return [p for p in products if p["category"].lower()== category.lower() and p["price"] <= max_price]

