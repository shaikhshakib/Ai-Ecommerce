from fastapi import FastAPI
import mysql.connector
import os
from dotenv import load_dotenv

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

connection = get_db_connection()
print("MySQL Connected!")
connection.close()