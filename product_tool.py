import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


def search_products(category, max_price):

    category_map = {
        "pendants": "Pendant",
        "pendant": "Pendant",
        "bracelets": "Bracelet",
        "bracelet": "Bracelet",
        "watches": "Watch",
        "watch": "Watch",
        "rings": "Rings",
        "ring": "Rings"
    }

    category = category_map.get(category.lower(), category)

    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM products WHERE LOWER(category) = LOWER(%s) AND price <= %s",
            (category, max_price)
        )

        products = cursor.fetchall()

        return products

    except mysql.connector.Error as e:
        print("Database Error:", e)
        raise

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

def search_products_by_name(product_name):

    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host = os.getenv("DB_HOST"),
            port = int(os.getenv("DB_PORT")),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            database = os.getenv("DB_NAME")
        )

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT id,name,category,price,stock FROM products WHERE LOWER(name) LIKE LOWER(%s)",
            (f"%{product_name}%",)
        )
        products = cursor.fetchall()

        return products
    except mysql.connector.Error as e:
        print("Database Error", e)
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

if __name__ == "__main__":

    result = search_products_by_name("Golden")

    print("Search Result:", result)
    