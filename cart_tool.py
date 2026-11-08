import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


def add_to_cart(product_id, quantity,session_id, confirmed=False):

    # Step 1: Confirmation check
    if confirmed is not True:
        return {
            "success": False,
            "message": "Customer confirmation required"
        }

    # Step 2: Quantity validation
    if quantity <= 0:
        return {"error": "Quantity must be greater than zero"}

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
            "SELECT id, name, stock FROM products WHERE id = %s",
            (product_id,)
        )

        product = cursor.fetchone()

        # Step 3: Product validation
        if product is None:
            return {"error": "Product not found"}

        # Step 4: Stock validation
        if product["stock"] < quantity:
            return {
                "error": "Insufficient stock",
                "available_stock": product["stock"]
            }

        # Step 5: Add product to cart
        cursor.execute(
            "INSERT INTO cart_items (product_id, quantity, session_id) VALUES (%s, %s, %s)",
            (product_id, quantity, session_id)
        )

        connection.commit()

        return {
            "success": True,
            "message": "Product added successfully",
            "product_name": product["name"],
            "quantity": quantity
        }

    except mysql.connector.Error as e:
        if connection is not None:
            connection.rollback()

        print("Database Error:", e)
        raise

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


if __name__ == "__main__":

    result = add_to_cart(
        product_id=1,
        quantity=2,
        session_id="test-session",
        confirmed=False
    )

    print("Cart Result:", result)