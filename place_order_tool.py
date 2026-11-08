import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


def place_order(session_id, customer_name, phone, address):

    connection = None
    cursor = None

    try:
        # Step 1: Connect to database
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Start database transaction
        connection.start_transaction()

        # Step 2: Fetch cart products
        # Combine duplicate products into one row
        cursor.execute("""
            SELECT
                ci.product_id,
                SUM(ci.quantity) AS quantity,
                p.name,
                p.price,
                p.stock
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.session_id = %s
            GROUP BY ci.product_id, p.name, p.price, p.stock
        """, (session_id,))

        cart_items = cursor.fetchall()

        # Step 3: Check whether cart is empty
        if not cart_items:
            connection.rollback()

            return {
                "success": False,
                "message": "Your cart is empty."
            }

        # Step 4: Lock product stock rows
        # Sort product IDs to reduce deadlock chances
        for item in sorted(cart_items, key=lambda x: x["product_id"]):

            cursor.execute(
                "SELECT id, stock FROM products WHERE id = %s FOR UPDATE",
                (item["product_id"],)
            )

            locked_product = cursor.fetchone()

            if locked_product is None:
                connection.rollback()

                return {
                    "success": False,
                    "message": "Product no longer exists."
                }

            # Get latest available stock
            item["stock"] = locked_product["stock"]

        # Step 5: Validate stock
        for item in cart_items:

            if item["quantity"] > item["stock"]:

                connection.rollback()

                return {
                    "success": False,
                    "message": f"Sorry, only {item['stock']} units of {item['name']} are available."
                }

        # Step 6: Calculate total amount
        total_amount = sum(
            item["price"] * item["quantity"]
            for item in cart_items
        )

        # Step 7: Create order record
        cursor.execute("""
            INSERT INTO orders (
                session_id,
                customer_name,
                phone,
                address,
                total_amount,
                order_status
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            session_id,
            customer_name,
            phone,
            address,
            total_amount,
            "Pending"
        ))

        # Get newly generated order ID
        order_id = cursor.lastrowid

        # Step 8: Insert products into order_items
        for item in cart_items:

            cursor.execute("""
                INSERT INTO order_items (
                    order_id,
                    product_id,
                    quantity,
                    price
                )
                VALUES (%s, %s, %s, %s)
            """, (
                order_id,
                item["product_id"],
                item["quantity"],
                item["price"]
            ))

        # Step 9: Deduct product stock
        for item in cart_items:

            cursor.execute("""
                UPDATE products
                SET stock = stock - %s
                WHERE id = %s AND stock >= %s
            """, (
                item["quantity"],
                item["product_id"],
                item["quantity"]
            ))

            # Check whether stock was successfully deducted
            if cursor.rowcount != 1:
                raise Exception(
                    f"Stock unavailable for {item['name']}"
                )

        # Step 10: Clear customer's cart
        cursor.execute("""
            DELETE FROM cart_items
            WHERE session_id = %s
        """, (session_id,))

        # Step 11: Commit transaction
        connection.commit()

        # Step 12: Return order confirmation
        return {
            "success": True,
            "message": "Order placed successfully!",
            "order_id": order_id,
            "customer_name": customer_name,
            "total_amount": float(total_amount)
        }

    except Exception as e:

        # Rollback all changes if any error occurs
        if connection is not None:
            connection.rollback()

        print("Order Error:", e)

        return {
            "success": False,
            "message": "Order could not be placed. Please try again."
        }

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()