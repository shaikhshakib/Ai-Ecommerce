import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def check_stock(product_id, requested_quantity=1):

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
            "SELECT id,name,stock FROM products WHERE id = %s",
            (product_id,)
        )

        product = cursor.fetchone()

        if product is None:
            return {"error": "Product Not Found"}

        return {
            "product_id": product["id"],
            "product_name": product["name"],
            "available_stock": product["stock"],
            "requested_quantity": requested_quantity,
            "in_stock": product["stock"] > 0,
            "enough_stock": product["stock"] >= requested_quantity
}
    except mysql.connector.Error as e:
        print("Database Error", e)
        raise

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

if __name__ == "__main__":
    result = check_stock(1)
    print("Stock Result", result)