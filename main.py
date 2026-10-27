from fastapi import FastAPI
import mysql.connector
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/products")
def get_products():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return products


@app.get("/products/filter")
def filter_products(max_price: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products WHERE price <= %s", (max_price,))
    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return products

@app.get("/products/category")
def get_products_by_category(category: str):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM products WHERE LOWER(category) = LOWER(%s)",
        (category,)
    )
    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return products
@app.get("/products/search")
def search_products(category: str, max_price: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM products WHERE LOWER(category) = LOWER(%s) AND price <= %s",
        (category, max_price)
    )
    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return products

@app.get("/products/{product_id}")
def get_product(product_id: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()

    cursor.close()
    connection.close()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

@app.post("/products")
def add_product(name: str, category: str, price: float):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO products (name, category, price) VALUES (%s, %s, %s)",
        (name, category, price)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return {"message": "Product added successfully"}

@app.put("/products/{product_id}") 
def update_product(product_id: int, price: float): 
    connection = get_db_connection() 
    cursor = connection.cursor() 
    cursor.execute( "UPDATE products SET price = %s WHERE id = %s", (price, product_id) ) 
    connection.commit() 
    updated = cursor.rowcount 
    cursor.close() 
    connection.close() 
    return {"updated": updated}


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    connection.commit()

    deleted = cursor.rowcount

    cursor.close()
    connection.close()

    return {"deleted": deleted}

