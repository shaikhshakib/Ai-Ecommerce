print("Python file started")
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

if __name__ == "__main__":
    print("Main block started")

result = search_products("Pendant", 800)

print("Database Result:", result)