import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def search_products(category, max_price):
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

    cursor.close()
    connection.close()

    return products


if __name__ == "__main__":
    result = search_products("Pendant", 800)
    print(result)
