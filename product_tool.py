import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


def search_products(category, max_price=None, color=None):

    category_map = {
    "pendants": "Pendant",
    "pendant": "Pendant",

    "bracelets": "Bracelet",
    "bracelet": "Bracelet",

    "rings": "Ring",
    "ring": "Ring",

    "earrings": "Earrings",
    "earring": "Earrings",

    "bangles": "Bangles",
    "bangle": "Bangles"
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

        query = """
    SELECT * FROM products
    WHERE LOWER(category) = LOWER(%s)
"""

        params = [category]

        if max_price is not None:
            query += " AND price <= %s"
            params.append(max_price)

        if color:
            query += " AND LOWER(color) LIKE LOWER(%s)"
            params.append(f"%{color}%")

        cursor.execute(query, tuple(params))

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
            "SELECT id,sku,name,category,color,price,stock FROM products WHERE LOWER(name) LIKE LOWER(%s)",
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

def get_product_details(product_name):

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
            """
            SELECT id, sku, name, category, color, price,
                   stock, discount_percent, description, image_url
            FROM products
            WHERE LOWER(name) = LOWER(%s)
            """,
            (product_name,)
        )

        product = cursor.fetchone()

        return product

    except mysql.connector.Error as e:
        print("Database Error:", e)
        raise

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

if __name__ == "__main__":

    result = get_product_details("Tulip Bracelet")

    print("Product Details:", result)