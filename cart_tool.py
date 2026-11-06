import mysql.connector 
import os
from dotenv import load_dotenv

load_dotenv()

def add_to_cart(product_id, quantity):
    if quantity <= 0:
        return {"error": "Quantity Must Be Greater Than Zero"}

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

        if product_id is None:
            return {"error": "Product Not Found"}

        if product["stock"] < quantity:
            return {
                "error" : "Insufficient Quantity",
                "available_stock" : product["stock"]
            }

        cursor.execute(
            "INSERT INTO cart_items (product_id, quantity) VALUES (%s, %s)",
            (product_id, quantity)
        )

        connection.commit()

        return {
            "success" : True,
            "message" : "Product Added Successfully",
            "product_name" : product["name"],
            "quantity" : quantity
        }

    except mysql.connector.Error as e:
        if connection is not None:
            connection.rollback()

        print("Database Error", e)
        raise
    finally:
        if cursor is not None:
            cursor.close()

if __name__ == "__main__":

    result = add_to_cart(1, 2)

    print("Cart Result:", result)