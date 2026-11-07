import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def check_discount(product_id):
    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host = os.getenv("DB_HOST"),
            port = int(os.getenv('DB_PORT')),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            database = os.getenv('DB_NAME')
        )

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, name, price, discount_percent FROM products
            WHERE id = %s
            """,
            (product_id,)
        )


        product = cursor.fetchone()

        if product is None:
            return {"error" : 'Product Not Found'}

        discount = product["discount_percent"]
        original_price = float(product["price"])

        discounted_price = original_price - (
            original_price * float(discount) / 100
        )

        return {
            "product_name" : product["name"],
            "original_price" : original_price,
            "discount_percent" : float(discount),
            "discounted_price" : round(discounted_price, 2),
            "discount_available" : discount > 0
        }

    except mysql.connector.Error as e:
        print("Database error", e)
        raise

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

if __name__ == "__main__":
    result = check_discount(1)
    print('Discount Result : ', result)