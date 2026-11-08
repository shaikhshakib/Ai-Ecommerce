import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def view_cart(session_id):

    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            p.id AS product_id,
            p.name,
            p.category,
            p.price,
            SUM(ci.quantity) AS quantity,
            (p.price * SUM(ci.quantity)) AS subtotal
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.session_id = %s
        GROUP BY p.id, p.name, p.category, p.price
    """, (session_id,))

    items = cursor.fetchall()

    total = sum(float(item["subtotal"]) for item in items)

    for item in items:
        item["price"] = float(item["price"])
        item["subtotal"] = float(item["subtotal"])

    cursor.close()
    connection.close()

    return {
        "items": items,
        "total": total,
        "item_count": sum(item["quantity"] for item in items)
    }