import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


def update_cart(product_id, quantity, session_id):

    if quantity <= 0:
        return {"error": "Quantity must be greater than zero"}

    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT stock, name FROM products WHERE id = %s",
            (product_id,)
        )
        product = cursor.fetchone()

        if product is None:
            return {"error": "Product not found"}

        if quantity > product["stock"]:
            return {
                "error": "Insufficient stock",
                "available_stock": product["stock"]
            }

        cursor.execute(
            "SELECT id FROM cart_items WHERE product_id = %s AND session_id = %s ORDER BY id",
            (product_id, session_id)
        )

        cart_items = cursor.fetchall()

        if not cart_items:
            return {"error": "Product not found in cart"}

        first_id = cart_items[0]["id"]

        cursor.execute(
            "UPDATE cart_items SET quantity = %s WHERE id = %s",
            (quantity, first_id)
        )

        for item in cart_items[1:]:
            cursor.execute(
                "DELETE FROM cart_items WHERE id = %s",
                (item["id"],)
            )

        connection.commit()

        return {
            "success": True,
            "message": "Cart updated successfully",
            "product_name": product["name"],
            "quantity": quantity
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()