import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


def search_products(category, max_price=None, color=None, limit=5, style_type = None):

    category_map = {
    "pendants": "Pendant",
    "pendant": "Pendant",

    "bracelets": "Bracelet",
    "bracelet": "Bracelet",

    "rings": "Ring",
    "ring": "Ring",

    "earrings": "Earrings",
    "earring": "Earrings",

    "bangles": "Bangles",
    "bangle": "Bangles"
}

    category = category_map.get(category.lower(), category)

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

        query = """
    SELECT id, name, category, price, stock, color,
           style_type, occasion, outfit_compatibility
    FROM products
    WHERE LOWER(category) = LOWER(%s)
"""
   
        params = [category]

        if max_price is not None:
            query += " AND price <= %s"
            params.append(max_price)

        if color:
            query += " AND LOWER(color) LIKE LOWER(%s)"
            params.append(f"%{color}%")
        if style_type:
            query += " AND LOWER(style_type) = LOWER(%s)"
            params.append(style_type)
        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)
        cursor.execute(query, tuple(params))

        products = cursor.fetchall()

        for product in products:
            product["price"] = float(product["price"])

        return products

    except mysql.connector.Error as e:
        print("Database Error:", e)
        raise

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

def search_products_by_name(product_name, color=None):

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
            """
    SELECT id, sku, name, category, color, price, stock
    FROM products
    WHERE LOWER(name) LIKE LOWER(%s)
    AND (%s IS NULL OR LOWER(color) = LOWER(%s))
    """,
    (f"%{product_name}%", color, color)
)
        products = cursor.fetchall()

        return products
    except mysql.connector.Error as e:
        print("Database Error", e)
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def get_product_details(product_name):

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
            """
            SELECT id, sku, name, category, color, price,
                   stock, discount_percent, description, image_url, style_type
            FROM products
            WHERE LOWER(name) = LOWER(%s)
            """,
            (product_name,)
        )

        product = cursor.fetchone()

        return product

    except mysql.connector.Error as e:
        print("Database Error:", e)
        raise

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()
def get_personalized_recommendations(user_id, limit=5):

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

        # Find customer's most purchased category and style
        cursor.execute("""
            SELECT
                p.category,
                p.style_type,
                SUM(oi.quantity) AS purchased_quantity
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN products p ON oi.product_id = p.id
            WHERE o.user_id = %s
            GROUP BY p.category, p.style_type
            ORDER BY purchased_quantity DESC
            LIMIT 1
        """, (user_id,))

        preference = cursor.fetchone()

        if not preference:
            return []

        # Recommend similar products not purchased before
        cursor.execute("""
            SELECT
                id, name, category, price, stock,
                color, style_type
            FROM products
            WHERE LOWER(category) = LOWER(%s)
              AND LOWER(style_type) = LOWER(%s)
              AND stock > 0
              AND id NOT IN (
                  SELECT oi.product_id
                  FROM orders o
                  JOIN order_items oi ON o.id = oi.order_id
                  WHERE o.user_id = %s
              )
            ORDER BY stock DESC
            LIMIT %s
        """, (
            preference["category"],
            preference["style_type"],
            user_id,
            limit
        ))

        recommendations = cursor.fetchall()

        for product in recommendations:
            product["price"] = float(product["price"])

        return recommendations

    except mysql.connector.Error as e:
        print("Personalized Recommendation Error:", e)
        raise

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()
if __name__ == "__main__":

    result = get_product_details("Tulip Bracelet")

    print("Product Details:", result)