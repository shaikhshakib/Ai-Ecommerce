import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


def remove_from_cart(product_id, session_id):

    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT p.name
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.product_id = %s AND ci.session_id = %s
        """, (product_id, session_id))

        product = cursor.fetchone()

        if product is None:
            return {"error": "Product not found in cart"}

        cursor.execute("""
            DELETE FROM cart_items
            WHERE product_id = %s AND session_id = %s
        """, (product_id, session_id))

        connection.commit()

        return {
            "success": True,
            "message": "Product removed from cart successfully",
            "product_name": product["name"]
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()