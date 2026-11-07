import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_all_products():

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
        SELECT id,name,category, price, stock
        FROM products
        ORDER BY category,name
            """
        )

        products = cursor.fetchall()

        for product in products:
            product["price"] = float(product["price"])

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
    result = get_all_products()
    print("All Products:", result)